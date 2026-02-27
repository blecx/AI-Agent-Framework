# Issue 437 — Planning/Spec Split (Traceability)

## Context

This issue is a small “split slice” created to keep manual execution below ~20 minutes.

Split chain:

- #437 (this issue) → parent #434
- #434 → parent #425 (Context7 integration hardening)

The underlying Context7 integration work referenced by #425 is already present in this repository (e.g. `docker-compose.context7.yml`, `docker/context7/Dockerfile`, `scripts/install-context7-systemd.sh`, and `docs/howto/context7-vscode-docker.md`).

## Goal

Create a foundational planning/spec artifact with explicit acceptance criteria so future slices can be kept small, reviewable, and deterministic.

## Scope

### In scope

- Record the “what/where/how to validate” for the Context7 integration track.
- Make follow-up slicing rules explicit (so automation doesn’t need to guess).

### Out of scope

- Any additional Context7 feature work or refactors.
- Any unrelated documentation changes.

## Acceptance Criteria

- [x] Scoped implementation is complete and validated (this doc created; references verified).
- [x] Changes remain within one reviewable PR (single doc addition).
- [x] No sensitive files committed (`projectDocs/`, `configs/llm.json`).

## Validation

From repo root:

```bash
ls -la docker-compose.context7.yml \
  docker/context7/Dockerfile \
  scripts/install-context7-systemd.sh \
  docs/howto/context7-vscode-docker.md
```

Optional runtime verification (if you need to re-check behavior): see the commands documented in `docs/howto/context7-vscode-docker.md`.

## Follow-up slicing rule (for future automation)

If new work is needed under this track, slice by capability and keep each PR small:

1. Docker runtime + endpoint verification
2. Host persistence (systemd helper)
3. VS Code MCP wiring + environment variable support
4. Documentation updates and troubleshooting
