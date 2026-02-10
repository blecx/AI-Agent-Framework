# Audit Domain

## Overview

The Audit domain provides event logging and querying for compliance, security auditing, and operational observability using NDJSON storage.

## Responsibilities

- Define `AuditEvent` entity for structured event logging
- Support event filtering and pagination
- Provide resource hashing for compliance verification
- Enable correlation tracking across requests

## Domain Models

### AuditEvent (Entity)

Core domain entity representing a single audit event.

**Fields:**
- `event_id`: Unique event identifier
- `event_type`: Type of event (see AuditEventType enum)
- `timestamp`: ISO 8601 timestamp
- `actor`: User or system that triggered the event
- `correlation_id`: Request/trace ID for distributed tracing (optional)
- `project_key`: Project this event relates to
- `payload_summary`: Summary of event details (dict)
- `resource_hash`: SHA256 hash of affected resource for compliance (optional)

**Validation:**
- `event_type` must be valid enum value
- `timestamp` must be ISO 8601 format
- `project_key` must exist

### AuditEventList

Response model for paginated audit event queries.

**Fields:**
- `events`: List of AuditEvent objects
- `total`: Total matching events (before pagination)
- `limit`: Page size limit
- `offset`: Record offset for pagination
- `filtered_by`: Applied filters (optional)

### AuditEventType Enum

Event types tracked by the audit system:

- `PROJECT_CREATED`: New project initialization
- `PROJECT_UPDATED`: Project metadata changes
- `ARTIFACT_CREATED`: New artifact added
- `ARTIFACT_UPDATED`: Existing artifact modified
- `ARTIFACT_DELETED`: Artifact removed
- `PROPOSAL_CREATED`: New change proposal
- `PROPOSAL_ACCEPTED`: Proposal approved and applied
- `PROPOSAL_REJECTED`: Proposal declined
- `TEMPLATE_APPLIED`: Template used to generate artifact
- `WORKFLOW_STATE_CHANGED`: Project workflow state transition
- `USER_ACTION`: Generic user-initiated action

## Storage Format

Audit events are stored in **NDJSON** (Newline Delimited JSON) format:

```ndjson
{"event_id":"evt-001","event_type":"PROJECT_CREATED","timestamp":"2025-02-10T10:00:00Z","actor":"user@example.com","project_key":"PROJ-001","payload_summary":{"name":"New Project"}}
{"event_id":"evt-002","event_type":"ARTIFACT_CREATED","timestamp":"2025-02-10T10:05:00Z","actor":"system","project_key":"PROJ-001","payload_summary":{"artifact":"pmp.md"},"resource_hash":"abc123..."}
```

**Benefits:**
- Append-only writes (fast, no locking)
- Line-oriented processing (grep, awk, etc.)
- Streaming support
- Schema evolution friendly

## Usage

### Logging an Event

```python
from apps.api.domain.audit.models import AuditEvent
from apps.api.domain.audit.enums import AuditEventType
from datetime import datetime, timezone

event = AuditEvent(
    event_id="evt-123",
    event_type=AuditEventType.ARTIFACT_UPDATED,
    timestamp=datetime.now(timezone.utc).isoformat(),
    actor="user@example.com",
    correlation_id="req-456",
    project_key="PROJ-001",
    payload_summary={"artifact": "requirements.md", "change": "Added section 3"},
    resource_hash="sha256:abc123def456..."
)
```

### Querying Events

```python
from apps.api.domain.audit.models import AuditEventList

# Service layer would filter NDJSON file and return:
result = AuditEventList(
    events=[event1, event2],
    total=42,
    limit=20,
    offset=0,
    filtered_by={"project_key": "PROJ-001", "event_type": "ARTIFACT_UPDATED"}
)
```

## Design Notes

- **SRP Compliance**: Audit domain focuses ONLY on event structure and querying, not persistence
- **No Infrastructure Dependencies**: Pure domain models, storage handled by service layer
- **Immutability**: Audit events are immutable once written (append-only)
- **Privacy**: `resource_hash` instead of full payload for sensitive data
- **Traceability**: `correlation_id` links events across distributed services
