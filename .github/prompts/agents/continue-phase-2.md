# Agent: continue-phase-2

**Command Name:** `/continue-phase-2`

**Purpose:** Run the phase-2 integration loop with CI-friendly slices and mandatory review-before-merge gates.

**Inputs:**

- Optional issue number (if omitted, select next via `./next-issue`)
- Optional scope constraints

**Workflow:**

1. Select next issue and validate dependencies.
2. Create a small implementation slice (target reviewable diff and CI-safe scope).
3. Run implementation via `scripts/work-issue.py` with existing guardrails.
4. Ensure UX authority consultation evidence for UI-affecting changes.
5. Run validations and fix failures.
6. Run PR review using repository rubric and confirm approval status.
7. Merge via `scripts/prmerge` only after review + CI pass.
8. Record outcome and continue with next issue until stop condition.

Primary command:

- `./continue-phase-2`
- `./continue-phase-2 --max-issues 3`
- `./continue-phase-2 --issue <n>`

Default cap policy:

- Default run limit is `25` issues.
- If `--max-issues` is set above `25`, the script asks for explicit override confirmation.

**Hard Rules:**

- Keep one issue per PR.
- Do not merge without review confirmation.
- Preserve DDD boundaries and UX delegation policy.
- Keep process deterministic and repeatable.

**References:**

- `.github/prompts/modules/continue-phase-2-workflow.md`
- `.github/prompts/modules/resolve-issue-workflow.md`
- `.github/prompts/pr-review-rubric.md`
