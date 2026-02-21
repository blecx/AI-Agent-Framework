# Cross-Repo Change Coordination

## Objective

Plan and execute coordinated backend/frontend changes with explicit contracts, ordering, and rollback strategy.

## When to Use

- A feature spans `AI-Agent-Framework` and `AI-Agent-Framework-Client`.
- API contract or behavior changes affect both repos.
- Deployment timing/order matters.

## When Not to Use

- Single-repo changes with no downstream impact.
- Pure documentation edits unrelated to runtime behavior.

## Inputs

- Change description
- Impacted repository/repositories
- Breaking/non-breaking expectation

## Constraints

- Backend-first by default for new/changed APIs.
- Document explicit request/response contracts.
- Keep issues and PRs cross-linked across repos.

## Workflow

Use detailed checklist: [`modules/cross-repo-coordination-checklist.md`](modules/cross-repo-coordination-checklist.md).

Core steps:

1. Impact analysis and compatibility decision.
2. Define implementation order and dependency gates.
3. Create linked backend/client issues.
4. Validate integration and rollback plan.

## Output Format

Return:

- Impact summary (backend/client/breaking status)
- Ordered rollout plan
- Issue links per repo
- Validation + rollback checklist

## Completion Criteria

- API contract and sequencing are explicit.
- Cross-repo issues are linked and scoped.
- Integration test plan and rollback path are documented.

## References

- `.github/prompts/modules/cross-repo-coordination-checklist.md`
- `.github/prompts/modules/prompt-quality-baseline.md`
