"""
Pydantic models for API requests and responses.

DEPRECATED: This file is maintained for backward compatibility only.
All models have been migrated to the domain/ directory structure following DDD architecture.

Use domain-specific imports instead:
- from domain.projects import ProjectCreate, ProjectInfo, ProjectUpdate
- from domain.commands import CommandProposal, CommandPropose, CommandApply
- from domain.governance import GovernanceMetadata, DecisionLogEntry
- from domain.raid import RAIDItem, RAIDType, RAIDStatus
- from domain.workflow import WorkflowStateEnum, WorkflowTransition
- from domain.audit import AuditEvent, AuditEventType
- from domain.skills import SkillInfo, PlanRequest, LearnRequest
"""

# Re-export all models from domain layer for backward compatibility
from domain import *  # noqa: F401, F403

__all__ = [
    # Projects
    "ProjectCreate",
    "ProjectInfo",
    "ProjectUpdate",
    "ProjectState",
    "ArtifactInfo",
    # Commands
    "FileChange",
    "CommandProposal",
    "CommandPropose",
    "CommandApply",
    "CommandApplyResult",
    "ProposalStatus",
    "Proposal",
    "ProposalCreate",
    "ProposalList",
    "CommandStatus",
    "CommandHistory",
    "CommandExecute",
    "CommandHistoryList",
    # Governance
    "GovernanceMetadata",
    "GovernanceMetadataUpdate",
    "DecisionLogEntry",
    "DecisionLogEntryCreate",
    # RAID
    "RAIDType",
    "RAIDStatus",
    "RAIDPriority",
    "RAIDImpactLevel",
    "RAIDLikelihood",
    "RAIDItem",
    "RAIDItemCreate",
    "RAIDItemUpdate",
    "RAIDItemList",
    # Workflow
    "WorkflowStateEnum",
    "WorkflowTransition",
    "WorkflowStateUpdate",
    "WorkflowStateInfo",
    # Audit
    "AuditEventType",
    "AuditEvent",
    "AuditEventList",
    # Skills
    "SkillInfo",
    "SkillListResponse",
    "MemoryGetRequest",
    "MemorySetRequest",
    "MemoryResponse",
    "PlanRequest",
    "PlanStep",
    "PlanResponse",
    "LearnRequest",
    "LearnResponse",
]
