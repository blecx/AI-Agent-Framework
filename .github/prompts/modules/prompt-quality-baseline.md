# Prompt Quality Baseline

## Required Sections

Each operational prompt (non-README) should include:

- Objective
- When to Use
- When Not to Use
- Inputs
- Constraints
- Output Format
- Completion Criteria

## Size Guidance

- `agents/*.md`: target <= 100 lines
- Non-agent prompts: keep concise; split if > 200 lines
- Exceptions must include a short justification in-file

## Anti-Patterns

- Monolithic prompts with duplicated instructions
- Missing output contract
- Vague completion criteria ("done when done")
- Cross-repo instructions without merge/deploy order

## Validation

- Run: `python scripts/check_prompt_quality.py`
- Verify links: `rg -n "\]\(.*\)" .github/prompts --glob '*.md'`
