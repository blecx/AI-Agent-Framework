"""
RAID domain enums.

Contains all enum types for RAID register (Risk, Assumption, Issue, Dependency).
"""

from enum import Enum


class RAIDType(str, Enum):
    """RAID item types."""

    RISK = "risk"
    ASSUMPTION = "assumption"
    ISSUE = "issue"
    DEPENDENCY = "dependency"


class RAIDStatus(str, Enum):
    """RAID item status."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    MITIGATED = "mitigated"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class RAIDPriority(str, Enum):
    """RAID item priority/severity."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RAIDImpactLevel(str, Enum):
    """Impact level for risks."""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class RAIDLikelihood(str, Enum):
    """Likelihood level for risks."""

    VERY_LIKELY = "very_likely"
    LIKELY = "likely"
    POSSIBLE = "possible"
    UNLIKELY = "unlikely"
    VERY_UNLIKELY = "very_unlikely"
