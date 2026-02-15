# GUI Artifact Browsing (Current UI)

**Duration:** 10 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Browse generated artifacts using the currently shipped `ArtifactsList` UI.
This tutorial only documents behavior that exists right now.

## Current capabilities

In `Artifacts` tab you can:

- See artifact cards with name/path/type
- Refresh the project artifact list
- Open artifact content in a modal viewer
- Close the viewer and continue browsing

Not currently available in this UI:

- Tree/list mode switch
- Search/filter box
- ZIP export button
- Per-file download button
- Version history/bulk actions

## Prerequisites

- Completed [Commands and Proposals](03-commands-and-proposals.md)
- At least one artifact exists in the selected project

## Step 1: Open Artifacts tab

1. Select your project.
2. Open `Artifacts` tab in project view.

### Checkpoint (Step 1)

You see **Project Artifacts** and a **Refresh** button.

## Step 2: Refresh and inspect cards

1. Click **Refresh**.
2. Review artifact cards.

Each card shows:

- artifact name
- artifact path
- artifact type badge

### Checkpoint (Step 2)

At least one artifact card is visible (or the empty-state message appears if none exist).

## Step 3: Open an artifact

1. Click an artifact card.
2. Wait for content to load.

### Checkpoint (Step 3)

A modal opens with file name and content preview.

## Step 4: Close viewer

Close by either:

- clicking `✕`
- clicking outside modal overlay

### Checkpoint (Step 4)

Viewer closes and you return to artifact cards.

## Optional verification via TUI/API

TUI list:

```bash
python apps/tui/main.py artifacts list --project TODO-001
```

TUI get:

```bash
python apps/tui/main.py artifacts get --project TODO-001 --path artifacts/project-charter.md
```

API list:

```bash
curl -s http://localhost:8000/projects/TODO-001/artifacts | jq .
```

## Next steps

1. [Workflow States (via API)](05-workflow-states.md)
2. [Advanced: TUI + GUI Hybrid](../advanced/01-tui-gui-hybrid.md)
3. [Advanced: Complete ISO 21500](../advanced/02-complete-iso21500.md)

---

**Last Updated:** 2026-02-16
