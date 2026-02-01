"""
Governance domain models (ISO 21500/21502).

Contains all Pydantic models related to project governance, decision logging,
and stakeholder management.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GovernanceMetadata(BaseModel):
    """Project governance metadata aligned with ISO 21500/21502."""

    objectives: List[str] = Field(
        default_factory=list, description="Project objectives"
    )
    scope: str = Field(default="", description="Project scope statement")
    stakeholders: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Stakeholders with roles (name, role, responsibilities)",
    )
    decision_rights: Dict[str, str] = Field(
        default_factory=dict,
        description="Decision authority mapping (decision_type -> role)",
    )
    stage_gates: List[Dict[str, Any]] = Field(
        default_factory=list, description="Stage gates and approval checkpoints"
    )
    approvals: List[Dict[str, Any]] = Field(
        default_factory=list, description="Required approvals and authorities"
    )
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = Field(default="system", description="User who created")
    updated_by: Optional[str] = Field(
        default="system", description="User who last updated"
    )


class GovernanceMetadataUpdate(BaseModel):
    """Request model for updating governance metadata."""

    objectives: Optional[List[str]] = None
    scope: Optional[str] = None
    stakeholders: Optional[List[Dict[str, str]]] = None
    decision_rights: Optional[Dict[str, str]] = None
    stage_gates: Optional[List[Dict[str, Any]]] = None
    approvals: Optional[List[Dict[str, Any]]] = None
    updated_by: Optional[str] = Field(default="system")


class DecisionLogEntry(BaseModel):
    """Decision log entry for governance tracking."""

    id: str = Field(..., description="Unique decision ID")
    title: str = Field(..., description="Decision title")
    description: str = Field(..., description="Decision description")
    decision_date: str = Field(..., description="Date decision was made (ISO format)")
    decision_maker: str = Field(..., description="Person/role who made the decision")
    rationale: str = Field(default="", description="Rationale behind the decision")
    impact: str = Field(default="", description="Expected impact of the decision")
    status: str = Field(
        default="approved", description="Decision status (proposed, approved, rejected)"
    )
    linked_raid_ids: List[str] = Field(
        default_factory=list, description="RAID item IDs linked to this decision"
    )
    linked_change_requests: List[str] = Field(
        default_factory=list, description="Change request IDs linked to this decision"
    )
    created_at: Optional[str] = None
    created_by: Optional[str] = Field(default="system")


class DecisionLogEntryCreate(BaseModel):
    """Request model for creating a decision log entry."""

    title: str = Field(..., description="Decision title", min_length=1)
    description: str = Field(..., description="Decision description", min_length=1)
    decision_maker: str = Field(..., description="Person/role who made the decision")
    rationale: Optional[str] = Field(
        default="", description="Rationale behind the decision"
    )
    impact: Optional[str] = Field(default="", description="Expected impact")
    status: Optional[str] = Field(default="approved", description="Decision status")
    linked_raid_ids: Optional[List[str]] = Field(default_factory=list)
    linked_change_requests: Optional[List[str]] = Field(default_factory=list)
    created_by: Optional[str] = Field(default="system")
