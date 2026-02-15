# Automation and Scripting

Build scripts around the currently supported surfaces.

## Supported automation targets
- TUI: `projects create/list/get`, `commands propose/apply`, `artifacts list/get`, `health`
- REST: RAID CRUD + workflow state/allowed-transitions

## Example script snippets

```bash
# Create project
python apps/tui/main.py projects create --key AUTO-001 --name "Automation Demo"

# Propose/apply plan
python apps/tui/main.py commands propose --project AUTO-001 --command generate_plan
python apps/tui/main.py commands apply --project AUTO-001 --proposal <proposal-id>

# List artifacts
python apps/tui/main.py artifacts list --project AUTO-001

# Workflow state transition via REST
curl -s -X PATCH http://localhost:8000/projects/AUTO-001/workflow/state \
  -H "Content-Type: application/json" \
  -d '{"to_state":"executing","actor":"bot","reason":"pipeline gate passed"}' | jq .
```

## CI note
For new integrations, prefer `/api/v1/*` endpoints in scripts.

---

**Last Updated:** 2026-02-15
