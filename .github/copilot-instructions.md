# Copilot Instructions for AI-Agent-Framework

## Overview
ISO 21500 Project Management AI Agent - Full-stack app with FastAPI (Python 3.10+) + React/Vite. Docker deployment or local venv. ~190MB, 8000+ files. Git-based document storage in `projectDocs/` (separate repo, NEVER commit to code). Two containers: API + web/nginx.

## Build & Setup (ALWAYS follow this sequence)

**Local Dev (5-10 min):**
```bash
./setup.sh  # Auto-detects Python, creates .venv, installs deps (60-90s)
source .venv/bin/activate  # REQUIRED for all Python commands
mkdir -p projectDocs  # MUST exist before API starts
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload  # http://localhost:8000
```

**Frontend (optional, 2-3 min):**
```bash
cd apps/web && npm install  # ~4s
npm run dev  # http://localhost:5173
npm run build  # ~120ms
```

**Docker (2-3 min build):**
```bash
mkdir -p projectDocs  # MUST exist
docker compose up --build  # Web: :8080, API: :8000
```

**Prerequisites:** Python 3.10+ (3.12 tested), Node 20+, Git, Docker 28+ (optional)

## Key Files

**Backend (apps/api/):** main.py (76L, FastAPI app), models.py (69L, Pydantic), services/ (command_service.py 291L, git_manager.py 193L, llm_service.py 94L), routers/ (projects.py 78L, commands.py 71L, artifacts.py 48L). Two requirements.txt: root=dev+test deps, apps/api/=runtime only (Docker).

**Frontend (apps/web/):** package.json (uses rolldown-vite@7.2.5), vite.config.js (proxies /api), src/components/ (ProjectSelector, ProjectView, CommandPanel, ProposalModal, ArtifactsList).

**Config:** configs/llm.default.json (LM Studio default), templates/prompts/iso21500/*.j2 (Jinja2), templates/output/iso21500/*.md (Markdown), docker/ (Dockerfiles + nginx.conf).

**Docs:** README.md (full), QUICKSTART.md, SUMMARY.md, docs/development.md (detailed dev guide).

## Testing & Linting

**No automated tests:** No pytest files, no CI/CD workflows, no .github/workflows/. Manual testing via API docs (/docs) or web UI.

**Linting (optional):** `python -m black apps/api/`, `python -m flake8 apps/api/`, `cd apps/web && npm run lint` (1 warning in ProjectView.jsx is OK).

**Validation:** Test API health (`curl localhost:8000/health`), create project via POST /projects, check git log in projectDocs/, run commands via web UI or API.

## Common Issues

**Setup:** Multiple Python versions detected by setup.sh - choose any 3.10+. Missing python3-venv: `sudo apt install python3.12-venv`. PowerShell restricted: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.

**Runtime:** PROJECT_DOCS_PATH not set - ALWAYS use `PROJECT_DOCS_PATH=../../projectDocs` when running uvicorn from apps/api/. Git fails: configure `git config --global user.email/name`. LLM unavailable: auto-fallback to templates (no error). Ports in use: stop services or edit docker-compose.yml.

**Docker:** "npm error Exit handler never called" during build is HARMLESS, ignore. SSL errors: Dockerfile has --trusted-host flags, try `docker compose build --no-cache`. Missing projectDocs: create before docker compose up.

**Frontend:** ESLint warning in ProjectView.jsx (useEffect deps) is ACCEPTABLE.

## Dependencies

**Python (requirements.txt):** fastapi 0.109.1, uvicorn 0.27.0, pydantic 2.5.3, GitPython 3.1.41, jinja2 3.1.3, openai 1.10.0, pytest 7.4.4, black 24.1.1, flake8 7.0.0. **Important:** Root requirements.txt has dev/test deps; apps/api/requirements.txt has runtime only. Add runtime deps to BOTH, dev deps to root only.

**JS (package.json):** react 19.2.0, vite (rolldown-vite@7.2.5 override), eslint 9.39.1.

**Security:** NEVER commit projectDocs/ or configs/llm.json (.gitignored). Use env vars for secrets. Audit logs store hashes only (default).

## Conventions

**Git:** projectDocs/ is separate repo, auto-initialized by API. Each command = commit `[PROJECT_KEY] Description`. Let API manage projectDocs/, don't modify manually.

**Code:** Backend=no strict style (black/flake8 available), Frontend=modern React hooks. Minimal comments (prefer self-documenting). RESTful API with propose/apply pattern. CORS enabled (configure for prod).

**Env:** PROJECT_DOCS_PATH (required for API), LLM_CONFIG_PATH (defaults /config/llm.json in Docker).

## Quick Command Reference

```bash
# Setup from scratch
./setup.sh && source .venv/bin/activate && mkdir -p projectDocs

# Run API (local dev)
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Run frontend dev server
cd apps/web && npm install && npm run dev

# Build frontend for production
cd apps/web && npm run build

# Docker deployment
mkdir -p projectDocs && docker compose up --build

# Lint code
python -m black apps/api/ && python -m flake8 apps/api/  # Python
cd apps/web && npm run lint  # JavaScript

# Check API health
curl http://localhost:8000/health

# View project docs git log
cd projectDocs && git log --oneline
```

## Trust These Instructions

These instructions have been validated by running all commands in a clean environment. Build times, file locations, and workarounds are accurate as of 2026-01-09. Only search for additional information if:
1. A command fails with an unexpected error not covered above
2. You need to understand implementation details not in this guide
3. Requirements or specifications are unclear from this document

When in doubt, consult README.md, QUICKSTART.md, or docs/development.md for extended details.
