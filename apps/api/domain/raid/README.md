# RAID Domain

## Overview

The RAID domain implements Risk, Assumption, Issue, and Dependency register for project management aligned with ISO 21500 risk management practices.

## Responsibilities

- Define `RAIDItem` entity for all RAID types
- Track risk assessment (impact, likelihood)
- Manage mitigation plans and next actions
- Link RAID items to governance decisions and change requests

## Domain Models

### RAIDItem (Entity)

Core domain entity representing a RAID register entry.

**Fields:**

- `id`: Unique RAID item identifier
- `type`: RAID type (RISK, ASSUMPTION, ISSUE, DEPENDENCY)
- `title`: Brief summary of the RAID item
- `description`: Detailed description
- `status`: Current status (OPEN, IN_PROGRESS, CLOSED, etc.)
- `owner`: Person responsible for managing this item
- `priority`: Priority/severity (LOW, MEDIUM, HIGH, CRITICAL)
- `impact`: Impact level if realized (for risks)
- `likelihood`: Probability of occurrence (for risks)
- `mitigation_plan`: Response or mitigation strategy
- `next_actions`: List of actionable next steps
- `linked_decisions`: Related governance decision IDs
- `linked_change_requests`: Related change request IDs
- `created_at`: Creation timestamp (ISO format)
- `updated_at`: Last update timestamp (ISO format)
- `created_by`: Original creator
- `updated_by`: Last updater
- `target_resolution_date`: Target completion date (optional)

**Validation:**

- `type` must be valid RAIDType enum value
- `status` must be valid RAIDStatus enum value
- `priority` must be valid RAIDPriority enum value
- `impact` and `likelihood` primarily apply to RISK type

### RAIDItemCreate / RAIDItemUpdate

Request models for API operations (RAIDItemUpdate has optional fields for partial updates).

### RAIDType Enum

- `RISK`: Potential future problem
- `ASSUMPTION`: Belief taken as true without proof
- `ISSUE`: Current problem requiring resolution
- `DEPENDENCY`: External dependency or prerequisite

### RAIDStatus Enum

- `OPEN`: Newly identified, not yet addressed
- `IN_PROGRESS`: Actively being worked on
- `RESOLVED`: Successfully addressed
- `CLOSED`: Finalized and archived
- `ACCEPTED`: Risk accepted, no mitigation planned

### RAIDPriority Enum

- `LOW`: Minor impact, low urgency
- `MEDIUM`: Moderate impact, standard handling
- `HIGH`: Significant impact, escalated attention
- `CRITICAL`: Severe impact, immediate action required

### RAIDImpactLevel / RAIDLikelihood

Risk assessment scales (typically 1-5 or LOW/MEDIUM/HIGH/VERY_HIGH).

## Usage

### Creating a Risk

```python
from apps.api.domain.raid.models import RAIDItemCreate
from apps.api.domain.raid.enums import RAIDType, RAIDPriority, RAIDImpactLevel, RAIDLikelihood

risk = RAIDItemCreate(
    type=RAIDType.RISK,
    title="Third-party API may be deprecated",
    description="Vendor announced end-of-life for API v1 in Q3",
    owner="john.doe@example.com",
    priority=RAIDPriority.HIGH,
    impact=RAIDImpactLevel.HIGH,
    likelihood=RAIDLikelihood.MEDIUM,
    mitigation_plan="Migrate to API v2 by Q2, implement fallback adapter pattern"
)
```

### Creating an Issue

```python
issue = RAIDItemCreate(
    type=RAIDType.ISSUE,
    title="Database connection pool exhausted during load test",
    description="Load test at 500 concurrent users revealed connection limits",
    status=RAIDStatus.IN_PROGRESS,
    owner="jane.smith@example.com",
    priority=RAIDPriority.CRITICAL,
    mitigation_plan="Increase pool size from 50 to 200, add connection monitoring",
    linked_change_requests=["CR-123"]
)
```

### Linking to Governance Decision

```python
assumption = RAIDItemCreate(
    type=RAIDType.ASSUMPTION,
    title="User base will not exceed 10K users in first year",
    description="Capacity planning based on projected growth rate",
    owner="architect@example.com",
    priority=RAIDPriority.MEDIUM,
    linked_decisions=["DEC-042"]  # References governance decision log
)
```

## Design Notes

- **SRP Compliance**: RAID domain focuses ONLY on register item structure, not storage
- **ISO 21500 Alignment**: Risk management practices follow ISO 21500 guidance
- **Unified Model**: Single RAIDItem entity for all types (Risk, Assumption, Issue, Dependency)
- **Traceability**: Links to governance decisions and change requests for audit trails
- **Risk Assessment**: Impact and likelihood fields primarily for risk type items
- **Flexibility**: `next_actions` and `mitigation_plan` adapt to all RAID types
