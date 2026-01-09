"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


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
    command: str = Field(..., description="Command name (assess_gaps, generate_artifact, generate_plan)")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Optional command parameters")


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
