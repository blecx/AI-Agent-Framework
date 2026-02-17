# GUI Workflow States (via API)

Current web app shows a **visual workflow indicator** in the header area.
That control is local UI state.

For persisted workflow-state operations (source of truth), use REST API endpoints below.

## Read workflow state

```bash
curl -s http://localhost:8000/projects/TODO-001/workflow/state | jq .
```

## Read allowed transitions

```bash
curl -s http://localhost:8000/projects/TODO-001/workflow/allowed-transitions | jq .
```

## Transition workflow state

```bash
curl -s -X PATCH http://localhost:8000/projects/TODO-001/workflow/state \
  -H "Content-Type: application/json" \
  -d '{"to_state":"executing","actor":"pm","reason":"planning baseline approved"}' | jq .
```

## Supported states and transitions

- initiating → planning
- planning → executing | initiating
- executing → monitoring | planning
- monitoring → executing | closing
- closing → closed

## Versioned equivalents

- `/api/v1/projects/{project_key}/workflow/state`
- `/api/v1/projects/{project_key}/workflow/allowed-transitions`

## Audit operations (workflow assurance)

### List audit events

```bash
curl -s "http://localhost:8000/projects/TODO-001/audit-events?limit=20" | jq .
```

### Run project audit rules

```bash
curl -s -X POST http://localhost:8000/projects/TODO-001/audit | jq .
```

### Read audit history

```bash
curl -s "http://localhost:8000/projects/TODO-001/audit/history?limit=10" | jq .
```

### Run bulk audit (all projects)

```bash
curl -s -X POST http://localhost:8000/projects/audit/bulk | jq .
```

---

**Last Updated:** 2026-02-16
