# ISO 21500/21502 Governance Backbone

## Overview

The governance backbone provides a structured framework for managing project governance in alignment with ISO 21500/21502 standards. It enables organizations to track governance metadata, decision logs, and maintain traceability across project artifacts.

## Features

### 1. Governance Metadata

Governance metadata captures essential project governance information:

- **Objectives**: Clear project objectives and goals
- **Scope**: Project scope statement defining boundaries
- **Stakeholders**: Stakeholder register with roles and responsibilities
- **Decision Rights**: Authority mapping for different types of decisions
- **Stage Gates**: Key checkpoints and milestones requiring approval
- **Approvals**: Required approvals and approval authorities

### 2. Decision Log

The decision log provides a structured record of key project decisions:

- **Decision Details**: Title, description, and rationale
- **Decision Maker**: Person or role who made the decision
- **Impact Analysis**: Expected impact of the decision
- **Status**: Decision status (proposed, approved, rejected)
- **Traceability**: Links to RAID items and change requests
- **Audit Trail**: Creation timestamp and creator information

### 3. Traceability

The governance backbone supports bidirectional traceability:

- Link decisions to RAID items (risks, assumptions, issues, dependencies)
- Link RAID items to decisions
- Query RAID items by linked decision
- Full audit trail of all linkages

## API Reference

### Governance Metadata Endpoints

#### Get Governance Metadata
```http
GET /projects/{project_key}/governance/metadata
```

**Response:**
```json
{
  "objectives": ["Objective 1", "Objective 2"],
  "scope": "Project scope statement",
  "stakeholders": [
    {
      "name": "John Doe",
      "role": "Project Manager",
      "responsibilities": "Overall delivery"
    }
  ],
  "decision_rights": {
    "architecture": "Technical Lead",
    "budget": "Project Manager"
  },
  "stage_gates": [
    {
      "name": "Design Complete",
      "date": "2026-02-01",
      "status": "pending"
    }
  ],
  "approvals": [
    {
      "type": "budget",
      "approver": "Finance Director",
      "status": "pending"
    }
  ],
  "created_at": "2026-01-11T20:00:00Z",
  "updated_at": "2026-01-11T20:00:00Z",
  "created_by": "admin",
  "updated_by": "admin"
}
```

#### Create Governance Metadata
```http
POST /projects/{project_key}/governance/metadata
Content-Type: application/json

{
  "objectives": ["Objective 1", "Objective 2"],
  "scope": "Project scope statement",
  "stakeholders": [...],
  "decision_rights": {...},
  "stage_gates": [...],
  "approvals": [...],
  "created_by": "admin"
}
```

#### Update Governance Metadata
```http
PUT /projects/{project_key}/governance/metadata
Content-Type: application/json

{
  "objectives": ["Updated objective"],
  "updated_by": "admin"
}
```

### Decision Log Endpoints

#### List Decisions
```http
GET /projects/{project_key}/governance/decisions
```

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Decision title",
    "description": "Decision description",
    "decision_date": "2026-01-11T20:00:00Z",
    "decision_maker": "CTO",
    "rationale": "Why this decision was made",
    "impact": "Expected impact",
    "status": "approved",
    "linked_raid_ids": ["raid-uuid-1"],
    "linked_change_requests": [],
    "created_at": "2026-01-11T20:00:00Z",
    "created_by": "admin"
  }
]
```

#### Get Single Decision
```http
GET /projects/{project_key}/governance/decisions/{decision_id}
```

#### Create Decision
```http
POST /projects/{project_key}/governance/decisions
Content-Type: application/json

{
  "title": "Decision title",
  "description": "Decision description",
  "decision_maker": "CTO",
  "rationale": "Rationale for the decision",
  "impact": "Expected impact",
  "status": "approved",
  "linked_raid_ids": [],
  "created_by": "admin"
}
```

#### Link Decision to RAID Item
```http
POST /projects/{project_key}/governance/decisions/{decision_id}/link-raid/{raid_id}
```

## Usage Examples

### Example 1: Setting Up Project Governance

```bash
# 1. Create a project
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "key": "PROJ001",
    "name": "Digital Transformation Project"
  }'

# 2. Create governance metadata
curl -X POST http://localhost:8000/projects/PROJ001/governance/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "objectives": [
      "Modernize legacy systems",
      "Improve customer experience",
      "Reduce operational costs by 30%"
    ],
    "scope": "Full digital transformation of customer-facing systems",
    "stakeholders": [
      {
        "name": "Sarah Johnson",
        "role": "Executive Sponsor",
        "responsibilities": "Strategic direction and funding approval"
      },
      {
        "name": "Mike Chen",
        "role": "Project Manager",
        "responsibilities": "Day-to-day project execution"
      }
    ],
    "decision_rights": {
      "architecture": "Technical Lead",
      "budget": "Executive Sponsor",
      "scope_changes": "Steering Committee"
    },
    "stage_gates": [
      {
        "name": "Requirements Complete",
        "date": "2026-02-15",
        "status": "pending",
        "criteria": "All requirements documented and approved"
      },
      {
        "name": "Design Approved",
        "date": "2026-03-30",
        "status": "pending",
        "criteria": "Architecture and design reviewed by stakeholders"
      }
    ],
    "created_by": "admin"
  }'
```

### Example 2: Recording a Decision

```bash
# Record a significant project decision
curl -X POST http://localhost:8000/projects/PROJ001/governance/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Adopt cloud-native architecture",
    "description": "Migrate from on-premise to AWS cloud infrastructure",
    "decision_maker": "CTO",
    "rationale": "Cloud provides better scalability, reduced maintenance, and faster deployment",
    "impact": "6-month migration timeline, $200K initial investment, $50K/year savings",
    "status": "approved",
    "created_by": "admin"
  }'
```

### Example 3: Querying Governance Data

```bash
# Get current governance metadata
curl http://localhost:8000/projects/PROJ001/governance/metadata

# List all decisions
curl http://localhost:8000/projects/PROJ001/governance/decisions

# Get specific decision
curl http://localhost:8000/projects/PROJ001/governance/decisions/{decision_id}
```

## Data Storage

All governance data is persisted in the project's git repository:

```
projectDocs/
└── {PROJECT_KEY}/
    ├── governance/
    │   ├── metadata.json      # Governance metadata
    │   ├── decisions.json     # Decision log
    │   └── raid_register.json # RAID register (see RAID documentation)
    ├── artifacts/             # Generated artifacts
    └── events/
        └── events.ndjson      # Audit log
```

Each change is committed to git with a descriptive commit message, providing full version history and traceability.

## Audit Trail

All governance operations are logged to the project's audit log:

- `governance_metadata_created` - When governance metadata is first created
- `governance_metadata_updated` - When governance metadata is updated
- `decision_created` - When a decision is logged
- Timestamps and user information are captured for all operations

## Integration with RAID Register

The governance backbone integrates seamlessly with the RAID register:

- Decisions can reference RAID items
- RAID items can reference decisions
- Bidirectional traceability is maintained
- See [RAID Register Documentation](./raid_register.md) for details

## Best Practices

1. **Set Up Governance Early**: Create governance metadata at project inception
2. **Document Key Decisions**: Record all significant architectural, budgetary, and scope decisions
3. **Maintain Traceability**: Link decisions to related RAID items for better visibility
4. **Review Regularly**: Update governance metadata as stakeholders, scope, or decision rights change
5. **Use Stage Gates**: Define clear stage gates with specific approval criteria
6. **Audit Trail**: Leverage the git-based storage for complete change history

## ISO 21500/21502 Alignment

This governance backbone implements key concepts from ISO 21500 and ISO 21502:

- **Project Governance Framework**: Structured approach to governance metadata
- **Decision Making Process**: Formal decision logging with rationale and impact
- **Stakeholder Management**: Comprehensive stakeholder register
- **Authority and Responsibility**: Clear decision rights mapping
- **Stage Gates**: Formal approval checkpoints
- **Traceability**: Links between governance artifacts and project elements
- **Audit Trail**: Complete history of all governance activities

## Security

- All governance data is stored in the project's git repository
- Access control should be implemented at the API level (project-based authorization)
- Sensitive decisions should be documented with appropriate classification
- Audit logs capture user information for accountability

## Future Enhancements

Potential future enhancements include:

- Decision workflow with approval routing
- Automated notifications for stage gate milestones
- Advanced reporting and analytics
- Integration with change management systems
- Role-based access control at the governance level
