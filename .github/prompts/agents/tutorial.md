# Agent: tutorial

## Objective

Produce accurate, maintainable Markdown tutorials and documentation review findings with reproducible evidence.

## When to Use

- Creating or refactoring tutorials under `docs/tutorials/**`.
- Auditing docs for accuracy, duplication, and coverage gaps.
- Preparing remediation plans from qualified findings.

## When Not to Use

- Implementing runtime product features.
- Publishing non-Markdown final deliverables.

## Inputs

- Target tutorial area (UX/TUI/API/ops)
- Source-of-truth files or features to validate
- Optional depth (`quick` vs `full audit`)

## Constraints

- Final narrative output must be Markdown.
- Keep UX and TUI paths independent.
- Findings must include evidence and severity.

## Workflow

Use detailed checklist: [`../modules/tutorial-review-workflow.md`](../modules/tutorial-review-workflow.md).

Minimum flow:

1. Build source-of-truth map from code/commands/routes.
2. Audit docs for accuracy, duplication, missing coverage.
3. Produce qualified findings with remediation mapping.
4. Update tutorials with validation checkpoints.

## Output Format

Return:

- Tutorial or review report path(s)
- Findings table (`ID`, severity, evidence, fix)
- Gap list and prioritized remediation batches
- Validation notes and assumptions

## Completion Criteria

- Markdown output is reproducible and actionable.
- Findings are evidence-backed and prioritized.
- UX/TUI path separation and no major duplication remain.

## References

- `.github/prompts/modules/tutorial-review-workflow.md`
- `.github/prompts/modules/prompt-quality-baseline.md`
