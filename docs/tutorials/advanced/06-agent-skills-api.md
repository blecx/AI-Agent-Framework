# Agent Skills API (Advanced)

Use cognitive skills endpoints for memory, planning, and learning flows.

## Endpoint summary

Base path (versioned): `/api/v1/agents/{agent_id}`

- `GET /skills`
- `GET /skills/memory?memory_type=<short_term|long_term>`
- `POST /skills/memory`
- `POST /skills/plan`
- `POST /skills/learn`
- `GET /skills/learn/summary`

Legacy equivalents also exist under `/agents/{agent_id}/skills*`, but `/api/v1/*` is preferred.

## 1) List available skills

```bash
curl -s http://localhost:8000/api/v1/agents/demo-agent/skills | jq .
```

## 2) Store memory

```bash
curl -s -X POST http://localhost:8000/api/v1/agents/demo-agent/skills/memory \
  -H "Content-Type: application/json" \
  -d '{
    "memory_type": "short_term",
    "data": {
      "project_key": "AUTO-001",
      "last_action": "generate_plan"
    }
  }' | jq .
```

## 3) Read memory

```bash
curl -s "http://localhost:8000/api/v1/agents/demo-agent/skills/memory?memory_type=short_term" | jq .
```

## 4) Create a plan

```bash
curl -s -X POST http://localhost:8000/api/v1/agents/demo-agent/skills/plan \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Prepare governance baseline for release",
    "constraints": ["2-day timeline", "no schema changes"],
    "context": {"project_key": "AUTO-001"}
  }' | jq .
```

## 5) Log learning event

```bash
curl -s -X POST http://localhost:8000/api/v1/agents/demo-agent/skills/learn \
  -H "Content-Type: application/json" \
  -d '{
    "context": "CI pipeline review",
    "action": "Added command-history checks",
    "outcome": "Reduced regressions",
    "feedback": "Keep checks in smoke suite",
    "tags": ["ci", "quality"]
  }' | jq .
```

## 6) Read learning summary

```bash
curl -s http://localhost:8000/api/v1/agents/demo-agent/skills/learn/summary | jq .
```

## Notes

- `agent_id` is a routing key for agent context.
- For memory calls, `memory_type` should be `short_term` or `long_term`.

---

**Last Updated:** 2026-02-17
