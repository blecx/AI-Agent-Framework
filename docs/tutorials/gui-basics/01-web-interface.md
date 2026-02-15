# GUI Web Interface Basics (Current UI)

**Duration:** 10 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

This tutorial reflects the **currently shipped** web app in `apps/web/src`.
You will learn the real UI layout, verify API health, and identify where command and artifact workflows happen.

## Learning Objectives

By the end of this tutorial, you will:

- Open the web app and recognize the actual top-level components
- Understand the difference between project selection and project work views
- Locate the `Commands` and `Artifacts` tabs in project view
- Open API docs and run a health check endpoint
- Understand local visual workflow phase vs API-persisted workflow state

## Prerequisites

- Docker or local dev setup is running
- Web UI reachable at:

  - Docker: `http://localhost:8080`
  - Local dev: `http://localhost:5173`

- API reachable at `http://localhost:8000`

## Step 1: Open the web UI

Open the app in your browser.

### Expected result (Step 1)

You see:

- Header title: **ISO 21500 Project Management AI Agent**
- A workflow phase indicator row (Initiation → Closing)
- A project selection/create area (if no project selected)

## Step 2: Understand the current layout

The current app is centered around these components:

1. **WorkflowIndicator** (top): visual phase selector in UI
2. **ProjectSelector** (when no project selected):
   - existing project cards
   - create form toggle
3. **ProjectView** (after selecting/creating a project):
   - `Commands` tab
   - `Artifacts` tab
   - proposal review modal when a command is proposed

### Expected result (Step 2)

You can explain where each action occurs:

- create/select project in selector view
- run command proposals in `Commands`
- inspect generated files in `Artifacts`

## Step 3: Open API docs

Open `http://localhost:8000/docs`.

In Swagger UI, verify project/command/artifact/workflow routes are available.

### Expected result (Step 3)

Swagger loads and you can expand endpoints successfully.

## Step 4: Run health check in Swagger

Execute:

- `GET /health` (simple health)

Optionally also check:

- `GET /api/v1/health` (detailed health)

### Expected result (Step 4)

You receive a successful response from API health endpoint(s).

## Notes on workflow phase in UI

- The top phase indicator is a **local visual control** in the web app.
- Authoritative workflow state transitions are handled by API endpoints:

  - `GET/PATCH /projects/{project_key}/workflow/state`
  - `GET /projects/{project_key}/workflow/allowed-transitions`
  - and `/api/v1/...` equivalents

## What you learned

✅ How to navigate the **actual** shipped UI
✅ Where project creation, command proposals, and artifact viewing happen
✅ How to verify API health and docs
✅ How to distinguish visual workflow indicator from persisted workflow state

## Next steps

1. [Project Creation](02-project-creation.md)
2. [Commands and Proposals](03-commands-and-proposals.md)
3. [Artifact Browsing](04-artifact-browsing.md)

---

**Last Updated:** 2026-02-15
