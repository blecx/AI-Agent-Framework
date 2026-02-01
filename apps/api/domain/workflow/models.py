"""
Workflow domain models (ISO 21500 aligned).

Contains all Pydantic models related to workflow state management and transitions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

from .enums import WorkflowStateEnum


class WorkflowTransition(BaseModel):
    """Workflow state transition information."""

    from_state: WorkflowStateEnum
    to_state: WorkflowStateEnum
    timestamp: str
    actor: str = Field(default="system")
    reason: Optional[str] = None


class WorkflowStateUpdate(BaseModel):
    """Request model for updating workflow state."""

    to_state: WorkflowStateEnum = Field(
        ..., description="Target state to transition to"
    )
    actor: Optional[str] = Field(
        default="system", description="User/actor performing transition"
    )
    reason: Optional[str] = Field(
        default=None, description="Reason for state transition"
    )


class WorkflowStateInfo(BaseModel):
    """Current workflow state information."""

    current_state: WorkflowStateEnum
    previous_state: Optional[WorkflowStateEnum] = None
    transition_history: List[WorkflowTransition] = Field(default_factory=list)
    updated_at: str
    updated_by: str = Field(default="system")
