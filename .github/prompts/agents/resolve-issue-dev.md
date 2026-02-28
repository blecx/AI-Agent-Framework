# Agent: resolve-issue-dev

## Objective

Implement one issue into a small, reviewable PR with DDD-compliant changes and local validation evidence.

## When to Use

- A specific issue is selected for implementation.
- You need code changes, tests, and PR creation.
- You need backend-first ordering across repos.

## When Not to Use

- Issue drafting only (`create-issue`).
- PR merge/close-only operations (`pr-merge`, `close-issue`).

## Inputs

- Issue number (optional; if absent, select next by priority).
- Optional constraints (scope/time/risk).

## Constraints

- Priority order: backend first, then client; lowest issue number first.
- Follow DDD boundaries and keep diffs focused.
- Use `.tmp/` for PR body and temporary artifacts.
- For external API/framework usage, verify behavior against Context7 docs and capture assumptions when docs are version-ambiguous.
- If Context7 is unavailable/offline, continue with local MCP-first grounding (`git`, `search`, `filesystem`, `bashGateway`) and repository docs (`docs/`, `README.md`, `templates/`).
- For internal architecture, prioritize repository conventions and local source-of-truth files.
- If scope affects UI/UX/navigation/responsive behavior, consult `blecs-ux-authority` and block completion until `UX_DECISION: PASS`.

## Workflow

Use detailed checklist: [`../modules/resolve-issue-workflow.md`](../modules/resolve-issue-workflow.md).

Core flow:

1. Select/fetch issue and define compact plan/spec.
2. Implement minimal changes in a feature branch.
3. Run required local validation commands.
4. Commit, push, create PR with required template sections.
5. Check CI once; if failing, fix root cause and re-run.

## Output Format

Return:

- Plan summary (goal, scope, AC, files, validation)
- Files changed and rationale
- Validation results (commands + outcome)
- PR URL and status

## Completion Criteria

- PR created with issue linkage and complete template.
- Required validations executed and documented.
- CI initiated (or passed) with no unresolved blockers.
- Branch/workspace hygiene preserved.

## References

- `.github/prompts/modules/resolve-issue-workflow.md`
- `.github/prompts/modules/ux/delegation-policy.md`
- `.github/prompts/pr-review-rubric.md`
- `.github/prompts/modules/prompt-quality-baseline.md`
