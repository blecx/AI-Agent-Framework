# GUI Project Creation

**Duration:** 15 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Goal / Context

This tutorial matches the current create-project flow implemented in:

- `apps/web/src/components/ProjectSelector.jsx`
- `apps/web/src/services/api.js`

## Prerequisites

- Complete [01 - Web Interface](01-web-interface.md)
- Open <http://localhost:8080>
- API healthy at <http://localhost:8000/health>

## Current Create Flow (Shipped)

1. In `Select or Create Project`, click **+ Create New Project**.
2. Fill:
   - `Project Key`
   - `Project Name`
3. Click **Create Project**.

### Important current behavior

- The UI currently submits **key + name** only.
- A description field is **not currently present** in this form.
- Valid key pattern in the form: `[a-zA-Z0-9_-]+`

## Verification Steps

1. Create project `TODO_001` (or any unused key matching the pattern).
2. Confirm the project appears under **Existing Projects**.
3. Click the project card.
4. Confirm you enter `ProjectView` and can see `Commands` and `Artifacts` tabs.

## API Contract Reference

Frontend call:

- `POST /api/projects` with body `{ "key": "...", "name": "..." }`

Backend route:

- `POST /projects`

## Future Scope (Explicit)

- Richer project metadata fields in the create form (e.g., description)
- Sidebar-specific project list patterns documented in older drafts

## Visual Coverage Report

### 02-project-creation.md

- Existing asset(s):
  - `docs/tutorials/assets/screenshots/workflow/02-project-commands-tab.png`
- Missing asset(s) to capture later:
  - Current create form (`Project Key`, `Project Name`)
  - Existing Projects card list after successful creation

## Next

- Continue with [03 - Commands and Proposals](03-commands-and-proposals.md)

<!-- Legacy content retained below for history; excluded from tutorial flow. -->
<!--

**Duration:** 15 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Create your first ISO 21500 project using the web interface. This comprehensive tutorial walks you through the project creation form with detailed field explanations, validation rules, form submission, and verification steps. You'll learn about project key naming conventions, form best practices, and how to troubleshoot common creation issues.

## Learning Objectives

By the end of this tutorial, you will:
- Create ISO 21500 projects via web form with proper field inputs
- Understand all form fields: key, name, description requirements
- Master form validation rules and regex patterns
- View and interpret project details in UI after creation
- Switch between multiple projects efficiently
- Verify project creation in file system and Git repository
- Navigate project lists and selectors
- Troubleshoot common project creation errors
- Compare GUI workflow with TUI command-line approach
- Use keyboard shortcuts for faster form navigation

## Prerequisites

- **Completed:** [Tutorial 01: Web Interface](01-web-interface.md)
- Docker Compose running (`docker compose ps` shows web and api containers "Up")
- Browser open to http://localhost:8080
- API health check passed (green indicator in UI header)
- No existing TODO-001 project (we'll create it fresh)

## 🎥 Video Walkthrough

> **Coming Soon:** A video walkthrough of this tutorial will be available.
> 
> **What to expect:**
> - Live demonstration of project creation form
> - Field validation rules explained
> - Form submission and verification
> - Troubleshooting common errors
> 
> **Interested in contributing?** See [VIDEO-PLAN.md](../VIDEO-PLAN.md) for recording guidelines.

### Quick Verification

Before starting, verify readiness:

```bash
# Check web UI is accessible
curl -s http://localhost:8080 | grep -q "AI-Agent Framework" && echo "✅ Web UI accessible" || echo "❌ Web UI not accessible"

# Check API is healthy
curl -s http://localhost:8000/health | grep -q '"status":"healthy"' && echo "✅ API healthy" || echo "❌ API unhealthy"

# Verify no TODO-001 exists yet
if docker exec $(docker compose ps -q api) test -d projectDocs/TODO-001 2>/dev/null; then
  echo "⚠️  TODO-001 already exists - delete it first for clean start"
else
  echo "✅ TODO-001 does not exist - ready to create"
fi
```

✅ **Pre-flight Checkpoint:** All checks passed, ready to create project

## The Todo App Example

Throughout this tutorial series, we'll use a consistent real-world example:

**Project:** Todo Application MVP  
**Key:** TODO-001  
**Description:** CRUD task manager with React, Node.js, PostgreSQL

**Full Project Specification:**
- **Name:** Todo Application MVP
- **Key:** TODO-001 (format: ALPHA-DIGITS)
- **Description:** CRUD task manager with React frontend, Node.js API, PostgreSQL database
- **Features:** Create/read/update/delete tasks, filtering by status/priority, due dates, user assignment
- **Tech Stack:** React 19.2, Node.js 20, PostgreSQL 16, Docker
- **Target Users:** Small software teams (5-20 users)
- **Timeline:** 8-week MVP sprint
- **ISO 21500 Phases:** Will progress through all 5 phases (Initiating → Closing)

**Why This Example:**
- Realistic scope for learning ISO 21500 principles
- Common use case (most teams need task management)
- Demonstrates full project lifecycle
- Manageable complexity for tutorial context
- Relatable to software development teams

## Steps

### Step 1: Access Project Creation Form

1. Open web UI: `http://localhost:8080`
2. Click "Create New Project" button
3. Project creation form appears

✅ **Checkpoint:** Form with Key, Name, Description fields visible

### Step 2: Fill Project Details

Enter:
- **Key:** `TODO-001`
- **Name:** `Todo Application MVP`
- **Description:** `CRUD task manager with React frontend, Node.js API, PostgreSQL database`

### Step 3: Submit Form

1. Click "Create Project" button
2. Wait for success message

**Expected:** "Project created successfully!" notification

✅ **Checkpoint:** Project created, appears in projects list

### Step 4: View Project Details

1. Click on "TODO-001" in projects list
2. Project details panel opens

**Expected Information:**
- Key: TODO-001
- Name: Todo Application MVP
- Phase: Initiating
- Status: Active
- Artifacts: 0

✅ **Checkpoint:** Project details displayed

### Step 5: Verify in Sidebar

Check sidebar projects list:
- TODO-001 should appear
- Click to select/deselect

✅ **Checkpoint:** Project appears in sidebar

## Form Validation

Try invalid inputs to see validation:

**Invalid Key (with spaces):**
- Enter: `TODO 001`
- Expected: "Key must not contain spaces" error

**Duplicate Key:**
- Try creating TODO-001 again
- Expected: "Project already exists" error

**Missing Required Fields:**
- Leave Name blank
- Expected: "Name is required" error

## What You've Learned

✅ Create projects via web form  
✅ Form validation rules  
✅ View project details in UI  
✅ Navigate projects list  
✅ Compare GUI vs TUI approaches

## Next Steps

1. **[Tutorial 03: Commands and Proposals](03-commands-and-proposals.md)** - Execute commands via GUI (15 min)
2. **[TUI First Project](../tui-basics/02-first-project.md)** - Command-line version (10 min)

## TUI Equivalent

```bash
python apps/tui/main.py projects create \
  --key TODO-001 \
  --name "Todo Application MVP" \
  --description "CRUD task manager..."
```

See [TUI First Project](../tui-basics/02-first-project.md)

## Success Checklist

- [ ] Create project via web form
- [ ] Project appears in sidebar
- [ ] View project details
- [ ] Understand form validation
- [ ] Compare with TUI approach

---

**Tutorial Series:** [GUI Basics](../README.md#gui-basics) | **Previous:** [01 - Web Interface](01-web-interface.md) | **Next:** [03 - Commands and Proposals](03-commands-and-proposals.md)

-->
