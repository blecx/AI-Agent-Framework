# RAID Register

## Overview

The RAID Register is a comprehensive system for managing **Risks**, **Assumptions**, **Issues**, and **Dependencies** in alignment with ISO 21500/21502 project management standards. It provides structured tracking, prioritization, and mitigation planning for all RAID items throughout the project lifecycle.

## What is RAID?

- **Risks**: Potential events that may negatively impact the project
- **Assumptions**: Factors believed to be true for planning purposes
- **Issues**: Current problems requiring resolution
- **Dependencies**: Reliance on external factors, teams, or deliverables

## Features

### Core RAID Item Attributes

Each RAID item includes:

- **Type**: Risk, Assumption, Issue, or Dependency
- **Title & Description**: Clear identification of the item
- **Status**: Current state (open, in_progress, mitigated, closed, accepted)
- **Owner**: Person responsible for managing the item
- **Priority**: Severity level (critical, high, medium, low)
- **Impact & Likelihood**: Risk assessment (for risks)
- **Mitigation Plan**: Strategy for addressing the item
- **Next Actions**: Specific steps to be taken
- **Traceability**: Links to governance decisions and change requests
- **Audit Trail**: Creation and update timestamps with user tracking
- **Target Resolution Date**: Expected resolution date

### Filtering & Querying

The RAID register supports filtering by:

- RAID type (risk, assumption, issue, dependency)
- Status (open, in_progress, mitigated, closed, accepted)
- Owner (person responsible)
- Priority (critical, high, medium, low)

### Traceability

Full bidirectional traceability:

- Link RAID items to governance decisions
- Link governance decisions to RAID items
- Query RAID items by linked decision
- Track relationships over time

## API Reference

### List RAID Items

```http
GET /projects/{project_key}/raid
```

Query Parameters:
- `type` (optional): Filter by RAID type (risk, assumption, issue, dependency)
- `status` (optional): Filter by status (open, in_progress, mitigated, closed, accepted)
- `owner` (optional): Filter by owner name
- `priority` (optional): Filter by priority (critical, high, medium, low)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "type": "risk",
      "title": "Database migration complexity",
      "description": "Migration may encounter data integrity issues",
      "status": "open",
      "owner": "Jane Smith",
      "priority": "high",
      "impact": "high",
      "likelihood": "possible",
      "mitigation_plan": "Comprehensive testing and rollback strategy",
      "next_actions": [
        "Create test environment",
        "Document rollback procedure"
      ],
      "linked_decisions": ["decision-uuid"],
      "linked_change_requests": [],
      "created_at": "2026-01-11T20:00:00Z",
      "updated_at": "2026-01-11T20:00:00Z",
      "created_by": "admin",
      "updated_by": "admin",
      "target_resolution_date": "2026-02-15"
    }
  ],
  "total": 1,
  "filtered_by": {
    "type": "risk",
    "status": null,
    "owner": null,
    "priority": null
  }
}
```

### Get Single RAID Item

```http
GET /projects/{project_key}/raid/{raid_id}
```

### Create RAID Item

```http
POST /projects/{project_key}/raid
Content-Type: application/json

{
  "type": "risk",
  "title": "Security vulnerability in third-party library",
  "description": "Critical CVE identified in authentication library",
  "owner": "Security Team",
  "priority": "critical",
  "impact": "very_high",
  "likelihood": "likely",
  "mitigation_plan": "Update library to patched version immediately",
  "next_actions": [
    "Identify compatible version",
    "Test with staging environment",
    "Deploy to production"
  ],
  "created_by": "admin",
  "target_resolution_date": "2026-01-20"
}
```

### Update RAID Item

```http
PUT /projects/{project_key}/raid/{raid_id}
Content-Type: application/json

{
  "status": "in_progress",
  "next_actions": ["Deploy patch to production", "Monitor for issues"],
  "updated_by": "admin"
}
```

### Delete RAID Item

```http
DELETE /projects/{project_key}/raid/{raid_id}
```

### Link RAID Item to Decision

```http
POST /projects/{project_key}/raid/{raid_id}/link-decision/{decision_id}
```

### Get RAID Items by Decision

```http
GET /projects/{project_key}/raid/by-decision/{decision_id}
```

## Enumerations

### RAID Type

- `risk` - Potential negative event
- `assumption` - Factor assumed to be true
- `issue` - Current problem
- `dependency` - External reliance

### Status

- `open` - Newly identified, not yet addressed
- `in_progress` - Currently being worked on
- `mitigated` - Risk reduced to acceptable level
- `closed` - Resolved or no longer applicable
- `accepted` - Risk accepted, no mitigation planned

### Priority

- `critical` - Immediate attention required
- `high` - High importance
- `medium` - Moderate importance
- `low` - Low importance

### Impact Level (for Risks)

- `very_high` - Severe impact on project success
- `high` - Significant impact
- `medium` - Moderate impact
- `low` - Minor impact
- `very_low` - Negligible impact

### Likelihood (for Risks)

- `very_likely` - Almost certain to occur (>80%)
- `likely` - Probable (60-80%)
- `possible` - May occur (40-60%)
- `unlikely` - Improbable (20-40%)
- `very_unlikely` - Rare (<20%)

## Usage Examples

### Example 1: Managing a Critical Risk

```bash
# 1. Identify and create the risk
RISK_RESPONSE=$(curl -s -X POST http://localhost:8000/projects/PROJ001/raid \
  -H "Content-Type: application/json" \
  -d '{
    "type": "risk",
    "title": "Key team member resignation risk",
    "description": "Lead architect may leave due to competing offer",
    "owner": "HR Manager",
    "priority": "critical",
    "impact": "very_high",
    "likelihood": "possible",
    "mitigation_plan": "Cross-training, knowledge transfer sessions, retention bonus",
    "next_actions": [
      "Schedule knowledge transfer sessions",
      "Identify backup architect",
      "Discuss retention package with HR"
    ],
    "created_by": "pm_sarah",
    "target_resolution_date": "2026-01-30"
  }')

RISK_ID=$(echo $RISK_RESPONSE | jq -r '.id')

# 2. Update as mitigation progresses
curl -X PUT http://localhost:8000/projects/PROJ001/raid/$RISK_ID \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "next_actions": [
      "Retention package approved",
      "Knowledge transfer 60% complete",
      "Backup architect identified"
    ],
    "updated_by": "pm_sarah"
  }'

# 3. Close when resolved
curl -X PUT http://localhost:8000/projects/PROJ001/raid/$RISK_ID \
  -H "Content-Type: application/json" \
  -d '{
    "status": "closed",
    "mitigation_plan": "Retention package accepted. Knowledge fully transferred.",
    "updated_by": "pm_sarah"
  }'
```

### Example 2: Tracking an Issue

```bash
# Create an issue
curl -X POST http://localhost:8000/projects/PROJ001/raid \
  -H "Content-Type: application/json" \
  -d '{
    "type": "issue",
    "title": "Production deployment failed",
    "description": "Latest release failed to deploy due to configuration error",
    "owner": "DevOps Lead",
    "priority": "critical",
    "mitigation_plan": "Rollback to previous version, fix configuration, redeploy",
    "next_actions": [
      "Rollback completed",
      "Root cause analysis in progress",
      "Configuration fix being tested"
    ],
    "created_by": "devops_mike",
    "target_resolution_date": "2026-01-12"
  }'
```

### Example 3: Managing Dependencies

```bash
# Track an external dependency
curl -X POST http://localhost:8000/projects/PROJ001/raid \
  -H "Content-Type: application/json" \
  -d '{
    "type": "dependency",
    "title": "API integration dependent on vendor timeline",
    "description": "Payment gateway integration requires vendor to complete API v2",
    "owner": "Integration Lead",
    "priority": "high",
    "mitigation_plan": "Weekly check-ins with vendor, fallback to API v1 if delayed",
    "next_actions": [
      "Schedule vendor status meeting",
      "Document API v1 fallback approach",
      "Update project timeline if needed"
    ],
    "created_by": "integration_alex",
    "target_resolution_date": "2026-02-28"
  }'
```

### Example 4: Filtering RAID Items

```bash
# Get all critical items
curl "http://localhost:8000/projects/PROJ001/raid?priority=critical"

# Get all open risks
curl "http://localhost:8000/projects/PROJ001/raid?type=risk&status=open"

# Get all items owned by a specific person
curl "http://localhost:8000/projects/PROJ001/raid?owner=Jane%20Smith"

# Get all in-progress issues
curl "http://localhost:8000/projects/PROJ001/raid?type=issue&status=in_progress"
```

### Example 5: Linking to Governance Decisions

```bash
# Create a decision to address a risk
DECISION_RESPONSE=$(curl -s -X POST http://localhost:8000/projects/PROJ001/governance/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Approve additional security resources",
    "description": "Add 2 security engineers to address vulnerability risk",
    "decision_maker": "CTO",
    "rationale": "Critical security risks require dedicated resources",
    "impact": "Budget increase of $300K",
    "status": "approved",
    "created_by": "admin"
  }')

DECISION_ID=$(echo $DECISION_RESPONSE | jq -r '.id')

# Link the decision to the risk
curl -X POST "http://localhost:8000/projects/PROJ001/raid/$RISK_ID/link-decision/$DECISION_ID"

# Get all RAID items linked to this decision
curl "http://localhost:8000/projects/PROJ001/raid/by-decision/$DECISION_ID"
```

## Data Storage

RAID register data is stored in the project's git repository:

```
projectDocs/
└── {PROJECT_KEY}/
    └── governance/
        └── raid_register.json  # All RAID items
```

Each RAID operation is committed to git with a descriptive message:

- Create: `[{PROJECT_KEY}] Add {type}: {title}`
- Update: `[{PROJECT_KEY}] Update {type}: {title}`
- Delete: `[{PROJECT_KEY}] Delete {type}: {title}`
- Link: `[{PROJECT_KEY}] Link RAID {raid_id} to decision {decision_id}`

## Audit Trail

All RAID operations are logged to the project's audit log:

- `raid_item_created` - When a RAID item is created
- `raid_item_updated` - When a RAID item is updated
- `raid_item_deleted` - When a RAID item is deleted
- Timestamps and user information are captured for all operations

## Integration with Governance

The RAID register integrates with the governance backbone:

- Link RAID items to governance decisions
- Track which decisions address which risks/issues
- Maintain bidirectional traceability
- See [Governance Documentation](./governance.md) for details

## Best Practices

### Risk Management

1. **Assess Impact & Likelihood**: Always provide realistic assessments
2. **Proactive Mitigation**: Don't wait for risks to materialize
3. **Regular Review**: Review risks weekly or at project milestones
4. **Escalation**: Escalate critical/high risks immediately
5. **Documentation**: Keep mitigation plans specific and actionable

### Issue Management

1. **Immediate Response**: Create issues as soon as problems arise
2. **Root Cause Analysis**: Document root causes in description
3. **Clear Ownership**: Assign a specific owner for each issue
4. **Progress Tracking**: Update status and next actions regularly
5. **Lessons Learned**: Document resolution for future reference

### Assumption Management

1. **Validate Early**: Test assumptions as soon as possible
2. **Track Changes**: Update status when assumptions prove false
3. **Impact Analysis**: Document what happens if assumption is invalid
4. **Regular Review**: Review assumptions at each stage gate

### Dependency Management

1. **External Dependencies**: Track all dependencies on external teams/vendors
2. **Communication**: Maintain regular contact with dependency owners
3. **Contingency Plans**: Have fallback options for critical dependencies
4. **Timeline Impact**: Update project timeline if dependencies slip

## Risk Matrix

Use this matrix to assess risk priority based on impact and likelihood:

|            | Very Unlikely | Unlikely | Possible | Likely | Very Likely |
|------------|--------------|----------|----------|--------|-------------|
| Very High  | Medium       | High     | High     | Critical | Critical  |
| High       | Low          | Medium   | High     | High   | Critical    |
| Medium     | Low          | Low      | Medium   | High   | High        |
| Low        | Low          | Low      | Low      | Medium | Medium      |
| Very Low   | Low          | Low      | Low      | Low    | Low         |

## ISO 21500/21502 Alignment

The RAID register implements concepts from ISO 21500 and ISO 21502:

- **Risk Management**: Structured risk identification, assessment, and mitigation
- **Issue Management**: Formal issue tracking and resolution
- **Assumption Management**: Documentation and validation of project assumptions
- **Dependency Management**: Tracking external dependencies
- **Traceability**: Links between RAID items and governance decisions
- **Audit Trail**: Complete history of all RAID activities
- **Owner Assignment**: Clear accountability for each item

## Reporting & Analytics

To generate RAID reports:

```bash
# Get all critical and high priority items
curl "http://localhost:8000/projects/PROJ001/raid?priority=critical" > critical_items.json
curl "http://localhost:8000/projects/PROJ001/raid?priority=high" > high_priority_items.json

# Get all open risks
curl "http://localhost:8000/projects/PROJ001/raid?type=risk&status=open" > open_risks.json

# Get all in-progress items
curl "http://localhost:8000/projects/PROJ001/raid?status=in_progress" > in_progress.json
```

Process the JSON output with tools like `jq` for custom reporting.

## Future Enhancements

Potential future enhancements include:

- Risk probability calculations and scoring
- Automated risk escalation based on priority
- Risk heatmap visualization
- RAID item aging alerts
- Integration with notification systems
- Bulk import/export functionality
- Custom fields and categories
- Advanced filtering and search
- Risk burndown charts
- Dependency graph visualization
