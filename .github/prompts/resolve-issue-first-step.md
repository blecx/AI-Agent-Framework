# Resolve Issue → PR (Step 1 Prompt)

Use this prompt as the **first step** whenever you are asked to resolve an issue into a PR. It captures the decisions and structure defined during training.

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

- **Foundry stage (analysis/planning/review):** do selection (if needed), dependency ordering, risk decisions, and produce the plan/spec.
- **GitHub free-tier stage (coding/execution):** implement small, well-scoped coding tasks exactly as described by the Foundry plan/spec.
- **Foundry review loop:** re-check acceptance criteria + repo review checklist; if changes are needed, produce a new scoped task and repeat, up to iteration budget.

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

- Selected `issue_number` (or confirmation of provided one)
- Dedupe actions taken (if any)
- Dependency order (if chain)
- Impact score summary (brief)
- The plan/spec you will follow (bullet list)
- Validation commands you will run

## Expected final outputs (end of the full issue → PR run)

Before declaring the issue “resolved”, ensure the run produces:

- A PR link (or PR number) that maps to the selected/provided issue
- A short summary of what changed + why
- A PR description that includes validation steps and references the issue (e.g., `Fixes #<issue_number>`)
- Tests/lint/build evidence (commands run + pass/fail result)
- Any documentation updates required by the change (and where)
- Dedupe/dependency notes (if selection mode was used)
- Confirmation that constraints were respected (no `projectDocs/`, no `configs/llm.json` committed)
