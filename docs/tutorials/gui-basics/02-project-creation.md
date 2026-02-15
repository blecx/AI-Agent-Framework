# GUI Project Creation (Current UI)

**Duration:** 10 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Create your first project with the currently shipped project selector.
This flow is based on the current `ProjectSelector` implementation.

## What the form currently supports

The create form has exactly two fields:

- **Project Key** (required, pattern: `[a-zA-Z0-9_-]+`)
- **Project Name** (required)

There is no description field in the current web form.

## Prerequisites

- Completed [Web Interface Basics](01-web-interface.md)
- Web UI running (`http://localhost:8080` or `http://localhost:5173`)
- API healthy (`http://localhost:8000/health`)

## Step 1: Open create form

1. In the project selection screen, click **+ Create New Project**.
2. The inline create form appears.

### Checkpoint (Step 1)

You see inputs for **Project Key** and **Project Name**.

## Step 2: Enter project values

Use example values:

- Key: `TODO-001`
- Name: `Todo Application MVP`

### Checkpoint (Step 2)

Both required fields are filled.

## Step 3: Create project

1. Click **Create Project**.
2. Wait for request completion.

### Checkpoint (Step 3)

On success, the newly created project is selected and the app opens `ProjectView`.

## Step 4: Verify project context

In project view, confirm:

- project name in header
- project key in header
- tabs for `Commands` and `Artifacts`

### Checkpoint (Step 4)

You can switch between `Commands` and `Artifacts` tabs.

## Validation behavior to know

- Project key must match: `[a-zA-Z0-9_-]+`
- Key and name are required
- Duplicate key will be rejected by API (409)

## TUI equivalent

```bash
python apps/tui/main.py projects create --key TODO-001 --name "Todo Application MVP"
python apps/tui/main.py projects list
```

## Next steps

1. [Commands and Proposals](03-commands-and-proposals.md)
2. [Artifact Browsing](04-artifact-browsing.md)

---

**Last Updated:** 2026-02-15
