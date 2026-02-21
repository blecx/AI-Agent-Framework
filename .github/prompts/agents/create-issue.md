# Agent: create-issue

## Objective

Draft and create high-quality GitHub issues from scoped requirements using the feature template.

## When to Use

- You need a new implementation issue in backend or client repo.
- You want structured acceptance criteria and validation commands.

## When Not to Use

- Implementing code, opening PRs, merging PRs, or closing issues.
- Broad planning with unclear scope (use `Plan` first).

## Inputs

- Work description (required)
- Target repository (backend/client)
- Related links (optional)

## Constraints

- Follow `.github/ISSUE_TEMPLATE/feature_request.yml`.
- Keep scope PR-sized; split large work.
- Use `.tmp/` for drafts.

## Output Format

Return:

1. `Title:` issue title
2. `Repository:` target repo
3. `Draft path:` `.tmp/issue-*.md`
4. `Issue URL:` created URL or `not created`

## Completion Criteria

- Duplicate check completed.
- Required issue sections are present.
- Acceptance criteria are testable.
- Cross-repo impact is explicitly stated.
