# Agent Workflow Prompts

Concise workflow prompts for specialized agents.

## When to Use

Use these prompts when invoking subagents for issue lifecycle work.

## When Not to Use

Do not use these files as generic end-user docs; they are operator rails for agent execution.

## Available Agent Prompts

- `create-issue.md`
- `Plan.md`
- `continue-phase-2.md`
- `resolve-issue-dev.md`
- `pr-merge.md`
- `close-issue.md`
- `tutorial.md`

Note: Authority agent canonical definitions live under `.github/agents/*.agent.md`.

## Quality Baseline

- Keep prompts concise (target <= 100 lines for `agents/*.md`).
- Include explicit output format and completion criteria.
- Delegate out-of-scope actions to the correct agent.
- Keep detailed procedural content in shared modules under `../modules/`.

## Canonical UX Delegation Policy

- Canonical source: `.github/prompts/modules/ux/delegation-policy.md`
- Agent/workflow prompts must reference this source instead of duplicating delegation policy blocks.

## Validation

- `python scripts/check_prompt_quality.py`
- `wc -l .github/prompts/agents/*.md`
