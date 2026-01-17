# 2026-01-17 — AI-Agent-Framework / Client PR Process, CI Gates, Docs + ADRs

**Date:** 2026-01-17  
**Status:** Draft (Reviewed for repo hygiene; not redacted)  
**Participants:** blecx (maintainer), GitHub Copilot (coding agent)  
**Scope:** Backend (AI-Agent-Framework) + Client (AI-Agent-Framework-Client) PR review process + CI enforcement + cross-repo API integration + documentation

---

## Context

Goal: establish a reusable, deterministic PR review process that works for both humans and agents, and that enforces (a) coding standards and (b) proof the requested feature is actually implemented.

Constraints / requirements:

- Must apply to BOTH repositories:
  - Backend: AI-Agent-Framework (FastAPI/Python)
  - Client: AI-Agent-Framework-Client (React/TypeScript/Vite)
- Client CI must be able to validate against a running backend API (Docker-based).
- Python baseline standardized to 3.12.
- Repo hygiene must prevent committing sensitive/local-only files (e.g., backend `projectDocs/`, `configs/llm.json`, client `.env*`).

---

## High-level outcomes

- Implemented a 3-layer PR quality system:
  1. PR template “contract” (goal/AC/validation/hygiene)
  2. CI PR-body gate enforcing that contract
  3. A structured review rubric prompt for human/agent reviewers

- Added cross-repo API integration validation:
  - Backend provides a reusable GitHub Actions workflow that checks out and starts the backend via Docker Compose and then runs client tests.
  - Client CI calls the reusable workflow for deterministic smoke validation.

- Standardized Python version to 3.12 across setup docs/scripts.

- Brought backend codebase to a clean `black` + `flake8` state and verified tests.

---

## Key implementation pieces (Backend: AI-Agent-Framework)

### Backend PR review gate and hygiene

- CI enforces PR description structure and checked items.
- Hygiene guard ensures forbidden files are not committed (notably `projectDocs/` and `configs/llm.json`).

### Reusable workflow (client API integration)

- Added/updated backend reusable workflow used by client CI.
- Hardened it to ensure the `projectDocs/` bind-mount directory exists before starting Docker Compose.

### Backend documentation

- Updated development docs to reflect Python 3.12 requirement and CI-equivalent commands.
- Added ADRs documenting:
  - CI PR review gate enforcement
  - reusable client API integration workflow

---

## Key implementation pieces (Client: AI-Agent-Framework-Client)

### Client PR review gate and hygiene

- Client CI includes a PR description gate implemented via `actions/github-script`.
- Hygiene guard prevents committing real `.env*` files (examples allowed).

### API smoke tests

- Added deterministic API smoke test script runnable via `npm run test:api`.
- Enhanced smoke checks to validate:
  - `/health`
  - `/api/v1/health`
  - `/api/v1/projects` returns a JSON array

### Integration job

- Client CI calls the backend reusable workflow for API integration.
- Path filtering limits integration runs to relevant changes.

### Client documentation

- Updated client dev/testing docs to reflect PR gate expectations and API smoke checks.
- Note: client `main` is protected; changes land via PR branch.

---

## Notable robustness fixes during the session

- Tightened PR gate placeholder detection and checkbox parsing.
- Ensured the backend reusable workflow creates required bind-mount directories.
- Corrected docs commands to match real repo structure and env vars (especially `PROJECT_DOCS_PATH`).
- Added/confirmed unit test coverage on the client side when `client/scripts/**` changes (to satisfy client PR gate).

---

## Validation snapshot (as performed in the environment)

Backend (AI-Agent-Framework):

- `python -m flake8 apps/api` (passed)
- `python -m black apps/api --check` (passed)
- `python -m pytest -q` (passed; 286 tests)

Client (AI-Agent-Framework-Client):

- Local `npm` execution was not available in this environment, so lint/build/test evidence is expected to come from CI checks.

---

## Branching / sync notes

- Backend: changes were pushed to `origin/main`.
- Client: `main` is protected; changes were pushed to a PR branch `copilot/sync-ci-gaps-2026-01-17`.

---

## Related ADRs

- ADR-0005: Enforce PR Review Gate in CI
- ADR-0006: Reusable Workflow for Client API Integration Tests

---

## Next steps (if desired)

- Open/finish the client PR from `copilot/sync-ci-gaps-2026-01-17` and ensure CI passes.
- Optionally add a short “Docs index” entry referencing ADR-0005/0006 and this transcript.

---

## Document metadata

**Transcript ID:** 2026-01-17-pr-process-ci-gates-docs-adrs  
**Created:** 2026-01-17  
**Format:** Markdown  
**Classification:** Internal  
**Review status:** Draft
