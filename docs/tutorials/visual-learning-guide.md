# Visual Learning Guide (Playwright + Diagrams)

This guide helps beginners learn workflow tutorials with repeatable screenshots and process diagrams.

## What gets generated

- Workflow screenshots (from the live app):
  - `docs/tutorials/assets/screenshots/workflow/*.png`
- Process diagrams (draw.io source + SVG exports):
  - source: `docs/tutorials/assets/diagrams/src/*.drawio`
  - exports: `docs/tutorials/assets/diagrams/generated/*.svg`

## Prerequisites

- Node 20+
- Docker (required for draw.io export script)
- Optional: running app locally (`apps/api` + `apps/web`) or use Docker mode

## One-command generation

```bash
bash docs/tutorials/scripts/generate-visual-assets.sh
```

If you want Docker-backed screenshot capture:

```bash
bash docs/tutorials/scripts/generate-visual-assets.sh --docker
```

## Individual commands

### 1) Export diagrams from draw.io sources

```bash
bash docs/tutorials/scripts/export-drawio.sh
```

### 2) Capture tutorial screenshots with Playwright

```bash
bash docs/tutorials/scripts/capture-workflow-screenshots.sh
```

Docker mode:

```bash
bash docs/tutorials/scripts/capture-workflow-screenshots.sh --docker
```

## Screenshot set (novice learning path)

1. `01-home-overview.png` — App landing and orientation
2. `02-project-commands-tab.png` — Entering project work area
3. `03-command-selection.png` — Choosing command cards
4. `04-artifacts-tab.png` — Verifying output location
5. `05-artifact-viewer.png` — Reading generated artifact content (if present)

## Notes

- The screenshot test intentionally tolerates either existing-project selection or creating a new project.
- If no artifacts exist, `05-artifact-viewer.png` may not be produced; run a command/proposal/apply flow first.
- Keep files stable (same names) so tutorials can embed them directly.
