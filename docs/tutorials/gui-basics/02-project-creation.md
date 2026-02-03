# GUI Project Creation

**Duration:** 10 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Create your first ISO 21500 project using the web interface. Walk through the project creation form, validation, and verification.

## Learning Objectives

- Create projects via web form
- Understand form validation
- View project details in UI
- Switch between projects
- Compare with TUI approach

## Prerequisites

- Completed: [Tutorial 01: Web Interface](01-web-interface.md)
- Docker Compose running
- Browser open to http://localhost:8080

## The Todo App Example

**Project:** Todo Application MVP  
**Key:** TODO-001  
**Description:** CRUD task manager with React, Node.js, PostgreSQL

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
