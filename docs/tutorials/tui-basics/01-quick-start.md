# TUI Quick Start

Use the current TUI safely and quickly.

## 1) Start services

```bash
mkdir -p projectDocs
docker compose up -d
curl http://localhost:8000/health
```

## 2) Inspect available commands

```bash
python apps/tui/main.py --help
```

Current groups:

- `projects` (`create`, `list`, `get`)
- `commands` (`propose`, `apply`)
- `artifacts` (`list`, `get`)
- `config`
- `health`

## 3) Know what is TUI vs REST

The current TUI does **not** expose `raid` or `workflow` groups.
Use REST endpoints for those capabilities:

- RAID: `/projects/{project_key}/raid`
- Workflow state: `/projects/{project_key}/workflow/state`
- Allowed transitions: `/projects/{project_key}/workflow/allowed-transitions`

Versioned equivalents are available under `/api/v1/projects/{project_key}/...`.

## 4) Run health check

```bash
python apps/tui/main.py health
```

## 5) List projects

```bash
python apps/tui/main.py projects list
```

---

**Last Updated:** 2026-02-16
