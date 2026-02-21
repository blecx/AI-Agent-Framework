# Prompt Quality Baseline

## Required Sections

Each operational prompt should include:

- Objective
- When to Use
- When Not to Use
- Inputs
- Constraints
- Output Format
- Completion Criteria

## Size Guidance

- `agents/*.md`: target <= 100 lines
- Non-agent prompts: split when > 200 lines
- Exceptions require explicit justification

## Anti-Patterns

- Monolithic prompts with duplicated guidance
- Missing output/completion contracts
- Vague acceptance of "done"
- Unclear cross-repo sequencing

## Validation

- `./.venv/bin/python scripts/check_prompt_quality.py`
- `rg -n "\]\(.*\)" .github/prompts --glob '*.md'`
