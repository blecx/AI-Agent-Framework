# PR Merge Workflow (Module)

## Steps

1. Verify PR is open, mergeable, and not draft.
2. Confirm required checks are green (or only pre-existing failures).
3. Merge with squash and delete branch.
4. Comment and close linked issue (if needed).
5. Clean `.tmp` files for this issue/PR.
6. Sync local `main` and verify final state.

## Guardrails

- Do not fix failing code/tests in this workflow.
- Delegate implementation changes to `resolve-issue-dev`.
- Document any admin override rationale.
