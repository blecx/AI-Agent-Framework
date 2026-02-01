"""
RAID domain models.

Contains all Pydantic models for RAID register (Risk, Assumption, Issue, Dependency).
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from .enums import RAIDType, RAIDStatus, RAIDPriority, RAIDImpactLevel, RAIDLikelihood


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
    status: Optional[RAIDStatus] = Field(
        default=RAIDStatus.OPEN, description="Initial status"
    )
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
