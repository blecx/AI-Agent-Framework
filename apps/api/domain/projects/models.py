"""
Projects domain models.

Contains all Pydantic models related to project management.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ProjectCreate(BaseModel):
    """Request model for creating a project."""

    key: str = Field(..., description="Unique project key", pattern="^[a-zA-Z0-9_-]+$")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Optional project description")


class ProjectInfo(BaseModel):
    """Project information."""

    key: str
    name: str
    description: Optional[str] = None
    methodology: str = "ISO21500"
    created_at: str
    updated_at: str


class ProjectUpdate(BaseModel):
    """Request model for updating a project."""

    name: Optional[str] = Field(None, description="Project name", min_length=1)
    description: Optional[str] = Field(None, description="Project description")
    methodology: Optional[str] = Field(None, description="Project methodology")


class ProjectState(BaseModel):
    """Aggregated project state."""

    project_info: "ProjectInfo"
    artifacts: List[Dict[str, Any]]
    last_commit: Optional[Dict[str, Any]]


class ArtifactInfo(BaseModel):
    """Artifact information."""

    path: str
    type: str
    created_at: str
    updated_at: Optional[str] = None
