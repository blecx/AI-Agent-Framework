# TUI First Project

**Duration:** 10 minutes | **Difficulty:** Beginner | **Interface:** Command-Line (TUI)

## Overview

Create your first ISO 21500 project using the TUI. In this tutorial, you'll create a "Todo Application MVP" project, verify it was created correctly, inspect the Git repository structure, and query project state.

## Learning Objectives

By the end of this tutorial, you will:
- Create a new ISO 21500 project using the TUI
- Understand project key naming conventions
- Inspect project state and metadata
- Verify Git repository structure
- List and manage projects
- Delete projects when needed

## Prerequisites

- **Completed:** [Tutorial 01: Quick Start](01-quick-start.md)
- Docker services running (`docker compose up -d`)
- Terminal access
- Basic understanding of Git concepts (helpful but not required)

## The Todo App Example

Throughout this tutorial series, we'll use a consistent example: **Todo Application MVP**

**Project Overview:**
- **Name:** Todo Application MVP
- **Key:** TODO-001
- **Description:** CRUD task manager with React frontend, Node.js API, PostgreSQL database
- **Features:** Create/Read/Update/Delete tasks, filtering by status/priority, due dates, user assignment
- **Tech Stack:** React 19, Node.js 20, PostgreSQL 16, Docker
- **ISO 21500 Phases:** Initiating → Planning → Executing → Monitoring → Closing

This is a realistic project that demonstrates all ISO 21500 project management concepts.

## Steps

### Step 1: Create the Todo App Project

Create your first project with a key, name, and description:

```bash
python apps/tui/main.py projects create \
  --key TODO-001 \
  --name "Todo Application MVP" \
  --description "CRUD task manager with React frontend, Node.js API, PostgreSQL database"
```

**Expected Output:**
```json
✅ Project created successfully!

Project Details
{
  "key": "TODO-001",
  "name": "Todo Application MVP",
  "description": "CRUD task manager with React frontend, Node.js API, PostgreSQL database",
  "created_at": "2026-02-03T12:34:56.789Z",
  "state": {
    "phase": "initiating",
    "status": "active",
    "artifacts_count": 0,
    "last_command": null
  }
}
```

✅ **Checkpoint:** Project `TODO-001` created with status "active" and phase "initiating"

**Understanding the output:**
- **key:** Unique identifier for the project (must be unique across all projects)
- **name:** Human-readable project name
- **description:** Project details
- **created_at:** Timestamp when project was created
- **state.phase:** Current ISO 21500 phase (starts at "initiating")
- **state.status:** Project status (active, completed, archived)
- **artifacts_count:** Number of artifacts generated (starts at 0)

### Step 2: Verify Project Creation

List all projects to confirm yours was created:

```bash
python apps/tui/main.py projects list
```

**Expected Output:**
```json
Projects (1 total)
[
  {
    "key": "TODO-001",
    "name": "Todo Application MVP",
    "description": "CRUD task manager with React frontend, Node.js API, PostgreSQL database",
    "created_at": "2026-02-03T12:34:56.789Z",
    "state": {
      "phase": "initiating",
      "status": "active",
      "artifacts_count": 0
    }
  }
]
```

✅ **Checkpoint:** You should see your TODO-001 project in the list

**Try creating another project:**
```bash
python apps/tui/main.py projects create \
  --key DEMO-001 \
  --name "Demo Project" \
  --description "Test project for learning"
```

Now list again:
```bash
python apps/tui/main.py projects list
```

You should see 2 projects now.

### Step 3: Inspect Project Details

Get detailed information about a specific project:

```bash
python apps/tui/main.py projects show --key TODO-001
```

**Expected Output:**
```json
Project: TODO-001

{
  "key": "TODO-001",
  "name": "Todo Application MVP",
  "description": "CRUD task manager with React frontend, Node.js API, PostgreSQL database",
  "created_at": "2026-02-03T12:34:56.789Z",
  "updated_at": "2026-02-03T12:34:56.789Z",
  "state": {
    "phase": "initiating",
    "status": "active",
    "artifacts_count": 0,
    "raid_summary": {
      "risks": 0,
      "actions": 0,
      "issues": 0,
      "decisions": 0
    },
    "last_command": null,
    "last_command_at": null
  },
  "git_info": {
    "repository_path": "/projectDocs/TODO-001",
    "branch": "main",
    "commits": 1,
    "latest_commit": "Initial commit for project TODO-001"
  }
}
```

✅ **Checkpoint:** Detailed project information displayed with Git info

**Key fields explained:**
- **state.phase:** Current ISO 21500 phase (initiating, planning, executing, monitoring, closing)
- **state.status:** Project status (active, on-hold, completed, archived)
- **raid_summary:** Count of RAID register entries (covered in Tutorial 04)
- **git_info:** Git repository details for this project

### Step 4: Query Project State

Get the current state of a project:

```bash
python apps/tui/main.py projects state --key TODO-001
```

**Expected Output:**
```json
Project State: TODO-001

{
  "key": "TODO-001",
  "phase": "initiating",
  "status": "active",
  "artifacts_count": 0,
  "raid_summary": {
    "risks": 0,
    "actions": 0,
    "issues": 0,
    "decisions": 0
  },
  "workflow": {
    "current_phase": "initiating",
    "allowed_transitions": ["planning"],
    "phase_completion": 0.0,
    "next_recommended_actions": [
      "Create project charter",
      "Identify stakeholders",
      "Define initial risks and assumptions"
    ]
  }
}
```

✅ **Checkpoint:** Project state shows phase "initiating" with 0% completion

**Understanding workflow:**
- **current_phase:** Where the project is now in the ISO 21500 lifecycle
- **allowed_transitions:** Which phases you can move to next
- **phase_completion:** Progress percentage for current phase (0.0 to 1.0)
- **next_recommended_actions:** ISO 21500 guidance on what to do next

### Step 5: Verify Git Repository Structure

Behind the scenes, the AI-Agent Framework creates a Git repository for each project to track all changes. Let's explore it:

```bash
# Navigate to the project docs directory
cd projectDocs/TODO-001

# Check Git log
git log --oneline
```

**Expected Output:**
```
a1b2c3d (HEAD -> main) [TODO-001] Initial commit for project TODO-001
```

```bash
# View repository structure
ls -la
```

**Expected Output:**
```
total 16
drwxr-xr-x 3 user user 4096 Feb  3 12:34 .
drwxr-xr-x 4 user user 4096 Feb  3 12:34 ..
drwxr-xr-x 8 user user 4096 Feb  3 12:34 .git
-rw-r--r-- 1 user user  256 Feb  3 12:34 project.json
```

**What's in the project directory:**
- **.git/** - Git repository metadata
- **project.json** - Project metadata file
- **artifacts/** - Artifact files (created via Step 2 REST API: POST /artifacts)
- **raid.json** - RAID register entries (created via Step 1: POST /raid)

```bash
# View project metadata
cat project.json
```

**Expected Output:**
```json
{
  "key": "TODO-001",
  "name": "Todo Application MVP",
  "description": "CRUD task manager with React frontend, Node.js API, PostgreSQL database",
  "created_at": "2026-02-03T12:34:56.789Z",
  "state": {
    "phase": "initiating",
    "status": "active"
  }
}
```

✅ **Checkpoint:** Git repository exists with initial commit

```bash
# Return to main directory
cd ../..
```

### Step 6: Understanding Project Keys

Project keys follow a specific naming convention:

**Valid formats:**
- `PROJ-001`, `PROJ-002`, etc. (recommended)
- `TODO-001`, `TODO-002`, etc.
- `MYAPP-123`
- `FEATURE-ABC`

**Rules:**
- Must be unique across all projects
- Typically format: `PREFIX-NUMBER`
- Case-sensitive
- No spaces allowed
- Use hyphens, not underscores

**Try creating an invalid project key (this will fail):**
```bash
python apps/tui/main.py projects create \
  --key "Invalid Key With Spaces" \
  --name "Test Project"
```

**Expected Error:**
```
❌ Error: Project key must not contain spaces
```

**Try creating a duplicate key (this will also fail):**
```bash
python apps/tui/main.py projects create \
  --key TODO-001 \
  --name "Duplicate Project"
```

**Expected Error:**
```
❌ Error: Project with key 'TODO-001' already exists
```

### Step 7: Delete Demo Project (Cleanup)

Let's delete the demo project we created earlier:

```bash
python apps/tui/main.py projects delete --key DEMO-001
```

**Expected Output:**
```
⚠️  Warning: This will permanently delete project DEMO-001 and all its artifacts.
Are you sure? [y/N]: y

✅ Project DEMO-001 deleted successfully
```

**Note:** The TUI will prompt for confirmation to prevent accidental deletions.

Verify it's gone:
```bash
python apps/tui/main.py projects list
```

**Expected Output:** Only TODO-001 should remain.

✅ **Checkpoint:** Demo project deleted, only TODO-001 remains

## What You've Learned

Congratulations! You've completed the First Project tutorial. You now know:

✅ How to create ISO 21500 projects with the TUI  
✅ Project key naming conventions and validation rules  
✅ How to list, show, and query project details  
✅ Understanding project state (phase, status, artifacts count)  
✅ How Git repositories are created and structured for each project  
✅ How to delete projects when needed  
✅ ISO 21500 workflow phases and transitions

## Key Concepts Review

| Concept | Description |
|---------|-------------|
| **Project Key** | Unique identifier (e.g., TODO-001, PROJ-001) |
| **Project State** | Current phase, status, and metadata |
| **ISO 21500 Phases** | Initiating → Planning → Executing → Monitoring → Closing |
| **Git Repository** | Each project has its own Git repo in `projectDocs/<KEY>/` |
| **RAID Summary** | Count of Risks, Actions, Issues, Decisions (covered later) |
| **Workflow Transitions** | Allowed movements between ISO 21500 phases |

## Best Practices

### Project Key Naming

✅ **Good:**
- `TODO-001`, `TODO-002`, `TODO-003` (sequential numbering)
- `PROJ-2026-01`, `PROJ-2026-02` (year-based)
- `MVP-PHASE1`, `MVP-PHASE2` (phase-based)

❌ **Avoid:**
- `my project` (spaces not allowed)
- `todo_001` (prefer hyphens over underscores)
- `1` (too short, not descriptive)
- `This-Is-A-Very-Long-Project-Key-That-Is-Hard-To-Type` (too long)

### Project Descriptions

✅ **Good:**
- Include tech stack: "React + Node.js + PostgreSQL"
- Mention key features: "CRUD operations, authentication, reporting"
- Keep it concise: 1-2 sentences
- Use specific terminology: "RESTful API" vs "backend"

❌ **Avoid:**
- Too vague: "A project"
- Too long: Multiple paragraphs (use artifacts for detailed docs)
- Missing tech details: "A web application" (which stack?)

## Next Steps

Now that you have a project, continue learning:

1. **[Tutorial 03: Artifact Workflow](03-artifact-workflow.md)** - Generate artifacts with propose/apply (15 min)
2. **[Tutorial 04: RAID Management](04-raid-management.md)** - Add risks, actions, issues, decisions (15 min)
3. **[GUI Project Creation](../gui-basics/02-project-creation.md)** - Create projects via web interface (10 min)

**Recommended next:** Tutorial 03 - Artifact Workflow

## Reference

### Quick Command Reference

```bash
# Create project
python apps/tui/main.py projects create \
  --key <KEY> \
  --name "<NAME>" \
  --description "<DESC>"

# List all projects
python apps/tui/main.py projects list

# Show project details
python apps/tui/main.py projects show --key <KEY>

# Get project state
python apps/tui/main.py projects state --key <KEY>

# Delete project
python apps/tui/main.py projects delete --key <KEY>

# View project Git log
cd projectDocs/<KEY> && git log --oneline
```

### Project State Fields

```json
{
  "phase": "initiating | planning | executing | monitoring | closing",
  "status": "active | on-hold | completed | archived",
  "artifacts_count": 0,
  "raid_summary": {
    "risks": 0,
    "actions": 0,
    "issues": 0,
    "decisions": 0
  }
}
```

## Troubleshooting

### Project Creation Fails

**Problem:** `Error: Failed to create project`

**Solutions:**
1. Check project key doesn't already exist: `python apps/tui/main.py projects list`
2. Ensure project key has no spaces or invalid characters
3. Verify API is running: `python apps/tui/main.py health`
4. Check API logs: `docker compose logs api`

### Git Repository Not Created

**Problem:** `projectDocs/<KEY>` directory doesn't exist

**Solutions:**
1. Verify project was created successfully
2. Check Docker volume mounts: `docker compose config`
3. Check API logs for Git errors: `docker compose logs api | grep -i git`
4. Restart services: `docker compose restart`

### Project Key Already Exists

**Problem:** `Error: Project with key 'XXX' already exists`

**Solutions:**
1. Choose a different key: Add a number suffix (TODO-002, TODO-003)
2. Or delete existing project: `python apps/tui/main.py projects delete --key XXX`
3. List existing projects to see what's taken: `python apps/tui/main.py projects list`

## Additional Resources

- [ISO 21500 Standard Overview](https://www.iso.org/standard/50003.html) - Official ISO 21500 documentation
- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics) - Git fundamentals
- [API Documentation](http://localhost:8000/docs) - Interactive API reference
- [Tutorial 03: Artifact Workflow](03-artifact-workflow.md) - Next tutorial

## Success Checklist

Before moving to the next tutorial, ensure you can:

- [ ] Create a new project with `projects create`
- [ ] List all projects with `projects list`
- [ ] View project details with `projects show`
- [ ] Query project state with `projects state`
- [ ] Navigate to `projectDocs/<KEY>` and view Git log
- [ ] Delete a project with `projects delete`
- [ ] Understand ISO 21500 phases and workflow transitions

If all checkboxes are complete, you're ready for [Tutorial 03: Artifact Workflow](03-artifact-workflow.md)!

---

**Tutorial Series:** [TUI Basics](../README.md#tui-basics) | **Previous:** [01 - Quick Start](01-quick-start.md) | **Next:** [03 - Artifact Workflow](03-artifact-workflow.md)
