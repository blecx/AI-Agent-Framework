# Copilot Prompt Templates

Reusable prompts for planning, issue drafting, PR quality, and cross-repo coordination.

## When to Use

- You need a consistent structure for plan/issue/PR workflows.
- You want repeatable prompt quality and output contracts.

## When Not to Use

- One-off ad-hoc chat tasks that do not need template rigor.

## Core Prompts

- `planning-feature.md`
- `drafting-issue.md`
- `drafting-pr.md`
- `cross-repo-coordination.md`
- `pr-review-rubric.md`
- `multi-step-planning.md`

## Agent Prompts

See `agents/README.md` for specialized agent workflows.

## Shared Modules

- `modules/prompt-quality-baseline.md`
- `modules/issue-creation-workflow.md`
- `modules/resolve-issue-workflow.md`
- `modules/pr-merge-workflow.md`
- `modules/tutorial-review-workflow.md`
- `modules/cross-repo-coordination-checklist.md`
- `modules/multi-step-planning-checklist.md`
- `modules/ralph-skills-review.md`

Additional modules can be introduced incrementally during prompt refactor slices.

## Output Expectations

Operational prompts should include:

- Objective
- Inputs
- Constraints
- Output Format
- Completion Criteria

## Prompt Quality Checks

- `python scripts/check_prompt_quality.py`

## References

- `.github/copilot-instructions.md`
- `../README.md`
- `../../docs/development.md`
