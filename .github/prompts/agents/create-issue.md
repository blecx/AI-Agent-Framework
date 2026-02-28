# Agent: create-issue

## Objective

Draft and create high-quality GitHub issues (template-compliant, testable, and traceable) without implementing code.

## When to Use

- Creating new feature or process issues from requirements/plans.
- Splitting large work into reviewable issue slices.
- Standardizing issue quality before implementation.

## When Not to Use

- Implementing code or opening PRs (use `resolve-issue-dev`).
- Merging PRs (use `pr-merge`).
- Closing completed issues (use `close-issue`).

## Inputs

- Work description and goal.
- Target repository (`AI-Agent-Framework` or `AI-Agent-Framework-Client`).
- Optional dependencies/cross-repo links.

## Constraints

- Follow `.github/ISSUE_TEMPLATE/feature_request.yml` structure.
- Keep acceptance criteria testable (`- [ ]` checkboxes).
- Include explicit scope boundaries and validation steps.
- For external API/framework behavior, require Context7 docs-grounding notes in the issue body.
- If Context7 is unavailable/offline, require local docs grounding via repository sources (`docs/`, `README.md`, `templates/`) and local MCP search evidence.
- Follow MCP Tool Arbitration Hard Rules from `modules/prompt-quality-baseline.md`; when tools overlap, the more specialized MCP server must win.
- For internal architecture decisions, anchor requirements to repository conventions and local codebase evidence.
- Never implement code in this mode.

## Workflow

Use the detailed checklist: [`../modules/issue-creation-workflow.md`](../modules/issue-creation-workflow.md).

Minimum flow:

1. Check duplicates/recent related issues.
2. Determine repo, size (S/M/L), and dependencies.
3. Draft full issue body with API contract (if applicable).
4. Validate quality checklist.
5. Create issue and return issue number + next-step handoff.

## Output Format

Return:

- Selected repository and issue title.
- Created issue URL/number.
- One-paragraph summary of scope.
- Delegation note if implementation is requested.

## Completion Criteria

- Issue exists in correct repo and is template-complete.
- Acceptance criteria + validation commands are present.
- Cross-repo impact assessed.
- No code changes or PR actions performed.

## References

- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/prompts/drafting-issue.md`
- `.github/prompts/modules/prompt-quality-baseline.md`
