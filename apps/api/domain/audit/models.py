"""
Audit domain models (NDJSON storage).

Contains all Pydantic models for audit event logging and querying.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from .enums import AuditEventType


class AuditEvent(BaseModel):
    """Audit event schema for NDJSON storage."""

    event_id: str = Field(..., description="Unique event identifier")
    event_type: AuditEventType = Field(..., description="Type of audit event")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    actor: str = Field(default="system", description="User/system that triggered event")
    correlation_id: Optional[str] = Field(
        default=None, description="Request/correlation ID for tracing"
    )
    project_key: str = Field(..., description="Project key this event relates to")
    payload_summary: Dict[str, Any] = Field(
        default_factory=dict, description="Summary of event payload"
    )
    resource_hash: Optional[str] = Field(
        default=None, description="Hash of affected resource for compliance"
    )


class AuditEventList(BaseModel):
    """Response model for audit event list."""

    events: List[AuditEvent]
    total: int
    limit: int
    offset: int
    filtered_by: Optional[Dict[str, Any]] = None
