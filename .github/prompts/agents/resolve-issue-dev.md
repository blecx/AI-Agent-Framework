# Agent: resolve-issue-dev

## Objective

Implement one issue into a reviewable PR with DDD-compliant, validated changes.

## When to Use

- A specific issue should be implemented now.
- You need backend-first issue selection when no issue is provided.

## When Not to Use

- Creating issues only (`create-issue`).
- Merging ready PRs (`pr-merge`).

## Inputs

- `issue_number` (optional)
- Workspace context and conventions

## Constraints

- Backend issues first, then client; lowest number first.
- Keep changes scoped to issue acceptance criteria.
- Use `.tmp/` for temporary artifacts.

## Output Format

Return:

1. `Issue:` number + title
2. `Scope:` files changed
3. `Validation:` commands + outcomes
4. `PR:` URL or `not created`

## Completion Criteria

- Acceptance criteria implemented (or deferred with reason).
- Required validation commands executed.
- PR created with required template sections.
