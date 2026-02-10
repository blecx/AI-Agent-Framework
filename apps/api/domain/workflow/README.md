# Workflow Domain

## Overview

The Workflow domain manages ISO 21500-aligned project workflow state transitions and history tracking for auditable process governance.

## Responsibilities

- Define workflow state model and transitions
- Track state transition history
- Validate state transition rules
- Provide request/response models for API layer

## Domain Models

### WorkflowStateInfo (Entity)

Current workflow state and transition history.

**Fields:**

- `current_state`: Current workflow state (enum)
- `previous_state`: Previous state before last transition
- `transition_history`: List of all state transitions
- `updated_at`: Timestamp of last update (ISO format)
- `updated_by`: Actor who performed last transition

**Validation:**

- `current_state` must be valid WorkflowStateEnum value
- `updated_at` must be ISO 8601 format
- `transition_history` maintains chronological order

### WorkflowTransition

Record of a single state transition.

**Fields:**

- `from_state`: Source state
- `to_state`: Destination state
- `timestamp`: When transition occurred (ISO format)
- `actor`: Who performed the transition
- `reason`: Optional justification for transition

### WorkflowStateUpdate

Request model for state transitions.

**Fields:**

- `to_state`: Target state (required)
- `actor`: Who is performing transition (default: "system")
- `reason`: Optional reason for transition

### WorkflowStateEnum

ISO 21500-aligned workflow states:

- `INITIATION`: Project startup and authorization
- `PLANNING`: Requirements, scope, schedule planning
- `EXECUTION`: Active development and delivery
- `MONITORING_AND_CONTROLLING`: Progress tracking and adjustments
- `CLOSING`: Project closure and lessons learned

## Usage

### Transitioning State

```python
from apps.api.domain.workflow.models import WorkflowStateUpdate
from apps.api.domain.workflow.enums import WorkflowStateEnum

update = WorkflowStateUpdate(
    to_state=WorkflowStateEnum.EXECUTION,
    actor="john.doe@example.com",
    reason="Planning phase complete, approved to start execution"
)
```

### Querying State History

```python
from apps.api.domain.workflow.models import WorkflowStateInfo

# Service layer returns:
state_info = WorkflowStateInfo(
    current_state=WorkflowStateEnum.EXECUTION,
    previous_state=WorkflowStateEnum.PLANNING,
    transition_history=[
        WorkflowTransition(
            from_state=WorkflowStateEnum.INITIATION,
            to_state=WorkflowStateEnum.PLANNING,
            timestamp="2025-02-01T10:00:00Z",
            actor="system",
            reason="Initial planning phase"
        ),
        WorkflowTransition(
            from_state=WorkflowStateEnum.PLANNING,
            to_state=WorkflowStateEnum.EXECUTION,
            timestamp="2025-02-10T15:30:00Z",
            actor="john.doe@example.com",
            reason="Planning complete"
        )
    ],
    updated_at="2025-02-10T15:30:00Z",
    updated_by="john.doe@example.com"
)
```

## Design Notes

- **SRP Compliance**: Workflow domain focuses ONLY on state management, not artifact storage
- **ISO 21500 Alignment**: State names directly map to ISO 21500 process groups
- **Audit Trail**: All transitions tracked with timestamp, actor, and optional reason
- **Immutability**: Transition history is append-only (never modified or deleted)
- **Validation**: Service layer enforces valid state transitions (e.g., can't skip PLANNING)
