"""
Audit domain enums.

Contains audit event type enums for NDJSON storage.
"""

from enum import Enum


class AuditEventType(str, Enum):
    """Audit event types."""

    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    WORKFLOW_STATE_CHANGED = "workflow_state_changed"
    GOVERNANCE_METADATA_CREATED = "governance_metadata_created"
    GOVERNANCE_METADATA_UPDATED = "governance_metadata_updated"
    DECISION_CREATED = "decision_created"
    RAID_ITEM_CREATED = "raid_item_created"
    RAID_ITEM_UPDATED = "raid_item_updated"
    ARTIFACT_CREATED = "artifact_created"
    ARTIFACT_UPDATED = "artifact_updated"
    COMMAND_PROPOSED = "command_proposed"
    COMMAND_APPLIED = "command_applied"
