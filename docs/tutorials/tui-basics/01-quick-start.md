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

## 3) Run health check

```bash
python apps/tui/main.py health
```

## 4) List projects

```bash
python apps/tui/main.py projects list
```

---

**Last Updated:** 2026-02-15
