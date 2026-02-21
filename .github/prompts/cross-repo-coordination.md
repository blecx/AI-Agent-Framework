# Cross-Repo Change Coordination

## Objective

Coordinate backend and client changes with explicit API contract, sequencing, and rollback plan.

## When to Use

- Backend API changes affect client behavior.
- Work includes breaking changes or coordinated rollout.

## When Not to Use

- Repo-local changes with no downstream contract impact.

## Inputs

- Change description
- Affected repos and owners
- Timeline constraints

## Constraints

- Prefer backward-compatible backend-first sequencing.
- Document API contract before implementation.
- Include rollback strategy for breaking changes.

## Module References

- `modules/cross-repo-coordination-checklist.md`
- `drafting-issue.md`
- `drafting-pr.md`

## Output Format

Return:

1. `Impact Analysis:` backend/client + breaking status
2. `Implementation Order:` phased sequence
3. `Issue Strategy:` backend/client issue links
4. `API Contract:` endpoints and payloads
5. `Validation Plan:` independent + integration checks
6. `Rollback Plan:` fallback and owner

## Completion Criteria

- Cross-repo dependencies are explicit.
- API contract is documented and testable.
- Merge/deployment order is defined.
- Rollback path is documented.
