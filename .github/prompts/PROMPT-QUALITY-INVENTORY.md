# Prompt Quality Inventory

Date: 2026-02-21

## Summary

- Total prompt markdown files: 20
- Total lines: 4756
- `agents/*.md` prompts currently over target in several files (tracked for follow-up slices)
- This inventory is a baseline snapshot for incremental refactor work.

## Baseline Risk Samples (Before)

From issue context (`#327`):

- `multi-step-planning.md`: 2371 lines
- `agents/create-issue.md`: 386 lines
- `cross-repo-coordination.md`: 326 lines

## Current Inventory (Baseline)

| Lines | File |
| ---: | --- |
| 2371 | `.github/prompts/multi-step-planning.md` |
| 386 | `.github/prompts/agents/create-issue.md` |
| 326 | `.github/prompts/cross-repo-coordination.md` |
| 211 | `.github/prompts/agents/resolve-issue-dev.md` |
| 207 | `.github/prompts/resolve-issue-first-step.md` |
| 199 | `.github/prompts/agents/tutorial.md` |
| 184 | `.github/prompts/agents/pr-merge.md` |
| 171 | `.github/prompts/drafting-pr.md` |
| 132 | `.github/prompts/tutorial-invocation.md` |
| 129 | `.github/prompts/drafting-issue.md` |
| 74 | `.github/prompts/agents/Plan.md` |
| 63 | `.github/prompts/planning-feature.md` |
| 52 | `.github/prompts/README.md` |
| 52 | `.github/prompts/PROMPT-QUALITY-INVENTORY.md` |
| 37 | `.github/prompts/pr-review-rubric.md` |
| 37 | `.github/prompts/agents/close-issue.md` |
| 36 | `.github/prompts/tutorial-audit-strict.md` |
| 31 | `.github/prompts/modules/prompt-quality-baseline.md` |
| 31 | `.github/prompts/agents/README.md` |
| 27 | `.github/prompts/tutorial-default-prompt.md` |

## Quality Notes

- Baseline inventory captured for incremental refactoring.
- Added shared quality rubric: `modules/prompt-quality-baseline.md`.
- Added deterministic checker script: `scripts/check_prompt_quality.py`.
- Refactor of oversized prompts is intentionally deferred to follow-up small slices.
