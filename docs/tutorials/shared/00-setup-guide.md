# Tutorial Setup Guide

## Prerequisites
- Docker + Docker Compose
- Git
- Browser

## Docker-first setup (recommended)

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
mkdir -p projectDocs
docker compose up -d
curl http://localhost:8000/health
```

Open:
- Docker UI: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`

## Local development setup (optional)

```bash
./setup.sh
source .venv/bin/activate
mkdir -p projectDocs

cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

In another terminal:

```bash
cd apps/web
npm install
npm run dev
```

Local UI URL: `http://localhost:5173`

## Verify TUI surface

```bash
python apps/tui/main.py --help
python apps/tui/main.py projects --help
python apps/tui/main.py commands --help
python apps/tui/main.py artifacts --help
```

Expected command groups: `projects`, `commands`, `artifacts`, `config`, `health`.

---

**Last Updated:** 2026-02-15
