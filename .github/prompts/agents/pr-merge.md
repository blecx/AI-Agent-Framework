# Agent: pr-merge

## Objective

Merge a ready PR safely, close linked issue(s), and perform mandatory cleanup.

## When to Use

- PR is approved and merge-ready.
- You need standardized merge + close + cleanup flow.

## When Not to Use

- Creating/fixing PR content (`resolve-issue-dev`).
- Drafting new issues (`create-issue`).

## Inputs

- `pr_number` (required)
- Linked issue number (optional)

## Constraints

- Do not fix PR content in this flow.
- Prefer squash merge with branch deletion.
- Use `.tmp/` cleanup after merge.

## Output Format

Return:

1. `PR:` merged/not merged + URL
2. `Issue:` closed/not closed + number
3. `Merge SHA:` value or `n/a`
4. `Cleanup:` verified/not verified

## Completion Criteria

- PR is merged.
- Linked issue is closed (or auto-closed confirmed).
- Relevant `.tmp` files are removed.
- Local `main` is updated.

## Completion Criteria

- Requirements, coverage, and roadmap artifacts are defined.
- Issue slices are independently reviewable.
- Cross-repo coordination is explicit.
- Validation approach is concrete and runnable.
