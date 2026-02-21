# Prompt Quality Inventory

Date: 2026-02-21

## Summary

- Total prompt markdown files: 26
- Total lines: 1579
- All `agents/*.md` prompts are now <= 100 lines.
- Strict checker passes: `python scripts/check_prompt_quality.py --strict`

## Before → After (Issue #327 scope)

- `.github/prompts/multi-step-planning.md`: 2371 → 61 lines
- `.github/prompts/cross-repo-coordination.md`: 326 → 59 lines
- `.github/prompts/agents/create-issue.md`: 386 → 64 lines
- `.github/prompts/agents/resolve-issue-dev.md`: 211 → 61 lines
- `.github/prompts/agents/pr-merge.md`: 184 → 60 lines
- `.github/prompts/agents/tutorial.md`: 199 → 59 lines

## Current Inventory

| Lines | File |
| ---: | --- |
| 207 | `.github/prompts/resolve-issue-first-step.md` |
| 171 | `.github/prompts/drafting-pr.md` |
| 132 | `.github/prompts/tutorial-invocation.md` |
| 129 | `.github/prompts/drafting-issue.md` |
| 74 | `.github/prompts/agents/Plan.md` |
| 64 | `.github/prompts/agents/create-issue.md` |
| 63 | `.github/prompts/planning-feature.md` |
| 61 | `.github/prompts/multi-step-planning.md` |
| 61 | `.github/prompts/agents/resolve-issue-dev.md` |
| 60 | `.github/prompts/agents/pr-merge.md` |
| 59 | `.github/prompts/cross-repo-coordination.md` |
| 59 | `.github/prompts/agents/tutorial.md` |
| 57 | `.github/prompts/README.md` |
| 50 | `.github/prompts/PROMPT-QUALITY-INVENTORY.md` |
| 37 | `.github/prompts/pr-review-rubric.md` |
| 37 | `.github/prompts/agents/close-issue.md` |
| 36 | `.github/prompts/tutorial-audit-strict.md` |
| 32 | `.github/prompts/agents/README.md` |
| 31 | `.github/prompts/modules/prompt-quality-baseline.md` |
| 27 | `.github/prompts/tutorial-default-prompt.md` |
| 27 | `.github/prompts/modules/issue-creation-workflow.md` |
| 24 | `.github/prompts/modules/tutorial-review-workflow.md` |
| 23 | `.github/prompts/modules/resolve-issue-workflow.md` |
| 21 | `.github/prompts/modules/multi-step-planning-checklist.md` |
| 21 | `.github/prompts/modules/cross-repo-coordination-checklist.md` |
| 16 | `.github/prompts/modules/pr-merge-workflow.md` |

## Quality Notes

- Oversized prompts were split into focused wrappers + reusable modules.
- Key operational prompts include objective, use boundaries, outputs, and completion criteria.
- No broken local links detected by checker.
