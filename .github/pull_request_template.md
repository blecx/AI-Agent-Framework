# Pull Request

## Goal / Context

- Links: Fixes #\_\_\_
- Related client repo (if relevant): blecx/AI-Agent-Framework-Client#\_\_\_
- Scope (what’s included / excluded):

## Acceptance Criteria (copy from the issue)

- [ ] AC1:
- [ ] AC2:
- [ ] AC3:

## Implementation Notes

- Key design choices:
- API changes (endpoints/contracts): yes/no (details)
- Cross-repo impact: none / client update required (details)

## Validation Evidence

Backend:

- [ ] `./setup.sh && source .venv/bin/activate`
- [ ] `python -m black apps/api/`
- [ ] `python -m flake8 apps/api/`
- [ ] `pytest`
- [ ] `cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload`
- [ ] `curl http://localhost:8000/health`

Frontend (if changed):

- [ ] `cd apps/web && npm install`
- [ ] `npm run lint`
- [ ] `npm run build`

Docker (if changed):

- [ ] `docker compose build`
- [ ] `docker compose up`

## Repo Hygiene / Safety

- [ ] `projectDocs/` is NOT committed
- [ ] `configs/llm.json` is NOT committed
- [ ] No secrets in code/logs

## Screenshots / Logs (if relevant)
