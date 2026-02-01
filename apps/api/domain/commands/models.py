"""
Commands domain models.

Contains all Pydantic models related to command execution, proposals, and history.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


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


# Proposal API Models (Compatibility Layer)


class ProposalStatus(str, Enum):
    """Proposal status."""

    PENDING = "pending"
    APPLIED = "applied"
    REJECTED = "rejected"


class Proposal(BaseModel):
    """Proposal for client compatibility."""

    id: str = Field(..., description="Proposal ID")
    project_key: str = Field(..., description="Project key")
    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Command parameters"
    )
    status: ProposalStatus = Field(
        default=ProposalStatus.PENDING, description="Proposal status"
    )
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    assistant_message: Optional[str] = Field(
        default=None, description="AI assistant message"
    )
    file_changes: List[FileChange] = Field(
        default_factory=list, description="Proposed file changes"
    )
    draft_commit_message: Optional[str] = Field(
        default=None, description="Draft commit message"
    )


class ProposalCreate(BaseModel):
    """Request model for creating a proposal."""

    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(default_factory=dict)


class ProposalList(BaseModel):
    """Response model for listing proposals."""

    proposals: List[Proposal]
    total: int


# Command History Models


class CommandStatus(str, Enum):
    """Command execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class CommandHistory(BaseModel):
    """Command execution history."""

    id: str = Field(..., description="Unique command ID")
    project_key: str = Field(..., description="Project key")
    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(default_factory=dict)
    status: CommandStatus = Field(default=CommandStatus.PENDING)
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    started_at: Optional[str] = Field(
        default=None, description="Start timestamp (ISO format)"
    )
    completed_at: Optional[str] = Field(
        default=None, description="Completion timestamp"
    )
    proposal_id: Optional[str] = Field(
        default=None, description="Associated proposal ID"
    )
    commit_hash: Optional[str] = Field(
        default=None, description="Commit hash if applied"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    # Deprecated fields for backward compatibility
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Command result (deprecated)"
    )
    error: Optional[str] = Field(
        default=None, description="Error message (deprecated, use error_message)"
    )


class CommandExecute(BaseModel):
    """Request model for executing a command."""

    project_key: str = Field(..., description="Project key")
    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(default_factory=dict)


class CommandHistoryList(BaseModel):
    """Response model for command history list."""

    commands: List[CommandHistory]
    total: int
