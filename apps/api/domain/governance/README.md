# Governance Domain

## Overview

The Governance domain implements ISO 21500/21502-aligned project governance structures including stakeholder management, decision rights, stage gates, and decision logging.

## Responsibilities

- Define governance metadata structure
- Track stakeholders and decision rights
- Log governance decisions with traceability
- Manage stage gates and approval workflows

## Domain Models

### GovernanceMetadata (Entity)

Project governance structure and policies.

**Fields:**

- `objectives`: List of project objectives
- `scope`: Project scope statement
- `stakeholders`: List of stakeholders with roles (name, role, responsibilities)
- `decision_rights`: Decision authority mapping (decision_type → role)
- `stage_gates`: Stage gates and approval checkpoints
- `approvals`: Required approvals and authorities
- `created_at`: Creation timestamp (ISO format)
- `updated_at`: Last update timestamp (ISO format)
- `created_by`: Original creator
- `updated_by`: Last updater

**Validation:**

- `stakeholders` must have name and role fields
- `decision_rights` keys should match decision types
- `stage_gates` align with workflow states

### GovernanceMetadataUpdate

Request model for updating governance metadata (all fields optional for partial updates).

### DecisionLogEntry (Entity)

Record of a governance decision.

**Fields:**

- `id`: Unique decision identifier
- `title`: Decision title/summary
- `description`: Detailed decision description
- `decision_date`: When decision was made (ISO format)
- `decision_maker`: Person/role who made the decision
- `rationale`: Justification for the decision
- `status`: Decision status (PROPOSED, APPROVED, REJECTED, IMPLEMENTED)
- `linked_raid_items`: Related RAID register item IDs
- `linked_artifacts`: Affected artifact paths
- `created_at`: Creation timestamp (ISO format)
- `updated_at`: Last update timestamp (ISO format)
- `created_by`: Original creator
- `updated_by`: Last updater

**Validation:**

- `decision_date` must be ISO 8601 format
- `status` must be valid enum value
- `decision_maker` should match governance roles

### DecisionLogEntryCreate / DecisionLogEntryUpdate

Request models for API operations.

## Usage

### Setting Up Governance

```python
from apps.api.domain.governance.models import GovernanceMetadata

governance = GovernanceMetadata(
    objectives=[
        "Deliver MVP by Q2 2025",
        "Maintain 99.9% uptime SLA",
        "Complete within $500K budget"
    ],
    scope="Build customer onboarding portal with SSO integration",
    stakeholders=[
        {"name": "Jane Doe", "role": "Project Sponsor", "responsibilities": "Budget approval"},
        {"name": "John Smith", "role": "Technical Lead", "responsibilities": "Architecture decisions"},
        {"name": "Alice Johnson", "role": "Product Owner", "responsibilities": "Requirements prioritization"}
    ],
    decision_rights={
        "budget_changes": "Project Sponsor",
        "architecture": "Technical Lead",
        "scope_changes": "Project Sponsor + Product Owner"
    },
    stage_gates=[
        {"stage": "PLANNING", "approver": "Project Sponsor", "criteria": "Budget and scope approved"},
        {"stage": "EXECUTION", "approver": "Technical Lead", "criteria": "Architecture review complete"}
    ]
)
```

### Logging a Decision

```python
from apps.api.domain.governance.models import DecisionLogEntryCreate

decision = DecisionLogEntryCreate(
    title="Adopt React for frontend framework",
    description="Evaluated Angular, Vue, and React. Selected React for team expertise and ecosystem.",
    decision_date="2025-02-10",
    decision_maker="John Smith (Technical Lead)",
    rationale="Team has 3 React experts, largest community support, aligns with company standards",
    linked_raid_items=["RISK-042"],  # Mitigates technology risk
    linked_artifacts=["architecture/tech-stack.md"]
)
```

### Updating Governance

```python
from apps.api.domain.governance.models import GovernanceMetadataUpdate

update = GovernanceMetadataUpdate(
    stakeholders=[
        {"name": "Jane Doe", "role": "Project Sponsor", "responsibilities": "Budget approval"},
        {"name": "John Smith", "role": "Technical Lead", "responsibilities": "Architecture decisions"},
        {"name": "Bob Wilson", "role": "QA Lead", "responsibilities": "Quality standards"}  # Added
    ],
    updated_by="jane.doe@example.com"
)
```

## Design Notes

- **SRP Compliance**: Governance domain focuses ONLY on governance structure and decisions, not enforcement
- **ISO 21500/21502 Alignment**: Follows ISO governance and stakeholder management principles
- **Traceability**: Decision log links to RAID items and artifacts for audit trails
- **Flexibility**: `decision_rights` and `stage_gates` adapt to organization-specific workflows
- **Stakeholder Focus**: Explicit stakeholder roles and responsibilities for clarity
- **Immutability**: Decision log entries are append-only (status can update, but history preserved)
