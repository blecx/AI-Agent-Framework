# Issue 444 — Final Split Slice & Documentation Updates (Traceability)

## Context

Issue #444 is the remaining split slice under parent issue #440.

Chain:

- #444 (this slice) → parent #440
- #440 was previously split into #442 (planning/spec) and #443 (execution slice)

Issue #443 implemented split-step derivation behavior in `scripts/work_issue_split.py` and wiring in `scripts/work-issue.py`.
This slice finalizes the chain by documenting the resulting behavior in workflow guidance.

## Goal

Finalize remaining slice scope by updating backend workflow documentation to match implemented split behavior and preserve deterministic operator guidance.

## Scope

### In scope

- Add explicit split-step derivation order to workflow docs.
- Document filtering and persistence behavior for split issue draft generation.
- Keep this slice as a small, reviewable backend docs-only change.

### Out of scope

- Additional feature code changes in split generation/runtime.
- Client repo UX work (not applicable for this backend doc slice).
- Unrelated documentation refactors.

## Acceptance Criteria

- [x] Scoped implementation is complete and validated.
- [x] Changes remain within one reviewable PR.
- [x] No sensitive files committed (`projectDocs/`, `configs/llm.json`).

## Validation

From repository root:

```bash
python -m black apps/api/ --check
python -m flake8 apps/api/
python -m pytest -q
```

## Outcome

- `docs/WORK-ISSUE-WORKFLOW.md` now documents deterministic split-step derivation order and split draft behavior.
- This context file records #444 scope, boundaries, and validation framing for traceability.
