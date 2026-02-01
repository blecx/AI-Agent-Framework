"""
Proposal service for managing proposal lifecycle.
Handles CRUD operations, apply, and reject logic.
"""

import json
import difflib
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from domain.proposals.models import Proposal, ProposalStatus, ChangeType
from services.git_manager import GitManager
from services.audit_service import AuditService


class ProposalService:
    """Service for managing proposal lifecycle with audit trail."""

    def __init__(self, git_manager: GitManager, audit_service: AuditService):
        """
        Initialize proposal service.

        Args:
            git_manager: Git manager for persistence
            audit_service: Audit service for event logging
        """
        self.git_manager = git_manager
        self.audit_service = audit_service

    def create_proposal(self, proposal: Proposal) -> Proposal:
        """
        Create a new proposal.

        Args:
            proposal: Proposal to create

        Returns:
            Created proposal with metadata

        Raises:
            ValueError: If proposal validation fails
        """
        # Ensure proposals directory exists
        proposals_path = (
            self.git_manager.get_project_path(proposal.project_key) / "proposals"
        )
        proposals_path.mkdir(parents=True, exist_ok=True)

        # Persist proposal to JSON
        proposal_file = proposals_path / f"{proposal.id}.json"
        proposal_data = proposal.model_dump(mode="json")
        proposal_file.write_text(json.dumps(proposal_data, indent=2))

        # Commit proposal
        relative_path = f"proposals/{proposal.id}.json"
        self.git_manager.commit_changes(
            project_key=proposal.project_key,
            message=f"Create proposal {proposal.id}",
            files=[relative_path],
        )

        # Log audit event
        self.audit_service.log_audit_event(
            project_key=proposal.project_key,
            event_type="proposal.created",
            actor=proposal.author,
            payload_summary={
                "proposal_id": proposal.id,
                "target_artifact": proposal.target_artifact,
                "change_type": proposal.change_type,
            },
            git_manager=self.git_manager,
        )

        return proposal

    def get_proposal(self, project_key: str, proposal_id: str) -> Optional[Proposal]:
        """
        Retrieve a proposal by ID.

        Args:
            project_key: Project key
            proposal_id: Proposal ID

        Returns:
            Proposal if found, None otherwise
        """
        proposal_file = (
            self.git_manager.get_project_path(project_key)
            / "proposals"
            / f"{proposal_id}.json"
        )

        if not proposal_file.exists():
            return None

        proposal_data = json.loads(proposal_file.read_text())
        return Proposal(**proposal_data)

    def list_proposals(
        self,
        project_key: str,
        status: Optional[ProposalStatus] = None,
        change_type: Optional[ChangeType] = None,
    ) -> List[Proposal]:
        """
        List proposals with optional filtering.

        Args:
            project_key: Project key
            status: Filter by status
            change_type: Filter by change type

        Returns:
            List of proposals matching filters
        """
        proposals_path = self.git_manager.get_project_path(project_key) / "proposals"

        if not proposals_path.exists():
            return []

        proposals = []
        for proposal_file in proposals_path.glob("*.json"):
            proposal_data = json.loads(proposal_file.read_text())
            proposal = Proposal(**proposal_data)

            # Apply filters
            if status and proposal.status != status:
                continue
            if change_type and proposal.change_type != change_type:
                continue

            proposals.append(proposal)

        # Sort by creation time (newest first)
        proposals.sort(key=lambda p: p.created_at, reverse=True)
        return proposals

    def apply_proposal(self, project_key: str, proposal_id: str) -> Dict[str, Any]:
        """
        Apply a proposal to its target artifact.

        This operation is atomic - all changes (artifact update, proposal status,
        audit event) are committed in a single transaction.

        Args:
            project_key: Project key
            proposal_id: Proposal ID

        Returns:
            Result dictionary with status and details

        Raises:
            ValueError: If proposal is invalid or cannot be applied
        """
        # Load proposal
        proposal = self.get_proposal(project_key, proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")

        if proposal.status != ProposalStatus.PENDING:
            raise ValueError(
                f"Proposal {proposal_id} is already {proposal.status.value}"
            )

        # Handle change type
        artifact_path = proposal.target_artifact
        files_to_commit = [f"proposals/{proposal_id}.json"]

        if proposal.change_type == ChangeType.CREATE:
            # Create new artifact
            self.git_manager.write_file(
                project_key=project_key,
                relative_path=artifact_path,
                content=proposal.diff,  # For CREATE, diff contains the full content
            )
            files_to_commit.append(artifact_path)

        elif proposal.change_type == ChangeType.UPDATE:
            # Read existing artifact
            old_content = self.git_manager.read_file(project_key, artifact_path)
            if old_content is None:
                raise ValueError(f"Target artifact {artifact_path} not found")

            # Apply diff
            new_content = self._apply_diff(old_content, proposal.diff)
            self.git_manager.write_file(
                project_key=project_key,
                relative_path=artifact_path,
                content=new_content,
            )
            files_to_commit.append(artifact_path)

        elif proposal.change_type == ChangeType.DELETE:
            # Mark artifact for deletion
            full_path = self.git_manager.get_project_path(project_key) / artifact_path
            if full_path.exists():
                full_path.unlink()
                files_to_commit.append(artifact_path)

        # Update proposal status
        proposal.status = ProposalStatus.ACCEPTED
        proposal.applied_at = datetime.now(timezone.utc)
        proposal_file = (
            self.git_manager.get_project_path(project_key)
            / "proposals"
            / f"{proposal_id}.json"
        )
        proposal_data = proposal.model_dump(mode="json")
        proposal_file.write_text(json.dumps(proposal_data, indent=2))

        # Commit all changes atomically
        self.git_manager.commit_changes(
            project_key=project_key,
            message=f"Apply proposal {proposal_id}: {proposal.rationale}",
            files=files_to_commit,
        )

        # Log audit event
        self.audit_service.log_audit_event(
            project_key=project_key,
            event_type="proposal.accepted",
            actor="system",
            payload_summary={
                "proposal_id": proposal_id,
                "target_artifact": artifact_path,
                "change_type": proposal.change_type,
            },
            git_manager=self.git_manager,
        )

        return {
            "status": "success",
            "proposal_id": proposal_id,
            "artifact": artifact_path,
            "change_type": proposal.change_type.value,
        }

    def reject_proposal(
        self, project_key: str, proposal_id: str, reason: str
    ) -> Dict[str, Any]:
        """
        Reject a proposal with a reason.

        Args:
            project_key: Project key
            proposal_id: Proposal ID
            reason: Rejection reason

        Returns:
            Result dictionary with status

        Raises:
            ValueError: If proposal is invalid or already processed
        """
        # Load proposal
        proposal = self.get_proposal(project_key, proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")

        if proposal.status != ProposalStatus.PENDING:
            raise ValueError(
                f"Proposal {proposal_id} is already {proposal.status.value}"
            )

        # Update proposal status
        proposal.status = ProposalStatus.REJECTED
        proposal_file = (
            self.git_manager.get_project_path(project_key)
            / "proposals"
            / f"{proposal_id}.json"
        )
        proposal_data = proposal.model_dump(mode="json")
        # Store rejection reason in the proposal data
        proposal_data["rejection_reason"] = reason
        proposal_file.write_text(json.dumps(proposal_data, indent=2))

        # Commit change
        self.git_manager.commit_changes(
            project_key=project_key,
            message=f"Reject proposal {proposal_id}: {reason}",
            files=[f"proposals/{proposal_id}.json"],
        )

        # Log audit event
        self.audit_service.log_audit_event(
            project_key=project_key,
            event_type="proposal.rejected",
            actor="system",
            payload_summary={
                "proposal_id": proposal_id,
                "reason": reason,
            },
            git_manager=self.git_manager,
        )

        return {
            "status": "rejected",
            "proposal_id": proposal_id,
            "reason": reason,
        }

    def _generate_diff(self, old_content: str, new_content: str) -> str:
        """
        Generate unified diff between two content versions.

        Args:
            old_content: Original content
            new_content: Modified content

        Returns:
            Unified diff string
        """
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            lineterm="",
        )
        return "".join(diff)

    def _apply_diff(self, old_content: str, diff_str: str) -> str:
        """
        Apply a unified diff to content.

        Args:
            old_content: Original content
            diff_str: Unified diff string

        Returns:
            New content after applying diff

        Raises:
            ValueError: If diff cannot be applied
        """
        # For simplicity, we parse the diff and reconstruct content
        # A production implementation might use patch libraries
        old_lines = old_content.splitlines(keepends=True)
        diff_lines = diff_str.splitlines()

        new_lines = []
        old_idx = 0
        i = 0

        while i < len(diff_lines):
            line = diff_lines[i]

            # Skip diff headers
            if line.startswith("---") or line.startswith("+++"):
                i += 1
                continue

            # Parse hunk header
            if line.startswith("@@"):
                # Extract old start line from @@ -start,count +start,count @@
                parts = line.split()
                if len(parts) >= 2:
                    old_part = parts[1]  # -start,count
                    old_start = (
                        int(old_part.split(",")[0][1:]) - 1
                    )  # Convert to 0-indexed

                    # Copy unchanged lines before this hunk
                    while old_idx < old_start:
                        new_lines.append(old_lines[old_idx])
                        old_idx += 1

                i += 1
                continue

            # Process diff lines
            if line.startswith(" "):  # Context line
                new_lines.append(old_lines[old_idx])
                old_idx += 1
            elif line.startswith("-"):  # Removed line
                old_idx += 1
            elif line.startswith("+"):  # Added line
                new_lines.append(line[1:] + "\n")

            i += 1

        # Append remaining unchanged lines
        while old_idx < len(old_lines):
            new_lines.append(old_lines[old_idx])
            old_idx += 1

        return "".join(new_lines)
