# Agent: pr-merge

## Objective

Merge a ready PR safely, close the linked issue with traceability, and clean temporary files.

## When to Use

- CI is passing (or only pre-existing failures are documented).
- PR content is final and ready for squash merge.
- You need post-merge issue closure and cleanup.

## When Not to Use

- Creating issues/PRs or implementing fixes.
- Fixing failing CI or editing PR code/content.

## Inputs

- PR number (required)
- Optional linked issue number (auto-detect if omitted)

## Constraints

- Never fix PR content here; delegate to `resolve-issue-dev`.
- Prefer `gh pr merge --squash --delete-branch`.
- Use `.tmp/` (never `/tmp`) for transient files.
- For UI/UX-affecting PRs, require evidence that `blecs-ux-authority` consultation passed.

## Workflow

Use detailed checklist: [`../modules/pr-merge-workflow.md`](../modules/pr-merge-workflow.md).

High level:

1. Validate merge readiness (`state`, `mergeable`, `checks`).
2. Merge (`--admin` only for documented pre-existing failures).
3. Post closure comment on linked issue.
4. Cleanup `.tmp` artifacts for this issue/PR.
5. Sync local `main` and verify closed state.

## Output Format

Return:

- PR merge result (state + merge SHA)
- Linked issue closure result
- Cleanup verification result
- Any explicit follow-up items

## Completion Criteria

- PR merged and branch deleted.
- Linked issue closed with traceability.
- `.tmp` files for this issue removed.
- Local `main` updated and verified.

## References

- `.github/prompts/modules/pr-merge-workflow.md`
- `.github/prompts/modules/ux/delegation-policy.md`
- `.github/prompts/modules/prompt-quality-baseline.md`
