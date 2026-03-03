<skill>
<name>cross-repo-coordination-checklist</name>
<description>Workflow or rule module extracted from .github/prompts/modules/cross-repo-coordination-checklist.md</description>
<file>
# Cross-Repo Coordination Checklist (Module)

## Analysis

- Backend impact
- Frontend impact
- Breaking change status
- Compatibility strategy

## Delivery Order

1. Backend contract work (prefer backward compatible).
2. Client integration update.
3. Coordinated enforcement/deprecation (if breaking).

## Required Artifacts

- Explicit API contract (request/response/errors)
- Linked backend + client issues
- Validation plan for isolated and integrated testing
- Rollback strategy

</file>
</skill>