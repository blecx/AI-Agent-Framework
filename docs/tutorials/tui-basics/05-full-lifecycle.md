# Full Lifecycle (Current Surface)

Use TUI for project + command/artifact flow, and REST for workflow state.

## 1) Create project

```bash
python apps/tui/main.py projects create --key TODO-002 --name "Todo Lifecycle"
```

## 2) Propose/apply planning artifacts

```bash
python apps/tui/main.py commands propose --project TODO-002 --command generate_plan
python apps/tui/main.py commands apply --project TODO-002 --proposal <proposal-id>
```

## 3) Inspect artifacts

```bash
python apps/tui/main.py artifacts list --project TODO-002
```

## 4) Check workflow state (REST)

```bash
curl -s http://localhost:8000/projects/TODO-002/workflow/state | jq .
curl -s http://localhost:8000/projects/TODO-002/workflow/allowed-transitions | jq .
```

## 5) Transition workflow state (REST)

```bash
curl -s -X PATCH http://localhost:8000/projects/TODO-002/workflow/state \
  -H "Content-Type: application/json" \
  -d '{"to_state":"planning","actor":"pm","reason":"charter approved"}' | jq .
```

## Notes
- Versioned route equivalents exist under `/api/v1/projects/...`.

---

**Last Updated:** 2026-02-15
