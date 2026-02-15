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

---

**Last Updated:** 2026-02-15
