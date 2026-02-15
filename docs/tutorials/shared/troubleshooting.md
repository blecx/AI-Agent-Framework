# Tutorial Troubleshooting Guide

## Fast checks

```bash
docker compose ps
curl http://localhost:8000/health
python apps/tui/main.py health
```

## Common command-surface confusion

### “`main.py raid` not found”
Expected: current TUI has no `raid` command group.

Use REST instead:
- `GET/POST/PUT/DELETE /projects/{project_key}/raid`
- or `/api/v1/projects/{project_key}/raid`

### “`main.py workflow` not found”
Expected: current TUI has no workflow command group.

Use REST instead:
- `GET/PATCH /projects/{project_key}/workflow/state`
- `GET /projects/{project_key}/workflow/allowed-transitions`
- or `/api/v1/...` equivalents

### “`main.py propose` not found”
Use:
- `python apps/tui/main.py commands propose ...`
- `python apps/tui/main.py commands apply ...`

## Current TUI groups
- `projects` (`create`, `list`, `get`)
- `commands` (`propose`, `apply`)
- `artifacts` (`list`, `get`)
- `config`
- `health`

## Web URLs
- Docker web UI: `http://localhost:8080`
- Local dev web UI: `http://localhost:5173`

---

**Last Updated:** 2026-02-16
