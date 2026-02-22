# Resolve Issue Workflow (Module)

## Steps

1. Select issue (backend-first, lowest number) and confirm scope.
2. Write compact plan: goal, scope, AC, files, validation commands.
3. If scope affects UI/UX/navigation/responsive behavior, run `blecs-ux-authority` consultation and capture decision.
4. Implement minimal code changes in a dedicated branch.
5. Run required validations for touched areas.
6. Commit with `Fixes #<issue>` and push.
7. Create PR using required template sections.
8. Address CI failures by root cause and re-validate.

## Validation Baseline

- Backend: `black`, `flake8`, `pytest`
- Frontend: `npm run lint`, `npm run build`, tests if configured
- Include command outputs/evidence in PR body.

## Guardrails

- Avoid unrelated refactors.
- Keep diffs reviewable and DDD-compliant.
- Use `.tmp/` for transient artifacts.
- Block completion until UX consultation is `PASS` for UI-affecting scope.
