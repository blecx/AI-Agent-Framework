# Agent: continue-backend

**Command Name:** `/continue-backend`

**Purpose:** Run the backend roadmap loop with small, CI-safe slices and strict merge gates.

**Inputs:**

- Optional issue number (`--issue`)
- Optional roadmap paths (`--paths`)
- Optional label scope (`--label`)

**Workflow:**

1. Resolve model policy (planning role + execution role) and enforce token-budget mode.
2. Validate roadmap issue specs (strict sections + max body budget).
3. Publish backend roadmap issues idempotently.
4. Select next scoped backend issue.
5. Run `scripts/work-issue.py` with retry/backoff for rate-limit handling.
6. Merge via `scripts/prmerge` after review/CI gates.
7. Continue until stop condition.

Primary command:

- `./continue-backend`
- `./continue-backend --max-issues 3`
- `./continue-backend --issue <n>`

Default cap policy:

- Default run limit is `25` issues.
- If `--max-issues` is set above `25`, the script asks for explicit override confirmation.

**Hard Rules:**

- Keep one issue per PR.
- Do not merge without review confirmation.
- Keep backend scope deterministic and token-budgeted.

**References:**

- `.github/prompts/modules/continue-backend-workflow.md`
- `.github/prompts/modules/resolve-issue-workflow.md`
- `scripts/continue-backend.sh`
