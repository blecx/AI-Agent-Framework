# Resolve Issue Workflow (Module)

## Steps

1. Select issue (backend-first, lowest number) and confirm scope.
2. Write compact plan: goal, scope, AC, files, validation commands.
3. Implement minimal code changes in a dedicated branch.
4. Run required validations for touched areas.
5. Commit with `Fixes #<issue>` and push.
6. Create PR using required template sections.
7. Address CI failures by root cause and re-validate.

## Validation Baseline

- Backend: `black`, `flake8`, `pytest`
- Frontend: `npm run lint`, `npm run build`, tests if configured
- Include command outputs/evidence in PR body.

## Guardrails

- Avoid unrelated refactors.
- Keep diffs reviewable and DDD-compliant.
- Use `.tmp/` for transient artifacts.
