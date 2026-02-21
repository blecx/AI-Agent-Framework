# Multi-Step Planning Procedure

## Objective

Plan multi-week, cross-domain initiatives into reviewable issues and traceable implementation phases.

## When to Use

- Initiative spans multiple domains/repos or requires 6+ issues.
- You need a requirements → coverage → roadmap planning set.

## When Not to Use

- Small features that fit 1-4 issues (use `planning-feature.md`).
- Pure bug fix with no cross-repo dependency.

## Inputs

- Step identifier and goal
- Prior step artifacts (if any)
- Repositories involved (backend/client)

## Constraints

- Follow DDD boundaries and backend-first dependency ordering.
- Keep issue slices PR-sized and testable.
- Use `.tmp/` for generated drafts.

## Module References

- `modules/prompt-quality-baseline.md`
- `modules/multi-step-planning-phases.md`
- `modules/multi-step-planning-checklist.md`

## Output Format

Return:

1. `Plan Summary:` goal + scope + non-goals
2. `Issue Breakdown:` backend first, then client
3. `Traceability:` requirements → issues mapping
4. `Validation Commands:` exact commands
5. `Risks/Dependencies:` blockers and sequencing

## Completion Criteria

- Requirements, coverage, and roadmap artifacts are defined.
- Issue slices are independently reviewable.
- Cross-repo coordination is explicit.
- Validation approach is concrete and runnable.
