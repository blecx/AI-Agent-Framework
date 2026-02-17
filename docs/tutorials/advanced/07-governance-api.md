# Governance API (Advanced)

Use governance endpoints to manage metadata, decision logs, and decision-to-RAID traceability.

## Endpoint summary

Project-scoped base path (versioned): `/api/v1/projects/{project_key}/governance`

- `GET /metadata`
- `POST /metadata`
- `PUT /metadata`
- `GET /decisions`
- `GET /decisions/{decision_id}`
- `POST /decisions`
- `POST /decisions/{decision_id}/link-raid/{raid_id}`

Legacy equivalents also exist under `/projects/{project_key}/governance/*`.

## 1) Create governance metadata

```bash
curl -s -X POST http://localhost:8000/api/v1/projects/GOV-001/governance/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "objectives": ["Deliver MVP", "Maintain audit traceability"],
    "scope": "Governance baseline for release train",
    "stakeholders": [
      {"name": "Alice", "role": "Sponsor", "responsibilities": "Approve stage gates"},
      {"name": "Bob", "role": "PM", "responsibilities": "Coordinate execution"}
    ],
    "decision_rights": {
      "budget_change": "Sponsor",
      "scope_change": "Steering Committee"
    },
    "stage_gates": [
      {"name": "Planning Complete", "criteria": ["Plan approved", "RAID initialized"]}
    ],
    "approvals": [
      {"name": "Go/No-Go", "authority": "Sponsor"}
    ]
  }' | jq .
```

## 2) Read and update metadata

```bash
# Read metadata
curl -s http://localhost:8000/api/v1/projects/GOV-001/governance/metadata | jq .

# Partial update
curl -s -X PUT http://localhost:8000/api/v1/projects/GOV-001/governance/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "Governance baseline for release train (updated)",
    "updated_by": "pm"
  }' | jq .
```

## 3) Create and read decisions

```bash
# Create decision
curl -s -X POST http://localhost:8000/api/v1/projects/GOV-001/governance/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Adopt phased rollout",
    "description": "Release by stage gate with audit checkpoints",
    "decision_maker": "Steering Committee",
    "rationale": "Reduce delivery risk",
    "impact": "Longer lead time, lower failure rate",
    "status": "approved",
    "created_by": "pm"
  }' | jq .

# List decisions
curl -s http://localhost:8000/api/v1/projects/GOV-001/governance/decisions | jq .

# Get one decision
curl -s http://localhost:8000/api/v1/projects/GOV-001/governance/decisions/<decision-id> | jq .
```

## 4) Link decision to RAID item

```bash
curl -s -X POST http://localhost:8000/api/v1/projects/GOV-001/governance/decisions/<decision-id>/link-raid/<raid-id> | jq .
```

## Notes

- Governance endpoints require the project to exist.
- Create metadata once; subsequent changes use `PUT /metadata`.

---

**Last Updated:** 2026-02-17
