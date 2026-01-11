"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ProjectCreate(BaseModel):
    """Request model for creating a project."""

    key: str = Field(..., description="Unique project key", pattern="^[a-zA-Z0-9_-]+$")
    name: str = Field(..., description="Project name")


class ProjectInfo(BaseModel):
    """Project information."""

    key: str
    name: str
    methodology: str = "ISO21500"
    created_at: str
    updated_at: str


class FileChange(BaseModel):
    """Represents a file change with unified diff."""

    path: str
    operation: str  # "create", "modify", "delete"
    diff: str


class CommandProposal(BaseModel):
    """Response model for command proposal."""

    proposal_id: str
    assistant_message: str
    file_changes: List[FileChange]
    draft_commit_message: str


class CommandPropose(BaseModel):
    """Request model for proposing a command."""

    command: str = Field(
        ..., description="Command name (assess_gaps, generate_artifact, generate_plan)"
    )
    params: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional command parameters"
    )


class CommandApply(BaseModel):
    """Request model for applying a proposal."""

    proposal_id: str


class CommandApplyResult(BaseModel):
    """Response model for command apply."""

    commit_hash: str
    changed_files: List[str]
    message: str


class ProjectState(BaseModel):
    """Aggregated project state."""

    project_info: ProjectInfo
    artifacts: List[Dict[str, Any]]
    last_commit: Optional[Dict[str, Any]]


class ArtifactInfo(BaseModel):
    """Artifact information with version history."""

    path: str
    name: str
    type: str
    versions: List[Dict[str, Any]]


# ============================================================================
# Governance Models (ISO 21500/21502)
# ============================================================================


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


# ============================================================================
# RAID Register Models
# ============================================================================


class RAIDType(str, Enum):
    """RAID item types."""

    RISK = "risk"
    ASSUMPTION = "assumption"
    ISSUE = "issue"
    DEPENDENCY = "dependency"


class RAIDStatus(str, Enum):
    """RAID item status."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    MITIGATED = "mitigated"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class RAIDPriority(str, Enum):
    """RAID item priority/severity."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RAIDImpactLevel(str, Enum):
    """Impact level for risks."""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class RAIDLikelihood(str, Enum):
    """Likelihood level for risks."""

    VERY_LIKELY = "very_likely"
    LIKELY = "likely"
    POSSIBLE = "possible"
    UNLIKELY = "unlikely"
    VERY_UNLIKELY = "very_unlikely"


class RAIDItem(BaseModel):
    """RAID register item."""

    id: str = Field(..., description="Unique RAID item ID")
    type: RAIDType = Field(..., description="RAID item type")
    title: str = Field(..., description="RAID item title")
    description: str = Field(..., description="Detailed description")
    status: RAIDStatus = Field(default=RAIDStatus.OPEN, description="Current status")
    owner: str = Field(..., description="Owner/assignee")
    priority: RAIDPriority = Field(
        default=RAIDPriority.MEDIUM, description="Priority/severity"
    )
    impact: Optional[RAIDImpactLevel] = Field(
        default=None, description="Impact level (primarily for risks)"
    )
    likelihood: Optional[RAIDLikelihood] = Field(
        default=None, description="Likelihood (primarily for risks)"
    )
    mitigation_plan: str = Field(default="", description="Mitigation or response plan")
    next_actions: List[str] = Field(
        default_factory=list, description="Next actions to take"
    )
    linked_decisions: List[str] = Field(
        default_factory=list, description="Linked governance decision IDs"
    )
    linked_change_requests: List[str] = Field(
        default_factory=list, description="Linked change request IDs"
    )
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    updated_at: str = Field(..., description="Last update timestamp (ISO format)")
    created_by: str = Field(default="system", description="User who created")
    updated_by: str = Field(default="system", description="User who last updated")
    target_resolution_date: Optional[str] = Field(
        default=None, description="Target date for resolution"
    )


class RAIDItemCreate(BaseModel):
    """Request model for creating a RAID item."""

    type: RAIDType = Field(..., description="RAID item type")
    title: str = Field(..., description="RAID item title", min_length=1)
    description: str = Field(..., description="Detailed description", min_length=1)
    owner: str = Field(..., description="Owner/assignee")
    priority: Optional[RAIDPriority] = Field(default=RAIDPriority.MEDIUM)
    impact: Optional[RAIDImpactLevel] = None
    likelihood: Optional[RAIDLikelihood] = None
    mitigation_plan: Optional[str] = Field(default="")
    next_actions: Optional[List[str]] = Field(default_factory=list)
    linked_decisions: Optional[List[str]] = Field(default_factory=list)
    linked_change_requests: Optional[List[str]] = Field(default_factory=list)
    created_by: Optional[str] = Field(default="system")
    target_resolution_date: Optional[str] = None


class RAIDItemUpdate(BaseModel):
    """Request model for updating a RAID item."""

    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None, min_length=1)
    status: Optional[RAIDStatus] = None
    owner: Optional[str] = None
    priority: Optional[RAIDPriority] = None
    impact: Optional[RAIDImpactLevel] = None
    likelihood: Optional[RAIDLikelihood] = None
    mitigation_plan: Optional[str] = None
    next_actions: Optional[List[str]] = None
    linked_decisions: Optional[List[str]] = None
    linked_change_requests: Optional[List[str]] = None
    updated_by: Optional[str] = Field(default="system")
    target_resolution_date: Optional[str] = None


class RAIDItemList(BaseModel):
    """Response model for RAID item list."""

    items: List[RAIDItem]
    total: int
    filtered_by: Optional[Dict[str, Any]] = None
