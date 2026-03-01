# Custom Agent Registry

This directory contains repository custom agents (`*.agent.md`) discoverable by Copilot Chat.

## Available Agents

- **[resolve-issue.agent.md](./resolve-issue.agent.md)** - Issue → PR agent with plan-first execution and validation gates.
- **[pr-merge.agent.md](./pr-merge.agent.md)** - Merge PRs safely with CI checks and issue closure workflow.
- **[close-issue.agent.md](./close-issue.agent.md)** - Close issues with template-backed, traceable resolution comments.
- **[tutorial.agent.md](./tutorial.agent.md)** - Create Markdown-only tutorials with strict visual evidence, feature-gap reporting, and duplicate-content audits.
- **[blecs-ux-authority.agent.md](./blecs-ux-authority.agent.md)** - Master authority for UX/navigation/graphical design and responsive/a11y guardrails.
- **[blecs-workflow-authority.agent.md](./blecs-workflow-authority.agent.md)** - Workflow source-of-truth agent that normalizes process context for implementation and UX agents.
- **[create-issue.agent.md](./create-issue.agent.md)** - Create template-compliant issues only (no implementation), with clear acceptance criteria and validation steps.
- **[Plan.agent.md](./Plan.agent.md)** - Produce compact, actionable implementation plans with bounded discovery and issue sizing.
- **[continue-backend.agent.md](./continue-backend.agent.md)** - Run backend-only continuation loops with guarded PR/merge flow.
- **[continue-phase-2.agent.md](./continue-phase-2.agent.md)** - Run phase-2 continuation loops with review-before-merge policy.
- **[ralph-agent.agent.md](./ralph-agent.agent.md)** - Execute strict spec-kit style issue resolution with specialist review gates.
- **[workflow.agent.md](./workflow.agent.md)** - Legacy workflow-agent wrapper profile for scripted batch runs.

## Documentation-Only (Not Selectable Agents)

- **[agents-catalog-maintainer.md](./agents-catalog-maintainer.md)** - Maintainer playbook/prompt for keeping `.github/agents` and the automation inventory in sync.

## Automation Inventory

- **[AUTOMATIONS.md](./AUTOMATIONS.md)** is documentation (an inventory), not a selectable Copilot custom agent. It maps:
	- runtime agents (Python classes + aliases),
	- custom chat agents (`*.agent.md`),
	- prompt workflows (`.github/prompts/agents/*.md`),
	- command/script automations, VS Code task automations, and CI workflows.

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
