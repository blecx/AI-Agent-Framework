"""
Integration tests for ProposalService.

Tests full proposal lifecycle with real GitManager and temporary file system.
"""

import pytest
import json
import tempfile
import shutil
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../apps/api"))

from apps.api.domain.proposals.models import (  # noqa: E402
    Proposal,
    ProposalStatus,
    ChangeType,
)
from apps.api.services.proposal_service import ProposalService  # noqa: E402
from apps.api.services.git_manager import GitManager  # noqa: E402
from apps.api.services.audit_service import AuditService  # noqa: E402


@pytest.fixture
def temp_project_docs():
    """Create temporary projectDocs directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def git_manager(temp_project_docs):
    """Create GitManager with temporary storage."""
    manager = GitManager(base_path=temp_project_docs)
    manager.ensure_repository()
    return manager


@pytest.fixture
def audit_service():
    """Create AuditService instance."""
    return AuditService()


@pytest.fixture
def proposal_service(git_manager, audit_service):
    """Create ProposalService instance."""
    return ProposalService(git_manager=git_manager, audit_service=audit_service)


@pytest.fixture
def project_key():
    """Test project key."""
    return "TEST-001"


@pytest.fixture
def sample_create_proposal(project_key):
    """Sample proposal for creating a new artifact."""
    return Proposal(
        id="prop-create-001",
        project_key=project_key,
        target_artifact="artifacts/new-doc.md",
        change_type=ChangeType.CREATE,
        diff="# New Document\n\nThis is new content.",
        rationale="Creating new requirements document",
        author="test-user",
    )


@pytest.fixture
def sample_update_proposal(project_key):
    """Sample proposal for updating an artifact."""
    return Proposal(
        id="prop-update-001",
        project_key=project_key,
        target_artifact="artifacts/existing-doc.md",
        change_type=ChangeType.UPDATE,
        diff="--- a/existing-doc.md\n+++ b/existing-doc.md\n@@ -1,1 +1,1 @@\n-Old content\n+New content\n",
        rationale="Updated content based on feedback",
        author="test-user",
    )


class TestProposalServiceCreate:
    """Test proposal creation."""

    def test_create_proposal_success(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test successful proposal creation."""
        # Create project first
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create proposal
        result = proposal_service.create_proposal(sample_create_proposal)

        assert result.id == "prop-create-001"
        assert result.project_key == project_key
        assert result.status == ProposalStatus.PENDING
        assert result.change_type == ChangeType.CREATE

    def test_create_proposal_persists_to_storage(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test proposal is persisted to proposals/ directory."""
        # Create project first
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create proposal
        proposal_service.create_proposal(sample_create_proposal)

        # Verify file exists
        proposal_path = (
            git_manager.get_project_path(project_key)
            / "proposals"
            / f"{sample_create_proposal.id}.json"
        )
        assert proposal_path.exists()

        # Verify content
        content = json.loads(proposal_path.read_text())
        assert content["id"] == sample_create_proposal.id
        assert content["status"] == "pending"
        assert content["change_type"] == "create"

    def test_create_proposal_logs_audit_event(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test audit event is logged on proposal creation."""
        # Create project first
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create proposal
        proposal_service.create_proposal(sample_create_proposal)

        # Verify audit event
        events_path = (
            git_manager.get_project_path(project_key) / "events" / "audit.ndjson"
        )
        assert events_path.exists()

        events = events_path.read_text().strip().split("\n")
        # Last event should be proposal.created
        last_event = json.loads(events[-1])
        assert last_event["event_type"] == "proposal.created"
        assert last_event["payload_summary"]["proposal_id"] == sample_create_proposal.id


class TestProposalServiceGet:
    """Test proposal retrieval."""

    def test_get_proposal_success(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test successful proposal retrieval."""
        # Create project and proposal
        git_manager.create_project(project_key, {"name": "Test Project"})
        proposal_service.create_proposal(sample_create_proposal)

        # Retrieve proposal
        result = proposal_service.get_proposal(project_key, sample_create_proposal.id)

        assert result is not None
        assert result.id == sample_create_proposal.id
        assert result.status == ProposalStatus.PENDING

    def test_get_proposal_not_found(self, proposal_service, git_manager, project_key):
        """Test retrieval of non-existent proposal."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Try to get non-existent proposal
        result = proposal_service.get_proposal(project_key, "prop-nonexistent")

        assert result is None


class TestProposalServiceList:
    """Test proposal listing."""

    def test_list_proposals_empty(self, proposal_service, git_manager, project_key):
        """Test listing proposals when none exist."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        result = proposal_service.list_proposals(project_key)

        assert result == []

    def test_list_proposals_multiple(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test listing multiple proposals."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create multiple proposals
        proposal1 = sample_create_proposal
        proposal2 = Proposal(
            id="prop-create-002",
            project_key=project_key,
            target_artifact="artifacts/doc2.md",
            change_type=ChangeType.CREATE,
            diff="# Doc 2",
            rationale="Second doc",
            author="user2",
        )

        proposal_service.create_proposal(proposal1)
        proposal_service.create_proposal(proposal2)

        # List all proposals
        result = proposal_service.list_proposals(project_key)

        assert len(result) == 2
        # Should be sorted by creation time (newest first)
        assert result[0].id == "prop-create-002"
        assert result[1].id == "prop-create-001"

    def test_list_proposals_filter_by_status(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test filtering proposals by status."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create proposal
        proposal_service.create_proposal(sample_create_proposal)

        # List only pending proposals
        result = proposal_service.list_proposals(
            project_key, status=ProposalStatus.PENDING
        )

        assert len(result) == 1
        assert result[0].status == ProposalStatus.PENDING


class TestProposalServiceApply:
    """Test applying proposals."""

    def test_apply_create_proposal_success(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test successfully applying a CREATE proposal."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create proposal
        proposal_service.create_proposal(sample_create_proposal)

        # Apply proposal
        result = proposal_service.apply_proposal(project_key, sample_create_proposal.id)

        assert result["status"] == "success"
        assert result["proposal_id"] == sample_create_proposal.id
        assert result["change_type"] == "create"

        # Verify artifact was created
        artifact_content = git_manager.read_file(
            project_key, sample_create_proposal.target_artifact
        )
        assert artifact_content == "# New Document\n\nThis is new content."

        # Verify proposal status updated
        proposal = proposal_service.get_proposal(project_key, sample_create_proposal.id)
        assert proposal.status == ProposalStatus.ACCEPTED
        assert proposal.applied_at is not None

    def test_apply_update_proposal_success(
        self, proposal_service, sample_update_proposal, git_manager, project_key
    ):
        """Test successfully applying an UPDATE proposal."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create existing artifact
        git_manager.write_file(
            project_key, sample_update_proposal.target_artifact, "Old content\n"
        )
        git_manager.commit_changes(
            project_key,
            "Create initial artifact",
            [sample_update_proposal.target_artifact],
        )

        # Create and apply proposal
        proposal_service.create_proposal(sample_update_proposal)
        result = proposal_service.apply_proposal(project_key, sample_update_proposal.id)

        assert result["status"] == "success"

        # Verify artifact was updated
        artifact_content = git_manager.read_file(
            project_key, sample_update_proposal.target_artifact
        )
        assert "New content" in artifact_content

    def test_apply_delete_proposal_success(
        self, proposal_service, git_manager, project_key
    ):
        """Test successfully applying a DELETE proposal."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create artifact to delete
        artifact_path = "artifacts/to-delete.md"
        git_manager.write_file(project_key, artifact_path, "Content to delete")
        git_manager.commit_changes(project_key, "Create artifact", [artifact_path])

        # Create DELETE proposal
        delete_proposal = Proposal(
            id="prop-delete-001",
            project_key=project_key,
            target_artifact=artifact_path,
            change_type=ChangeType.DELETE,
            diff="",
            rationale="No longer needed",
            author="test-user",
        )
        proposal_service.create_proposal(delete_proposal)

        # Apply proposal
        result = proposal_service.apply_proposal(project_key, delete_proposal.id)

        assert result["status"] == "success"

        # Verify artifact was deleted
        artifact_content = git_manager.read_file(project_key, artifact_path)
        assert artifact_content is None

    def test_apply_proposal_not_found(self, proposal_service, git_manager, project_key):
        """Test applying non-existent proposal raises error."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        with pytest.raises(ValueError, match="Proposal .* not found"):
            proposal_service.apply_proposal(project_key, "prop-nonexistent")

    def test_apply_proposal_already_applied(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test applying already-applied proposal raises error."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create and apply proposal
        proposal_service.create_proposal(sample_create_proposal)
        proposal_service.apply_proposal(project_key, sample_create_proposal.id)

        # Try to apply again
        with pytest.raises(ValueError, match="already accepted"):
            proposal_service.apply_proposal(project_key, sample_create_proposal.id)

    def test_apply_update_proposal_missing_artifact(
        self, proposal_service, sample_update_proposal, git_manager, project_key
    ):
        """Test applying UPDATE proposal when artifact doesn't exist."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create proposal for non-existent artifact
        proposal_service.create_proposal(sample_update_proposal)

        with pytest.raises(ValueError, match="Target artifact .* not found"):
            proposal_service.apply_proposal(project_key, sample_update_proposal.id)

    def test_apply_proposal_logs_audit_event(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test audit event is logged when proposal is applied."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create and apply proposal
        proposal_service.create_proposal(sample_create_proposal)
        proposal_service.apply_proposal(project_key, sample_create_proposal.id)

        # Verify audit event
        events_path = (
            git_manager.get_project_path(project_key) / "events" / "audit.ndjson"
        )
        events = events_path.read_text().strip().split("\n")

        # Last event should be proposal.accepted
        last_event = json.loads(events[-1])
        assert last_event["event_type"] == "proposal.accepted"
        assert last_event["payload_summary"]["proposal_id"] == sample_create_proposal.id


class TestProposalServiceReject:
    """Test rejecting proposals."""

    def test_reject_proposal_success(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test successfully rejecting a proposal."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create proposal
        proposal_service.create_proposal(sample_create_proposal)

        # Reject proposal
        result = proposal_service.reject_proposal(
            project_key, sample_create_proposal.id, "Not aligned with project goals"
        )

        assert result["status"] == "rejected"
        assert result["proposal_id"] == sample_create_proposal.id
        assert result["reason"] == "Not aligned with project goals"

        # Verify proposal status updated
        proposal = proposal_service.get_proposal(project_key, sample_create_proposal.id)
        assert proposal.status == ProposalStatus.REJECTED

    def test_reject_proposal_not_found(
        self, proposal_service, git_manager, project_key
    ):
        """Test rejecting non-existent proposal raises error."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        with pytest.raises(ValueError, match="Proposal .* not found"):
            proposal_service.reject_proposal(project_key, "prop-nonexistent", "reason")

    def test_reject_proposal_already_accepted(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test rejecting already-accepted proposal raises error."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create and apply proposal
        proposal_service.create_proposal(sample_create_proposal)
        proposal_service.apply_proposal(project_key, sample_create_proposal.id)

        # Try to reject
        with pytest.raises(ValueError, match="already accepted"):
            proposal_service.reject_proposal(
                project_key, sample_create_proposal.id, "reason"
            )

    def test_reject_proposal_logs_audit_event(
        self, proposal_service, sample_create_proposal, git_manager, project_key
    ):
        """Test audit event is logged when proposal is rejected."""
        # Create project
        git_manager.create_project(project_key, {"name": "Test Project"})

        # Create and reject proposal
        proposal_service.create_proposal(sample_create_proposal)
        proposal_service.reject_proposal(
            project_key, sample_create_proposal.id, "Not needed"
        )

        # Verify audit event
        events_path = (
            git_manager.get_project_path(project_key) / "events" / "audit.ndjson"
        )
        events = events_path.read_text().strip().split("\n")

        # Last event should be proposal.rejected
        last_event = json.loads(events[-1])
        assert last_event["event_type"] == "proposal.rejected"
        assert last_event["payload_summary"]["proposal_id"] == sample_create_proposal.id
        assert last_event["payload_summary"]["reason"] == "Not needed"


class TestProposalServiceDiffHelpers:
    """Test diff generation and application helpers."""

    def test_generate_diff(self, proposal_service):
        """Test unified diff generation."""
        old_content = "Line 1\nLine 2\nLine 3\n"
        new_content = "Line 1\nLine 2 modified\nLine 3\n"

        diff = proposal_service._generate_diff(old_content, new_content)

        assert "Line 2" in diff
        assert "Line 2 modified" in diff
        assert "-Line 2" in diff or "- Line 2" in diff
        assert "+Line 2 modified" in diff or "+ Line 2 modified" in diff

    def test_apply_diff_simple(self, proposal_service):
        """Test applying a simple diff."""
        old_content = "Line 1\nLine 2\nLine 3\n"
        diff = "--- a/file.txt\n+++ b/file.txt\n@@ -1,3 +1,3 @@\n Line 1\n-Line 2\n+Line 2 modified\n Line 3\n"

        new_content = proposal_service._apply_diff(old_content, diff)

        assert "Line 1" in new_content
        assert "Line 2 modified" in new_content
        assert "Line 3" in new_content
        assert "Line 2\n" not in new_content
