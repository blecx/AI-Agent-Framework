"""Pydantic schemas for hub API."""
import json
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Run schemas ──────────────────────────────────────────────────────────────

class RunCreate(BaseModel):
    repo: str = Field(..., description="GitHub owner/repo")
    ref: str = Field(..., description="git ref (branch, SHA, tag)")
    spec_content: Optional[str] = Field(None, description="Contents of spec.md")


class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    repo: str
    ref: str
    spec_path: Optional[str]
    spec_content: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


# ── Task schemas ─────────────────────────────────────────────────────────────

TASK_TYPES = [
    "SPEC_NORMALIZE",
    "STORY_SPLIT",
    "TASK_DECOMPOSE",
    "PATCH_IMPLEMENT",
    "RUN_TESTS_PYTHON",
]


class TaskCreate(BaseModel):
    task_type: str
    depends_on: list[str] = Field(default_factory=list)
    input_data: Optional[dict[str, Any]] = None
    model_policy: Optional[str] = None

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        if v not in TASK_TYPES:
            raise ValueError(f"task_type must be one of {TASK_TYPES}")
        return v


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: UUID
    task_type: str
    status: str
    worker_id: Optional[str]
    lease_expires_at: Optional[datetime]
    input_data: Optional[str]
    output_data: Optional[str]
    error_message: Optional[str]
    depends_on: Optional[str]
    model_policy: Optional[str]
    requires_approval: bool
    approved: Optional[bool]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    retry_count: int

    def input_dict(self) -> dict[str, Any]:
        if self.input_data:
            return json.loads(self.input_data)
        return {}

    def depends_on_list(self) -> list[str]:
        if self.depends_on:
            return json.loads(self.depends_on)
        return []


class TaskClaim(BaseModel):
    worker_id: str
    lease_seconds: int = Field(default=120, ge=10, le=3600)


class TaskComplete(BaseModel):
    output_data: Optional[dict[str, Any]] = None


class TaskFail(BaseModel):
    error_message: str


class TaskHeartbeat(BaseModel):
    worker_id: str
    lease_seconds: int = Field(default=120, ge=10, le=3600)


# ── Artifact schemas ─────────────────────────────────────────────────────────

class ArtifactRegister(BaseModel):
    artifact_type: str  # patch, log, snapshot
    filename: str


class ArtifactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    run_id: UUID
    artifact_type: str
    filename: str
    storage_path: str
    size_bytes: Optional[int]
    created_at: datetime


# ── Config schemas ────────────────────────────────────────────────────────────

class ConfigSet(BaseModel):
    value: str


class ConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str
    updated_at: datetime
