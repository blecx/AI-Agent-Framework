"""Proposal domain models for propose/apply workflow."""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from enum import Enum
from datetime import datetime, timezone
from typing import Optional


class ProposalStatus(str, Enum):
    """Status of a proposal in its lifecycle."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ChangeType(str, Enum):
    """Type of change proposed for an artifact."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Proposal(BaseModel):
    """
    Domain entity representing a proposed change to an artifact.

    Proposals enable structured, auditable artifact modifications
    with traceability and approval workflows.
    """

    id: str = Field(..., description="Unique proposal identifier")
    project_key: str = Field(..., description="Project this proposal belongs to")
    target_artifact: str = Field(..., description="Path to target artifact")
    change_type: ChangeType = Field(..., description="Type of change")
    diff: str = Field(..., description="Unified diff of proposed changes")
    rationale: str = Field(..., description="Justification for the change")
    status: ProposalStatus = Field(
        default=ProposalStatus.PENDING, description="Current proposal status"
    )
    author: str = Field(default="system", description="Proposal author")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    applied_at: Optional[datetime] = Field(
        default=None, description="Timestamp when proposal was applied"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "prop-123",
                "project_key": "PRJ-001",
                "target_artifact": "artifacts/requirements.md",
                "change_type": "update",
                "diff": "--- a/requirements.md\n+++ b/requirements.md\n...",
                "rationale": "Updated requirements based on stakeholder feedback",
                "status": "pending",
                "author": "system",
                "created_at": "2026-02-01T10:00:00Z",
                "applied_at": None,
            }
        }
    )

    @model_validator(mode="after")
    def validate_lifecycle_fields(self):
        """Validate lifecycle field combinations for deterministic state rules."""
        if self.status == ProposalStatus.ACCEPTED and self.applied_at is None:
            raise ValueError("applied_at is required when status is accepted")
        if self.status != ProposalStatus.ACCEPTED and self.applied_at is not None:
            raise ValueError("applied_at can only be set when status is accepted")
        return self


class ProposalCreate(BaseModel):
    """
    Request model for creating a proposal.

    Excludes project_key (from path), status (set by system),
    created_at/applied_at (auto-generated).
    """

    id: str = Field(..., description="Unique proposal identifier")
    target_artifact: str = Field(..., description="Path to target artifact")
    change_type: ChangeType = Field(..., description="Type of change")
    diff: str = Field(..., description="Unified diff of proposed changes")
    rationale: str = Field(..., description="Justification for the change")
    author: str = Field(default="system", description="Proposal author")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "prop-001",
                "target_artifact": "artifacts/pmp.md",
                "change_type": "update",
                "diff": "--- old\n+++ new\n...",
                "rationale": "Update project scope per stakeholder feedback",
                "author": "user@example.com",
            }
        }
    )
