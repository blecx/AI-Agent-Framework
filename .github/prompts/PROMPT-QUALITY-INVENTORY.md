# Prompt Quality Inventory

Date: 2026-02-21

## Summary

- Scope audited: `.github/prompts/*.md` and `.github/prompts/agents/*.md`
- Oversized prompts were normalized into concise orchestrators plus modules.
- `agents/*.md` operational prompts are <= 100 lines.
- Prompt quality checker passes in baseline and strict modes.

## Current Inventory (lines)

| Lines | File                                                           |
| ----: | -------------------------------------------------------------- |
|   242 | `.github/prompts/README.md`                                    |
|   207 | `.github/prompts/resolve-issue-first-step.md`                  |
|   171 | `.github/prompts/drafting-pr.md`                               |
|   133 | `.github/prompts/agents/README.md`                             |
|   132 | `.github/prompts/tutorial-invocation.md`                       |
|   129 | `.github/prompts/drafting-issue.md`                            |
|    74 | `.github/prompts/agents/Plan.md`                               |
|    63 | `.github/prompts/planning-feature.md`                          |
|    50 | `.github/prompts/multi-step-planning.md`                       |
|    50 | `.github/prompts/cross-repo-coordination.md`                   |
|    49 | `.github/prompts/agents/tutorial.md`                           |
|    49 | `.github/prompts/agents/pr-merge.md`                           |
|    44 | `.github/prompts/PROMPT-QUALITY-INVENTORY.md`                  |
|    43 | `.github/prompts/agents/create-issue.md`                       |
|    41 | `.github/prompts/agents/resolve-issue-dev.md`                  |
|    37 | `.github/prompts/pr-review-rubric.md`                          |
|    37 | `.github/prompts/agents/close-issue.md`                        |
|    36 | `.github/prompts/tutorial-audit-strict.md`                     |
|    31 | `.github/prompts/modules/prompt-quality-baseline.md`           |
|    27 | `.github/prompts/tutorial-default-prompt.md`                   |
|    25 | `.github/prompts/modules/multi-step-planning-phases.md`        |
|    10 | `.github/prompts/modules/multi-step-planning-checklist.md`     |
|    10 | `.github/prompts/modules/cross-repo-coordination-checklist.md` |

## Quality Notes

- Added required-structure baseline (`Objective`, `Inputs`, `Constraints`, `Output Format`, `Completion Criteria`).
- Added explicit `When to Use` / `When Not to Use` guidance.
- Added module references to reduce prompt bloat.
- Added deterministic prompt quality checker script (`scripts/check_prompt_quality.py`).
