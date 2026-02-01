"""
Workflow domain enums.

Contains ISO 21500 aligned workflow state enums.
"""

from enum import Enum


class WorkflowStateEnum(str, Enum):
    """ISO 21500 aligned project workflow states."""

    INITIATING = "initiating"
    PLANNING = "planning"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    CLOSING = "closing"
    CLOSED = "closed"
