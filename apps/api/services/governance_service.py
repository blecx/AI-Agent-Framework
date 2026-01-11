"""
Governance service for managing project governance metadata and decision logs.
Aligned with ISO 21500/21502 standards.
"""

import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class GovernanceService:
    """Service for handling governance metadata and decision logs."""

    def __init__(self):
        """Initialize governance service."""
        pass

    # ========================================================================
    # Governance Metadata Operations
    # ========================================================================

    def get_governance_metadata(
        self, project_key: str, git_manager
    ) -> Optional[Dict[str, Any]]:
        """Get governance metadata for a project."""
        content = git_manager.read_file(project_key, "governance/metadata.json")
        if content is None:
            return None
        return json.loads(content)

    def create_governance_metadata(
        self, project_key: str, metadata: Dict[str, Any], git_manager
    ) -> Dict[str, Any]:
        """Create governance metadata for a project."""
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        governance_data = {
            "objectives": metadata.get("objectives", []),
            "scope": metadata.get("scope", ""),
            "stakeholders": metadata.get("stakeholders", []),
            "decision_rights": metadata.get("decision_rights", {}),
            "stage_gates": metadata.get("stage_gates", []),
            "approvals": metadata.get("approvals", []),
            "created_at": now,
            "updated_at": now,
            "created_by": metadata.get("created_by", "system"),
            "updated_by": metadata.get("created_by", "system"),
        }

        # Write to governance directory
        content = json.dumps(governance_data, indent=2)
        git_manager.write_file(project_key, "governance/metadata.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Create governance metadata",
            ["governance/metadata.json"],
        )

        # Log event
        git_manager.log_event(
            project_key,
            {
                "event_type": "governance_metadata_created",
                "project_key": project_key,
                "created_by": metadata.get("created_by", "system"),
            },
        )

        return governance_data

    def update_governance_metadata(
        self, project_key: str, updates: Dict[str, Any], git_manager
    ) -> Dict[str, Any]:
        """Update governance metadata for a project."""
        # Get existing metadata
        existing = self.get_governance_metadata(project_key, git_manager)
        if existing is None:
            raise ValueError(f"Governance metadata not found for project {project_key}")

        # Update fields
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        for key, value in updates.items():
            if key not in ["created_at", "created_by"] and value is not None:
                existing[key] = value

        existing["updated_at"] = now
        if "updated_by" in updates:
            existing["updated_by"] = updates["updated_by"]

        # Write updated metadata
        content = json.dumps(existing, indent=2)
        git_manager.write_file(project_key, "governance/metadata.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Update governance metadata",
            ["governance/metadata.json"],
        )

        # Log event
        git_manager.log_event(
            project_key,
            {
                "event_type": "governance_metadata_updated",
                "project_key": project_key,
                "updated_by": existing["updated_by"],
            },
        )

        return existing

    # ========================================================================
    # Decision Log Operations
    # ========================================================================

    def get_decisions(self, project_key: str, git_manager) -> List[Dict[str, Any]]:
        """Get all decision log entries for a project."""
        content = git_manager.read_file(project_key, "governance/decisions.json")
        if content is None:
            return []

        data = json.loads(content)
        return data.get("decisions", [])

    def get_decision(
        self, project_key: str, decision_id: str, git_manager
    ) -> Optional[Dict[str, Any]]:
        """Get a specific decision by ID."""
        decisions = self.get_decisions(project_key, git_manager)
        for decision in decisions:
            if decision["id"] == decision_id:
                return decision
        return None

    def create_decision(
        self, project_key: str, decision_data: Dict[str, Any], git_manager
    ) -> Dict[str, Any]:
        """Create a new decision log entry."""
        decisions = self.get_decisions(project_key, git_manager)

        # Generate unique ID
        decision_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        decision = {
            "id": decision_id,
            "title": decision_data["title"],
            "description": decision_data["description"],
            "decision_date": now,
            "decision_maker": decision_data["decision_maker"],
            "rationale": decision_data.get("rationale", ""),
            "impact": decision_data.get("impact", ""),
            "status": decision_data.get("status", "approved"),
            "linked_raid_ids": decision_data.get("linked_raid_ids", []),
            "linked_change_requests": decision_data.get("linked_change_requests", []),
            "created_at": now,
            "created_by": decision_data.get("created_by", "system"),
        }

        decisions.append(decision)

        # Write decisions
        content = json.dumps({"decisions": decisions}, indent=2)
        git_manager.write_file(project_key, "governance/decisions.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Add decision: {decision['title']}",
            ["governance/decisions.json"],
        )

        # Log event
        git_manager.log_event(
            project_key,
            {
                "event_type": "decision_created",
                "project_key": project_key,
                "decision_id": decision_id,
                "created_by": decision["created_by"],
            },
        )

        return decision

    def link_decision_to_raid(
        self, project_key: str, decision_id: str, raid_id: str, git_manager
    ) -> bool:
        """Link a decision to a RAID item."""
        decisions = self.get_decisions(project_key, git_manager)

        updated = False
        for decision in decisions:
            if decision["id"] == decision_id:
                if raid_id not in decision["linked_raid_ids"]:
                    decision["linked_raid_ids"].append(raid_id)
                    updated = True
                break

        if not updated:
            return False

        # Write updated decisions
        content = json.dumps({"decisions": decisions}, indent=2)
        git_manager.write_file(project_key, "governance/decisions.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Link decision {decision_id} to RAID {raid_id}",
            ["governance/decisions.json"],
        )

        return True
