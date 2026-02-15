# Tutorial Agent Invocation Template

Use this template to invoke the custom **`tutorial`** agent with consistent, high-quality inputs.

## Prompt (Generic)

```text
Use subagent: tutorial

Create a best-in-class tutorial in Markdown only.

Target:
- Tutorial type: [UX | TUI]
- Feature/workflow: [DESCRIBE WORKFLOW]
- Audience: [BEGINNER | INTERMEDIATE | ADVANCED]

Mandatory requirements:
1) Output must be Markdown only.
2) Include screenshots for major user transitions (required).
3) Include schema picture(s) with draw.io source + exported SVG references (required).
4) Include workflow picture(s) visualizing end-to-end step flow (required).
4) Detect logical breaks/functional gaps and add a "Feature Gap List" section for developers.
5) Prevent duplicate content with existing tutorials.
6) Keep UX and TUI content fully separated (self-contained learning path per track).

Deliverables (all Markdown):
- Main tutorial document
- Feature Gap List section (or sibling markdown)
- Duplicate Content Audit section
- Asset regeneration section (how screenshots/diagrams are regenerated)

Result description (required):
- Return one Markdown package that clearly separates:
  1) Tutorial content
  2) Feature Gap List
  3) Duplicate Content Audit
  4) Asset Regeneration instructions

Quality bar:
- Accurate and reproducible steps
- One action per step with expected result
- Troubleshooting + verification checklist
- No hallucinated routes/commands/UI behavior

Repository context:
- Tutorials location: docs/tutorials/
- Visual assets: docs/tutorials/assets/
- Scripted capture/export preferred (Playwright + draw.io)

Now produce the tutorial and all required sections.
```

## Prompt (UX Track)

```text
Use subagent: tutorial

Create a UX-only tutorial (self-contained, no TUI dependency) for:
[DESCRIBE UX FLOW]

Requirements:
- Markdown-only output
- Screenshot-backed steps (required)
- Schema picture(s) via draw.io (required)
- Workflow picture(s) (required)
- Feature Gap List for developers
- Duplicate Content Audit against existing UX docs
- Explicitly avoid duplicating TUI content
```

## Prompt (TUI Track)

```text
Use subagent: tutorial

Create a TUI-only tutorial (self-contained, no UX dependency) for:
[DESCRIBE TUI FLOW]

Requirements:
- Markdown-only output
- Terminal-step clarity with expected output checkpoints
- Screenshot-backed checkpoints (required)
- Schema picture(s) via draw.io (required)
- Workflow picture(s) (required)
- Feature Gap List for developers
- Duplicate Content Audit against existing TUI docs
- Explicitly avoid duplicating UX content
```

## Optional Add-On: Audit Existing Tutorials First

```text
Before writing, audit docs/tutorials for duplication, stale steps, and missing transitions.
Then produce:
1) Canonical structure proposal
2) Updated tutorial content
3) Feature Gap List
4) Duplicate Content Audit with canonical links
```

## Strict Audit Mode (No New Tutorial Content)

```text
Use subagent: tutorial

Run STRICT AUDIT MODE on existing tutorials only (do not create new tutorial steps unless fixing factual errors).

Scope:
- Track: [UX | TUI]
- Directory: [TARGET DOC PATHS]

Required checks:
1) Logical breaks and missing transitions
2) Functional mismatch vs real behavior
3) Duplicate content across tutorials
4) Missing visual evidence

Visual evidence policy (required):
- Screenshots: required for major transitions
- Schema picture(s): required (draw.io source + SVG export path)
- Workflow picture(s): required for flow comprehension

Result format (Markdown only):
1) Audit Summary
2) Defect List (with severity)
3) Feature Gap List (developer handoff)
4) Duplicate Content Audit (canonicalization plan)
5) Visual Coverage Report (missing/available screenshots/schema/workflow pictures)
6) Recommended Fix Plan (prioritized)
```
