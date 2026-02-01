"""
Skills domain models (Cognitive Skills).

Contains all Pydantic models for agent cognitive skills, memory, planning, and learning.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SkillInfo(BaseModel):
    """Information about a cognitive skill."""

    name: str = Field(..., description="Skill name")
    version: str = Field(..., description="Skill version")
    description: str = Field(..., description="Skill description")
    enabled: bool = Field(..., description="Whether skill is enabled")


class SkillListResponse(BaseModel):
    """Response model for listing skills."""

    skills: List[SkillInfo]
    total: int


class MemoryGetRequest(BaseModel):
    """Request model for getting memory."""

    memory_type: str = Field(
        ..., description="Memory type: 'short_term' or 'long_term'"
    )


class MemorySetRequest(BaseModel):
    """Request model for setting memory."""

    memory_type: str = Field(
        ..., description="Memory type: 'short_term' or 'long_term'"
    )
    data: Dict[str, Any] = Field(..., description="Memory data to store")


class MemoryResponse(BaseModel):
    """Response model for memory operations."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    timestamp: str


class PlanRequest(BaseModel):
    """Request model for creating a plan."""

    goal: str = Field(..., description="Goal to achieve", min_length=1)
    constraints: Optional[List[str]] = Field(
        default_factory=list, description="Constraints to consider"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context"
    )


class PlanStep(BaseModel):
    """A step in a plan."""

    step: int = Field(..., description="Step number")
    action: str = Field(..., description="Action to take")
    description: str = Field(..., description="Step description")
    status: str = Field(default="pending", description="Step status")
    dependencies: List[int] = Field(
        default_factory=list, description="Dependencies on other steps"
    )


class PlanResponse(BaseModel):
    """Response model for plan generation."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearnRequest(BaseModel):
    """Request model for logging an experience."""

    context: str = Field(..., description="Context of the experience", min_length=1)
    action: str = Field(..., description="Action taken", min_length=1)
    outcome: str = Field(..., description="Outcome observed", min_length=1)
    feedback: Optional[str] = Field(default="", description="Feedback or reflection")
    tags: Optional[List[str]] = Field(
        default_factory=list, description="Tags for categorization"
    )


class LearnResponse(BaseModel):
    """Response model for learning operations."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    timestamp: str
