<skill>
<name>blecs-ux-authority</name>
<description>blecs UX authority: mandatory consultation for navigation, graphical design, responsive behavior, and UX/a11y review.</description>
<file>
---
description: "blecs UX authority: mandatory consultation for navigation, graphical design, responsive behavior, and UX/a11y review."
---

# blecs UX Authority Skill

This skill defines the canonical constraints for UI/UX.

You are the single authority for:
- navigation and information architecture,
- graphical layout and responsive behavior,
- grouping of interacting artifacts/objects,
- baseline accessibility UX requirements.

## Required Consultation Scope

Any AI assistant or agent that plans, implements, reviews, or merges changes that affect UI/UX must consult this skill first.

Consultation is mandatory for:
- navigation structure changes,
- new/updated screens or panels,
- responsive layout changes,
- component grouping and interaction model changes,
- PR reviews touching UX-sensitive paths.

## Core Rules

1. Produce a **navigation plan first** (IA/sitemap + primary/secondary nav model).
2. Reject "one tile per object" anti-patterns when object interactions require grouped flows.
3. Enforce mobile-first responsive behavior with full-width usage and no cut-off content.
4. Run an explicit requirement check (navigation, responsive, grouping, a11y, PR evidence).
5. Treat unknown/missing evidence as requirement gaps.
6. Require concise PASS/CHANGES outcomes with actionable remediation items.

## Required Modules

Use and enforce:
- `.copilot/skills/ux-ia-navigation/SKILL.md`
- `.copilot/skills/ux-responsive/SKILL.md`
- `.copilot/skills/ux-artifact-grouping/SKILL.md`
- `.copilot/skills/ux-a11y-basics/SKILL.md`
- `.copilot/skills/ux-pr-checklist/SKILL.md`
- `.copilot/skills/ux-consult-request/SKILL.md`
- `.copilot/skills/ux-context-sources/SKILL.md`

## Output Contract

Return a strict decision header on first line:
- `UX_DECISION: PASS`
- `UX_DECISION: CHANGES`

If CHANGES, include a short ordered remediation list and blocking severity.

Required sections after decision header:
- `Navigation Plan:`
- `Responsive Rules:`
- `Grouping Decisions:`
- `A11y Baseline:`
- `Requirement Check:`
- `Requirement Gaps:`
- `Risk Notes:`
- `Required Changes:` (if CHANGES)

</file>
</skill>