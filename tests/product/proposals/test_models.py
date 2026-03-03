"""Unit tests for Proposal domain models."""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from apps.api.domain.proposals.models import (
    Proposal,
    ProposalStatus,
    ChangeType,
)


class TestProposalStatus:
    """Test ProposalStatus enum."""

    def test_enum_values(self):
        """Test all enum values are defined."""
        assert ProposalStatus.PENDING == "pending"
        assert ProposalStatus.ACCEPTED == "accepted"
        assert ProposalStatus.REJECTED == "rejected"

    def test_enum_members(self):
        """Test enum has exactly 3 members."""
        assert len(ProposalStatus) == 3


class TestChangeType:
    """Test ChangeType enum."""

    def test_enum_values(self):
        """Test all enum values are defined."""
        assert ChangeType.CREATE == "create"
        assert ChangeType.UPDATE == "update"
        assert ChangeType.DELETE == "delete"

    def test_enum_members(self):
        """Test enum has exactly 3 members."""
        assert len(ChangeType) == 3


class TestProposal:
    """Test Proposal domain model."""

    def test_create_minimal_proposal(self):
        """Test creating proposal with required fields only."""
        proposal = Proposal(
            id="prop-123",
            project_key="PRJ-001",
            target_artifact="artifacts/requirements.md",
            change_type=ChangeType.UPDATE,
            diff="--- a/file\n+++ b/file\n@@ -1 +1 @@\n-old\n+new",
            rationale="Test change",
        )

        assert proposal.id == "prop-123"
        assert proposal.project_key == "PRJ-001"
        assert proposal.target_artifact == "artifacts/requirements.md"
        assert proposal.change_type == ChangeType.UPDATE
        assert proposal.status == ProposalStatus.PENDING
        assert proposal.author == "system"
        assert isinstance(proposal.created_at, datetime)
        assert proposal.applied_at is None

    def test_create_full_proposal(self):
        """Test creating proposal with all fields."""
        created = datetime(2026, 2, 1, 10, 0, 0)
        applied = datetime(2026, 2, 1, 11, 0, 0)

        proposal = Proposal(
            id="prop-456",
            project_key="PRJ-002",
            target_artifact="artifacts/design.md",
            change_type=ChangeType.CREATE,
            diff="--- /dev/null\n+++ b/design.md\n@@ -0,0 +1 @@\n+new file",
            rationale="Create design document",
            status=ProposalStatus.ACCEPTED,
            author="user123",
            created_at=created,
            applied_at=applied,
        )

        assert proposal.id == "prop-456"
        assert proposal.status == ProposalStatus.ACCEPTED
        assert proposal.author == "user123"
        assert proposal.created_at == created
        assert proposal.applied_at == applied

    def test_missing_required_field(self):
        """Test validation fails when required fields missing."""
        with pytest.raises(ValidationError) as exc_info:
            Proposal(
                id="prop-789",
                project_key="PRJ-003",
                # Missing: target_artifact, change_type, diff, rationale
            )

        errors = exc_info.value.errors()
        required_fields = {"target_artifact", "change_type", "diff", "rationale"}
        error_fields = {err["loc"][0] for err in errors}
        assert required_fields.issubset(error_fields)

    def test_invalid_enum_value(self):
        """Test validation fails with invalid enum values."""
        with pytest.raises(ValidationError):
            Proposal(
                id="prop-999",
                project_key="PRJ-004",
                target_artifact="test.md",
                change_type="invalid_type",  # Invalid
                diff="diff content",
                rationale="test",
            )

    def test_change_type_create(self):
        """Test proposal with CREATE change type."""
        proposal = Proposal(
            id="prop-c1",
            project_key="PRJ-C",
            target_artifact="new_file.md",
            change_type=ChangeType.CREATE,
            diff="--- /dev/null\n+++ b/new_file.md",
            rationale="Create new artifact",
        )
        assert proposal.change_type == ChangeType.CREATE

    def test_change_type_update(self):
        """Test proposal with UPDATE change type."""
        proposal = Proposal(
            id="prop-u1",
            project_key="PRJ-U",
            target_artifact="existing_file.md",
            change_type=ChangeType.UPDATE,
            diff="--- a/existing_file.md\n+++ b/existing_file.md",
            rationale="Update existing artifact",
        )
        assert proposal.change_type == ChangeType.UPDATE

    def test_change_type_delete(self):
        """Test proposal with DELETE change type."""
        proposal = Proposal(
            id="prop-d1",
            project_key="PRJ-D",
            target_artifact="old_file.md",
            change_type=ChangeType.DELETE,
            diff="--- a/old_file.md\n+++ /dev/null",
            rationale="Remove obsolete artifact",
        )
        assert proposal.change_type == ChangeType.DELETE

    def test_proposal_status_transitions(self):
        """Test proposal can transition between statuses."""
        # Start as pending
        proposal = Proposal(
            id="prop-t1",
            project_key="PRJ-T",
            target_artifact="test.md",
            change_type=ChangeType.UPDATE,
            diff="test diff",
            rationale="test",
            status=ProposalStatus.PENDING,
        )
        assert proposal.status == ProposalStatus.PENDING

        # Can be updated to accepted
        proposal_dict = proposal.model_dump()
        proposal_dict["status"] = ProposalStatus.ACCEPTED
        proposal_dict["applied_at"] = datetime.now(timezone.utc)
        accepted = Proposal(**proposal_dict)
        assert accepted.status == ProposalStatus.ACCEPTED
        assert accepted.applied_at is not None

    def test_pending_with_applied_at_is_rejected(self):
        """Test invalid state: pending proposal cannot have applied_at."""
        with pytest.raises(ValidationError):
            Proposal(
                id="prop-invalid-1",
                project_key="PRJ-INV",
                target_artifact="artifacts/test.md",
                change_type=ChangeType.UPDATE,
                diff="test diff",
                rationale="invalid state",
                status=ProposalStatus.PENDING,
                applied_at=datetime.now(timezone.utc),
            )

    def test_accepted_without_applied_at_is_rejected(self):
        """Test invalid state: accepted proposal must have applied_at."""
        with pytest.raises(ValidationError):
            Proposal(
                id="prop-invalid-2",
                project_key="PRJ-INV",
                target_artifact="artifacts/test.md",
                change_type=ChangeType.UPDATE,
                diff="test diff",
                rationale="invalid state",
                status=ProposalStatus.ACCEPTED,
                applied_at=None,
            )

    def test_rejected_with_applied_at_is_rejected(self):
        """Test invalid state: rejected proposal cannot have applied_at."""
        with pytest.raises(ValidationError):
            Proposal(
                id="prop-invalid-3",
                project_key="PRJ-INV",
                target_artifact="artifacts/test.md",
                change_type=ChangeType.UPDATE,
                diff="test diff",
                rationale="invalid state",
                status=ProposalStatus.REJECTED,
                applied_at=datetime.now(timezone.utc),
            )

    def test_json_serialization(self):
        """Test proposal can be serialized to JSON."""
        proposal = Proposal(
            id="prop-j1",
            project_key="PRJ-J",
            target_artifact="json_test.md",
            change_type=ChangeType.UPDATE,
            diff="test diff",
            rationale="test json",
        )

        json_str = proposal.model_dump_json()
        assert "prop-j1" in json_str
        assert "PRJ-J" in json_str
        assert "pending" in json_str

    def test_json_deserialization(self):
        """Test proposal can be deserialized from JSON."""
        json_data = {
            "id": "prop-j2",
            "project_key": "PRJ-J2",
            "target_artifact": "deserialize.md",
            "change_type": "create",
            "diff": "test diff",
            "rationale": "test deserialization",
            "status": "accepted",
            "author": "tester",
            "created_at": "2026-02-01T10:00:00",
            "applied_at": "2026-02-01T11:00:00",
        }

        proposal = Proposal(**json_data)
        assert proposal.id == "prop-j2"
        assert proposal.status == ProposalStatus.ACCEPTED
        assert proposal.change_type == ChangeType.CREATE
