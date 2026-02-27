# Issue 449 — UX Slice Migration (Traceability)

## Context

Issue #449 describes client-side navigation/sidebar UX work (a “second slice”):

- keyboard navigation refinements
- advanced ARIA semantics
- focus indicators
- additional responsive polish
- dedicated UI-focused tests

This UI implementation belongs to `blecx/AI-Agent-Framework-Client` (vendored here as `_external/AI-Agent-Framework-Client`), not this backend repository.

## Migration Outcome

- Client follow-up issue created: `blecx/AI-Agent-Framework-Client#243`
- Related baseline client issue: `blecx/AI-Agent-Framework-Client#242` (migrated from backend #448)
- Backend tracking issue to close via this traceability PR: `blecx/AI-Agent-Framework#449`

## Scope

### In scope

- Record the cross-repo handoff for #449.
- Preserve plan → issue → PR traceability in backend history.

### Out of scope

- Any direct UI code changes in this backend repository.

## Acceptance Criteria

- [x] Cross-repo mapping for #449 is documented.
- [x] Backend change remains a single small, reviewable PR.
- [x] No sensitive files committed (`projectDocs/`, `configs/llm.json`).

## Validation

From repository root:

```bash
ls -la docs/issues/issue-449-context.md
git status --short
```
