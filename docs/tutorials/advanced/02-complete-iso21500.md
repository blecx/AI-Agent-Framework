# Complete ISO 21500 Tutorial (Current Platform Mapping)

This advanced guide maps ISO lifecycle phases to **currently available** surfaces.

## Phase mapping
- **Initiating / Planning / Executing / Monitoring / Closing**
- Use TUI `commands propose/apply` for generated project outputs.
- Use REST workflow endpoints for phase state transitions.
- Use REST RAID endpoints for risks/issues/assumptions/dependencies.

## Minimal end-to-end run

```bash
# Create project
python apps/tui/main.py projects create --key ISO-001 --name "ISO Lifecycle"

# Generate plan and apply
python apps/tui/main.py commands propose --project ISO-001 --command generate_plan
python apps/tui/main.py commands apply --project ISO-001 --proposal <proposal-id>

# Workflow state
curl -s http://localhost:8000/projects/ISO-001/workflow/state | jq .
curl -s -X PATCH http://localhost:8000/projects/ISO-001/workflow/state \
  -H "Content-Type: application/json" \
  -d '{"to_state":"planning","actor":"pm","reason":"approved"}' | jq .

# RAID
curl -s -X POST http://localhost:8000/projects/ISO-001/raid \
  -H "Content-Type: application/json" \
  -d '{"type":"risk","title":"scope drift","description":"scope may expand","priority":"medium","status":"open","owner":"pm"}' | jq .
```

## Versioning note
Prefer `/api/v1/*` routes for new automation, while legacy routes still work.

---

**Last Updated:** 2026-02-15
