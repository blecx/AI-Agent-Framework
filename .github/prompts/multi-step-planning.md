# Multi-Step Planning Procedure

## Objective

Create a concise, execution-ready plan for complex multi-issue work while preserving traceability (Plan → Issues → PRs).

## When to Use

- Work spans multiple weeks or domains.
- You need coordinated backend/client issue batches.
- Requirements need explicit coverage mapping.

## When Not to Use

- Small single-PR features (use `planning-feature.md`).
- One-off bugfixes that do not need phased planning.

## Inputs

- Step name/goal
- Scope boundaries and constraints
- Relevant prior docs/issues

## Constraints

- Keep output modular and reviewable.
- Each issue should remain PR-sized where possible.
- Include validation commands and ownership order.

## Workflow

Use detailed checklist: [`modules/multi-step-planning-checklist.md`](modules/multi-step-planning-checklist.md).

Minimum outputs:

1. Requirements spec
2. Coverage matrix
3. Implementation roadmap
4. Linked issue batch list

## Output Format

Return:

- Plan summary (goal, scope, AC)
- Generated planning file paths
- Issue list with ordering/dependencies
- Validation checklist

## Completion Criteria

- Requirements are fully mapped to issues.
- Dependencies and execution order are explicit.
- Validation commands and acceptance criteria are testable.
- Plan is ready for direct implementation handoff.

## References

- `.github/prompts/modules/multi-step-planning-checklist.md`
- `.github/prompts/modules/prompt-quality-baseline.md`
- `.github/prompts/planning-feature.md`
