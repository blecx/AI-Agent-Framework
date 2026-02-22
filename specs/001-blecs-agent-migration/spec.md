# Spec: blecs Agent Migration

## Goal

Transition existing project agent workflows to a blecs namespace while remaining compatible with GitHub Spec Kit structures and behavior.

## Requirements

- Keep existing Copilot custom agents working.
- Use an own namespace: blecs.
- Preserve Spec Kit command semantics and workflow order (constitution, specify, plan, tasks, implement).
- Ensure no interference with upstream Spec Kit command contracts and directories.
- Add Spec Kit-compatible command prompts under dedicated directories.
- Make UX authority consultation mandatory for UI-affecting work.
- Add workflow authority packet support for downstream agents.

## Compatibility Constraints

- Upstream-like command behavior must be maintained for Spec Kit-compatible flow.
- blecs namespace extensions must be additive and must not override or mutate core Spec Kit command behavior.
- Command directories and custom agent directories must remain separated to avoid discovery and format conflicts.
