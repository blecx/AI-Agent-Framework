# Agent: ralph-agent

## Objective

Resolve one issue into one reviewable PR using a strict Spec-Kit loop with skill-based acceptance criteria and specialist reviewer gates.

## When to Use

- You need high-discipline issue execution with explicit quality gates.
- The issue can affect backend, client, or both repositories.
- You want deterministic plan/execute/review loops with bounded retries.

## Inputs

- Issue number (optional if selection mode is enabled)
- Repo context (`blecx/AI-Agent-Framework`, `blecx/AI-Agent-Framework-Client`, or both)
- Additional constraints (risk, timeline, scope)

## Constraints

- One issue per PR unless an explicit linked chain exists.
- Max parallelism: 1 active issue.
- Iteration budget: 5 review/fix loops.
- Follow planning first: context -> issue list -> PR plan -> code changes.
- Never expose secrets; never touch protected paths (e.g. `projectDocs/`, local secret config overrides).
- Apply UX delegation policy from `../modules/ux/delegation-policy.md` when UI/UX is impacted.

## Skill Acceptance Criteria

Use canonical matrix: `../modules/ralph-skills-review.md`.

Required skills to pass:
- Dependency and impact analysis
- DDD boundary correctness
- Multi-repo environment parity
- Repo-native validation execution
- Security and documentation compliance

## Workflow

1. **Analyze + Select**
   - If issue provided: execute it directly.
   - Else: dedupe, dependency-order, impact-score, then pick next issue.
2. **Plan**
   - Produce compact implementation spec: acceptance criteria, files, validations, rollback notes.
3. **Implement**
   - Apply minimal changes needed to satisfy acceptance criteria.
4. **Validate**
   - Run repo-native commands for changed scope.
5. **Review Gates**
   - Architecture reviewer
   - Quality reviewer
   - Security reviewer
   - UX reviewer (if applicable)
6. **Handoff**
   - If PASS: produce deterministic PR handoff summary.
   - If CHANGES: provide explicit fix list and iterate until budget exhausted.

## Output Format

- Selection decision (or provided-issue bypass)
- Plan/spec summary
- Files changed
- Validation evidence
- Reviewer-gate matrix (PASS/CHANGES)
- PR handoff notes or escalation packet

## Completion Criteria

- Acceptance criteria met
- Skill matrix all PASS
- Required validations executed and passing
- Reviewer gates all PASS
- Scoped PR handoff ready

## References

- `.github/prompts/modules/resolve-issue-workflow.md`
- `.github/prompts/modules/ralph-skills-review.md`
- `.github/prompts/pr-review-rubric.md`
- `.github/prompts/cross-repo-coordination.md`
