# Issue 442 — Planning/Spec Split (Traceability)

## Context

Issue #442 is a split slice under parent #440 to keep manual execution below ~20 minutes.

Parent chain:

- #442 (this slice) → parent #440
- #440 → parent #437

Parent #440’s scope is UI-focused (“sidebar” grouping/order + type/state visual distinction).

This repository is the backend; the UI implementation for this chain lives in the client repo (vendored here as `_external/AI-Agent-Framework-Client`). This slice records a small, deterministic planning/spec artifact so follow-up slices stay reviewable and automation doesn’t need to guess.

## Goal

Create a foundational planning/spec artifact with explicit acceptance criteria and validation framing for this split slice.

## Scope

### In scope

- Record goal, boundaries, and acceptance criteria for issue #442.
- Define minimal validation commands and hygiene checks for this slice.
- Keep the implementation to one small documentation/process artifact.

### Out of scope

- Any backend feature code changes (API, services, domain models, routers).
- Any frontend/client repository changes (those belong in `blecx/AI-Agent-Framework-Client`).
- Any unrelated documentation or workflow refactoring.

## Acceptance Criteria

- [x] Scoped implementation is complete and validated (this artifact exists and is verifiable).
- [x] Changes remain within one reviewable PR (single-file docs/process change).
- [x] No sensitive files committed (`projectDocs/`, `configs/llm.json`).

## Validation

From repository root:

```bash
ls -la docs/issues/issue-442-context.md
ls -la _external/AI-Agent-Framework-Client/client/src/components/AppNavigation.tsx
git status --short
```

## Follow-up slicing guidance

For future split slices in this chain, keep each PR narrowly scoped to one concern, and prefer doing UI work in the client repo:

1. Sidebar navigation grouping/order refactor (client)
2. Type/state visual distinction update + basic visual confirmation (client)
3. Cross-repo traceability notes (backend only, when needed)

