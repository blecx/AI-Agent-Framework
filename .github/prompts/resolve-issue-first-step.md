# Resolve Issue → PR (Step 1 Prompt)

Use this prompt as the **first step** whenever you are asked to resolve an issue into a PR. It captures the decisions and structure defined during training.

## Output style (required)

Write like a concise Copilot Chat teammate:

- Start directly; no filler.
- Use short bullets.
- Give a brief plan before doing tool work.
- Provide short progress updates during execution.
- Keep this Step 1 response compact (prefer <= 15 lines) unless the user asks for more detail.
- Avoid emojis unless the user explicitly asks.
- Avoid long sectioned documents in chat; do not emit large templates.
- Do not include scoring tables; if selection mode is used, summarize the reasoning in 1–2 bullets.

Low-context guidance (free-tier friendly):

- Do not paste issue bodies or large file contents into chat.
- Prefer: “I’ll fetch issue + search code + implement” over reproducing data.
- Include only: key failure symptom (1 line) + 3–5 relevant file paths + next commands.

Strict validation guidance:

- In the Step 1 “Validation” bullet, list exact commands you will run (lint/tests/build) for each repo you touch.
- Default hard-rule command sets:
  - Client: `cd _external/AI-Agent-Framework-Client && npm run lint && npm run test -- --run && npm run build`
  - Backend: `python -m black apps/api/ && python -m flake8 apps/api/ && pytest`
- Assume CI will be strict: if the repo has PR description gates, plan to use the required PR template sections from the start.

### Step 1 response template (use this)

Output exactly this structure (bullets only), and keep it short:

- Target: {repo} #{issue_number} (or “picking next issue”)
- Plan: {3 bullets max}
- Next actions: {1–3 bullets; include exact gh/git commands or tools you’ll run}
- Validation: {1–2 bullets}

Hard cap: prefer <= 12 lines.

## Inputs

- `issue_number` (optional): if provided, skip selection and execute this issue.
- Repo context: current workspace, existing docs in `docs/`, prompts in `.github/prompts/`, CI config in `.github/workflows/`.

## Non-negotiable constraints

- **Plan → Issues → PRs** workflow: start with a plan/spec, break into small issues if needed, implement one issue per PR.
- **Small PRs:** keep diffs reviewable (prefer < 200 LOC changed) unless the issue requires more.
- **Protected paths:** never commit `projectDocs/` and never commit `configs/llm.json`.
- **PR scope guard:** one issue per PR unless an explicit issue chain is required.
- **Max parallelism (initial):** work on **1** issue at a time (can be expanded later).
- **Iteration budget:** max **5** fix/review loops.
- **Failure handling:** on CI/test failure, iterate up to **5** attempts; then escalate with logs + minimal repro + proposed next steps.
- **Time/request budget:** pack each request as much as possible without forcing a second; if more than **5 premium requests** are needed, store context and ask.

## Tools allowed (categories)

You may use:

- Repo reading/search (files, history, docs)
- Git/GitHub workflow tooling (issues/PRs/CI status)
- Language-specific build/test/lint tooling
- Documentation references for architecture/standards (e.g., RFC/ISO) when relevant

If you use standards or external references to justify a decision, record that in the technical documentation for the change.

## Selection mode (only when no issue is passed)

1. **Collect candidates** (next logical set): open issues, labels, dependencies, recent activity.
2. **Dedupe** (close duplicates, don’t delete history):
   - Duplicate if title similarity is high AND acceptance criteria overlap AND likely file overlap.
   - Action: close duplicate with a message linking to the kept issue.
3. **Dependency ordering**
   - Build a dependency graph (DAG) from “blocks/blocked-by” signals (links/labels/text) and file overlap.
   - Topologically sort; tie-break by impact score.
4. **Impact scoring**
   - Use weighted scoring (example weights):
     - 0.35 value, 0.25 urgency, 0.20 unblock, 0.10 risk, 0.10 effort (lower effort ⇒ higher score).
5. **Pick the next issue**
   - If an ordered chain exists, take the first.
   - Otherwise take the single highest-impact issue.

## Plan-first (mandatory)

Produce a short plan/spec before changing code:

- Goal and scope
- Multi-repo impact analysis (backend vs UX repo, or both)
- Acceptance criteria (explicit, testable)
- Non-goals (avoid unrelated refactors)
- Target files/modules
- Documentation targets (which file(s) will be updated)
- Validation steps (lint/tests/build + how to run)
- Risk notes + rollback

If the issue touches both repos, your plan must include per-repo validation steps and ensure commands run from the correct repo root.

If dependencies or blockers exist:

- Create or recommend sub-issues (ordered), then start with the first.

## Implementation loop (hybrid model structure)

- **Copilot planning stage (analysis/planning/review):** do selection (if needed), dependency ordering, risk decisions, and produce the plan/spec.
- **Copilot coding stage (coding/execution):** implement small, well-scoped coding tasks exactly as described by the plan/spec.
- **Copilot review loop:** re-check acceptance criteria + repo review checklist; if changes are needed, produce a new scoped task and repeat, up to iteration budget.

## Review checklist

- Use the repo’s existing review checklist if present.
- If none exists, use `.github/prompts/pr-review-rubric.md` as the default checklist. Optionally promote it to the repo docs if needed.

## Definition of “resolved”

An issue is resolved only when:

- All acceptance criteria are met
- Tests and docs are updated as needed
- CI is green for quality and tests
- Review passes with **no requested changes**

## Required output (end of Step 1)

Return:

- Target `issue_number` (or confirm the provided one) and which repo it belongs to.
- Any dedupe/dependency notes (only if applicable; keep brief).
- A short plan/spec (goal, scope, acceptance criteria, validation steps).
- The exact validation commands you intend to run.

## Expected final outputs (end of the full issue → PR run)

Before declaring the issue “resolved”, ensure the run produces:

- A PR link (or PR number) that maps to the selected/provided issue
- A short summary of what changed + why
- A PR description that includes validation steps and references the issue (e.g., `Fixes #<issue_number>`)
- Tests/lint/build evidence (commands run + pass/fail result)
- Any documentation updates required by the change (and where)
- Dedupe/dependency notes (if selection mode was used)
- Confirmation that constraints were respected (no `projectDocs/`, no `configs/llm.json` committed)
