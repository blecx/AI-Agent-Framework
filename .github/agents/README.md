# Custom Agent Registry

This directory contains repository custom agents (`*.agent.md`) discoverable by Copilot Chat.

## Available Agents

- **[resolve-issue-dev.agent.md](./resolve-issue-dev.agent.md)** - Implement backend/client issues with plan-first execution and validation gates.
- **[pr-merge.agent.md](./pr-merge.agent.md)** - Merge PRs safely with CI checks and issue closure workflow.
- **[close-issue.agent.md](./close-issue.agent.md)** - Close issues with template-backed, traceable resolution comments.
- **[tutorial.agent.md](./tutorial.agent.md)** - Create Markdown-only tutorials with strict visual evidence, feature-gap reporting, and duplicate-content audits.
- **[blecs-ux-authority.agent.md](./blecs-ux-authority.agent.md)** - Master authority for UX/navigation/graphical design and responsive/a11y guardrails.
- **[blecs-workflow-authority.agent.md](./blecs-workflow-authority.agent.md)** - Workflow source-of-truth agent that normalizes process context for implementation and UX agents.

## Spec Kit-Compatible Command Prompts

- Core Spec Kit workflow command prompts: [`./speckit/`](./speckit/)
- blecs namespace command extensions: [`./blecs/`](./blecs/)

These directories hold slash-command style prompt files and are intentionally separated from `*.agent.md` custom agent definitions.

## Tutorial Agent Support Prompts

When using `tutorial`, reference these prompt templates:

- **Rails/guardrails:** [`../prompts/agents/tutorial.md`](../prompts/agents/tutorial.md)
- **Default invocation:** [`../prompts/tutorial-default-prompt.md`](../prompts/tutorial-default-prompt.md)
- **Full invocation:** [`../prompts/tutorial-invocation.md`](../prompts/tutorial-invocation.md)
- **Strict audit mode:** [`../prompts/tutorial-audit-strict.md`](../prompts/tutorial-audit-strict.md)

## Auto-Approve Wiring

`tutorial` is enabled for subagent auto-approval in `.vscode/settings.json` under `chat.tools.subagent.autoApprove`.
