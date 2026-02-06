# TUI Artifact Workflow

**Duration:** 15 minutes | **Difficulty:** Beginner | **Interface:** Command-Line (TUI)

## Overview

Learn the propose/apply workflow pattern for generating artifacts in ISO 21500 projects. In this tutorial, you'll propose commands, review generated artifacts, apply or reject proposals, and inspect the resulting files.

## Learning Objectives

By the end of this tutorial, you will:
- Understand the propose/apply workflow pattern
- Propose commands for artifact generation
- Review proposal details and files
- Apply or reject proposals
- Inspect generated artifacts
- Navigate the artifact directory structure
- Export artifacts for external use

## Prerequisites

- **Completed:** [Tutorial 02: First Project](02-first-project.md)
- Docker services running
- Project TODO-001 created
- Basic understanding of project structure

## The Propose/Apply Pattern

The AI-Agent Framework uses a **two-step workflow** for artifact generation:

1. **Propose:** Generate artifacts as a proposal (doesn't modify project yet)
2. **Review:** Inspect proposed changes
3. **Apply or Reject:** Accept changes (apply) or discard them (reject)

**Why this pattern?**
- **Safety:** Preview changes before committing
- **Review:** Stakeholders can review proposals
- **Version Control:** Each application creates a Git commit
- **Rollback:** Easy to revert by reverting Git commits

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Propose    │──────>│    Review    │──────>│    Apply     │
│   Command    │       │   Proposal   │       │ / Reject     │
└──────────────┘       └──────────────┘       └──────────────┘
      │                                               │
      │                                               │
      v                                               v
  Temp files                                   Git commit
  generated                                    + artifacts
```

## Steps

### Step 1: Understanding Available Commands

First, let's see what commands are available for artifact generation:

```bash
python apps/tui/main.py propose --help
```

**Expected Output:**
```
Usage: main.py propose [OPTIONS] COMMAND [ARGS]...

  Command proposal and execution

Commands:
  apply    Apply a proposal to the project
  list     List all proposals for a project
  propose  Propose a command for execution
  reject   Reject a proposal
  show     Show proposal details
```

**Available commands for proposal:**
- **assess_gaps** - Analyze project gaps (Step 1 feature)
- **create_charter** - Generate project charter
- **define_wbs** - Create Work Breakdown Structure
- **plan_schedule** - Create project schedule
- **(Step 2 features - REST API available)**: Template management, Blueprint selection, Artifact generation with proposal workflow (see [Step 2 Status](../../../planning/step-2-complete-status.md) for details)

### Step 2: Propose Your First Command (Project Charter)

Let's propose creating a project charter for our Todo App:

```bash
python apps/tui/main.py propose propose \
  --project TODO-001 \
  --command create_charter \
  --description "Generate initial project charter for Todo Application MVP"
```

**Expected Output:**
```json
✅ Command proposed successfully!

Proposal Details
{
  "proposal_id": "prop-a1b2c3d4",
  "project_key": "TODO-001",
  "command": "create_charter",
  "description": "Generate initial project charter for Todo Application MVP",
  "status": "pending",
  "created_at": "2026-02-03T12:45:00.000Z",
  "artifacts_count": 3,
  "artifacts_preview": [
    "artifacts/charters/project-charter.md",
    "artifacts/charters/stakeholder-register.md",
    "artifacts/charters/assumptions-log.md"
  ],
  "estimated_size": "~12 KB"
}
```

✅ **Checkpoint:** Proposal created with ID `prop-a1b2c3d4` (yours will differ)

**Understanding the response:**
- **proposal_id:** Unique identifier for this proposal
- **status:** "pending" (awaiting apply or reject)
- **artifacts_count:** Number of files that will be created
- **artifacts_preview:** List of file paths
- **estimated_size:** Approximate total size

### Step 3: List All Proposals

See all pending proposals for a project:

```bash
python apps/tui/main.py propose list --project TODO-001
```

**Expected Output:**
```json
Proposals for TODO-001 (1 total)
[
  {
    "proposal_id": "prop-a1b2c3d4",
    "command": "create_charter",
    "description": "Generate initial project charter for Todo Application MVP",
    "status": "pending",
    "created_at": "2026-02-03T12:45:00.000Z",
    "artifacts_count": 3
  }
]
```

✅ **Checkpoint:** Your proposal appears in the list

### Step 4: View Proposal Details

Inspect a proposal in detail:

```bash
python apps/tui/main.py propose show \
  --project TODO-001 \
  --proposal prop-a1b2c3d4
```

**Note:** Replace `prop-a1b2c3d4` with your actual proposal ID from Step 2.

**Expected Output:**
```json
Proposal: prop-a1b2c3d4

{
  "proposal_id": "prop-a1b2c3d4",
  "project_key": "TODO-001",
  "command": "create_charter",
  "description": "Generate initial project charter for Todo Application MVP",
  "status": "pending",
  "created_at": "2026-02-03T12:45:00.000Z",
  "artifacts": [
    {
      "path": "artifacts/charters/project-charter.md",
      "type": "markdown",
      "size": 8192,
      "preview": "# Project Charter: Todo Application MVP\n\n## Project Overview\n..."
    },
    {
      "path": "artifacts/charters/stakeholder-register.md",
      "type": "markdown",
      "size": 2048,
      "preview": "# Stakeholder Register\n\n| Name | Role | Interest |..."
    },
    {
      "path": "artifacts/charters/assumptions-log.md",
      "type": "markdown",
      "size": 1024,
      "preview": "# Assumptions Log\n\n1. Users have modern browsers..."
    }
  ],
  "git_diff": "... (unified diff showing all changes) ..."
}
```

✅ **Checkpoint:** Detailed view shows file previews and Git diff

**Key sections:**
- **artifacts:** Array of files with previews
- **git_diff:** Unified diff showing what will be committed
- **preview:** First ~200 characters of each file

### Step 5: Apply the Proposal

Accept the proposal and commit artifacts to the project:

```bash
python apps/tui/main.py propose apply \
  --project TODO-001 \
  --proposal prop-a1b2c3d4
```

**Expected Output:**
```json
✅ Proposal applied successfully!

Applied Proposal
{
  "proposal_id": "prop-a1b2c3d4",
  "status": "applied",
  "applied_at": "2026-02-03T12:46:00.000Z",
  "git_commit": "abc123def456",
  "git_message": "[TODO-001] Applied proposal: create_charter",
  "artifacts_added": 3,
  "artifacts_paths": [
    "projectDocs/TODO-001/artifacts/charters/project-charter.md",
    "projectDocs/TODO-001/artifacts/charters/stakeholder-register.md",
    "projectDocs/TODO-001/artifacts/charters/assumptions-log.md"
  ]
}
```

✅ **Checkpoint:** Proposal applied, artifacts committed to Git

**What just happened:**
1. Proposal status changed from "pending" to "applied"
2. Artifacts were written to `projectDocs/TODO-001/artifacts/`
3. A Git commit was created
4. Project state was updated

### Step 6: Verify Artifacts Were Created

Check the file system:

```bash
# Navigate to project directory
cd projectDocs/TODO-001

# List artifact directory
ls -R artifacts/
```

**Expected Output:**
```
artifacts/:
charters

artifacts/charters:
assumptions-log.md  project-charter.md  stakeholder-register.md
```

```bash
# View project charter
cat artifacts/charters/project-charter.md | head -30
```

**Expected Output:**
```markdown
# Project Charter: Todo Application MVP

## Project Overview

**Project Name:** Todo Application MVP  
**Project Key:** TODO-001  
**Start Date:** 2026-02-03  
**Expected Duration:** 8-12 weeks  
**Budget:** $150,000 - $200,000

## Project Purpose and Justification

### Business Need
Modern teams need a lightweight, user-friendly task management solution that integrates with existing workflows...

### Project Goals
1. Deliver a functional CRUD task manager
2. Support 100+ concurrent users
3. Mobile-responsive design
4. RESTful API for integrations

## Project Objectives

- **Objective 1:** Complete frontend development by Week 6
- **Objective 2:** Deploy API to staging by Week 4
- **Objective 3:** Achieve 90% test coverage

...
```

✅ **Checkpoint:** Artifacts exist and contain generated content

```bash
# View Git log
git log --oneline -3
```

**Expected Output:**
```
abc123d (HEAD -> main) [TODO-001] Applied proposal: create_charter
def456e [TODO-001] Initial commit for project TODO-001
```

✅ **Checkpoint:** Git commit created for proposal application

```bash
# Return to main directory
cd ../..
```

### Step 7: List Project Artifacts via TUI

Use the TUI to browse artifacts:

```bash
python apps/tui/main.py artifacts list --project TODO-001
```

**Expected Output:**
```json
Artifacts for TODO-001 (3 total)

[
  {
    "path": "artifacts/charters/project-charter.md",
    "type": "file",
    "size": 8192,
    "modified": "2026-02-03T12:46:00.000Z"
  },
  {
    "path": "artifacts/charters/stakeholder-register.md",
    "type": "file",
    "size": 2048,
    "modified": "2026-02-03T12:46:00.000Z"
  },
  {
    "path": "artifacts/charters/assumptions-log.md",
    "type": "file",
    "size": 1024,
    "modified": "2026-02-03T12:46:00.000Z"
  }
]
```

✅ **Checkpoint:** TUI lists all artifacts with metadata

### Step 8: Propose Another Command (Assess Gaps)

Let's propose another command to assess project gaps:

```bash
python apps/tui/main.py propose propose \
  --project TODO-001 \
  --command assess_gaps \
  --description "Analyze gaps between current and desired project state"
```

**Expected Output:**
```json
✅ Command proposed successfully!

Proposal Details
{
  "proposal_id": "prop-e5f6g7h8",
  "project_key": "TODO-001",
  "command": "assess_gaps",
  "description": "Analyze gaps between current and desired project state",
  "status": "pending",
  "created_at": "2026-02-03T12:47:00.000Z",
  "artifacts_count": 1,
  "artifacts_preview": [
    "artifacts/assessments/gap-analysis.md"
  ]
}
```

✅ **Checkpoint:** Second proposal created

### Step 9: Reject a Proposal (Demonstrating Rejection)

Let's reject this proposal to demonstrate the reject workflow:

```bash
python apps/tui/main.py propose reject \
  --project TODO-001 \
  --proposal prop-e5f6g7h8 \
  --reason "Waiting for more project details before gap assessment"
```

**Expected Output:**
```json
✅ Proposal rejected successfully!

Rejected Proposal
{
  "proposal_id": "prop-e5f6g7h8",
  "status": "rejected",
  "rejected_at": "2026-02-03T12:48:00.000Z",
  "rejection_reason": "Waiting for more project details before gap assessment",
  "artifacts_cleaned": 1
}
```

✅ **Checkpoint:** Proposal rejected, temporary files cleaned

**What happened:**
1. Proposal status changed to "rejected"
2. Temporary artifact files were deleted
3. No Git commit was created
4. Project state remains unchanged

**Why reject?**
- Proposal doesn't meet requirements
- Need stakeholder approval first
- Wrong command or parameters
- Testing/learning purposes

### Step 10: Export Artifacts

Export artifacts for sharing or archiving:

```bash
python apps/tui/main.py artifacts export \
  --project TODO-001 \
  --output todo-artifacts.zip
```

**Expected Output:**
```
✅ Artifacts exported successfully!

Export Details
{
  "project_key": "TODO-001",
  "output_file": "todo-artifacts.zip",
  "files_count": 3,
  "total_size": "11.5 KB",
  "created_at": "2026-02-03T12:49:00.000Z"
}
```

Verify the export:
```bash
ls -lh todo-artifacts.zip
unzip -l todo-artifacts.zip
```

**Expected Output:**
```
Archive:  todo-artifacts.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     8192  02-03-2026 12:46   artifacts/charters/project-charter.md
     2048  02-03-2026 12:46   artifacts/charters/stakeholder-register.md
     1024  02-03-2026 12:46   artifacts/charters/assumptions-log.md
---------                     -------
    11264                     3 files
```

✅ **Checkpoint:** Artifacts exported to ZIP file

## What You've Learned

Congratulations! You've completed the Artifact Workflow tutorial. You now know:

✅ The propose/apply workflow pattern for safety and review  
✅ How to propose commands with `propose propose`  
✅ How to list proposals with `propose list`  
✅ How to view proposal details with `propose show`  
✅ How to apply proposals with `propose apply`  
✅ How to reject proposals with `propose reject`  
✅ How to list artifacts with `artifacts list`  
✅ How to export artifacts with `artifacts export`  
✅ How Git commits track proposal applications

## Key Concepts Review

| Concept | Description |
|---------|-------------|
| **Propose** | Generate artifacts as a proposal (doesn't modify project) |
| **Apply** | Accept proposal and commit artifacts to project |
| **Reject** | Discard proposal and clean temporary files |
| **Proposal ID** | Unique identifier (e.g., prop-a1b2c3d4) |
| **Artifacts** | Generated files (charters, schedules, code, etc.) |
| **Git Commit** | Each apply creates a versioned commit |

## Workflow Patterns

### Safe Workflow (Recommended)
```
1. Propose command
2. Review proposal details
3. Share with stakeholders
4. Apply if approved
5. Verify artifacts created
```

### Quick Workflow (For Testing)
```
1. Propose command
2. Immediately apply (skip detailed review)
```

### Bulk Workflow (Advanced)
```
1. Propose multiple commands
2. Review all proposals
3. Apply approved, reject others
```

## Available Commands (Step 1)

| Command | Description | Artifacts Generated |
|---------|-------------|---------------------|
| **create_charter** | Project charter | charter.md, stakeholders.md, assumptions.md |
| **assess_gaps** | Gap analysis | gap-analysis.md |
| **define_wbs** | Work Breakdown Structure | wbs.md, wbs-diagram.svg |
| **plan_schedule** | Project schedule | schedule.md, gantt-chart.svg |

**Step 2 REST API (Available Now):**

Step 2 features are available via REST API endpoints (TUI commands in progress):

- **POST /templates** - Create project templates with validation rules
- **GET /blueprints** - List available project blueprints
- **POST /artifacts** - Generate artifacts from templates with Jinja2 rendering
- **POST /proposals** - Create change proposals with diff visualization
- **POST /proposals/{id}/apply** - Apply approved proposals to project

See [Step 2 Complete Status](../../../planning/step-2-complete-status.md) for full implementation details (16/18 issues merged).

## Next Steps

Continue your learning journey:

1. **[Tutorial 04: RAID Management](04-raid-management.md)** - Manage risks, actions, issues, decisions (15 min)
2. **[Tutorial 05: Full Lifecycle](05-full-lifecycle.md)** - Complete ISO 21500 workflow (30 min)
3. **[GUI Commands and Proposals](../gui-basics/03-commands-and-proposals.md)** - Propose/apply via web UI (15 min)

**Recommended next:** Tutorial 04 - RAID Management

## Reference

### Quick Command Reference

```bash
# Propose command
python apps/tui/main.py propose propose \
  --project <KEY> \
  --command <COMMAND> \
  --description "<DESC>"

# List proposals
python apps/tui/main.py propose list --project <KEY>

# Show proposal
python apps/tui/main.py propose show --project <KEY> --proposal <ID>

# Apply proposal
python apps/tui/main.py propose apply --project <KEY> --proposal <ID>

# Reject proposal
python apps/tui/main.py propose reject --project <KEY> --proposal <ID> --reason "<REASON>"

# List artifacts
python apps/tui/main.py artifacts list --project <KEY>

# Export artifacts
python apps/tui/main.py artifacts export --project <KEY> --output <FILE.zip>
```

### Proposal Status Flow

```
pending ──apply──> applied
   │
   └───reject──> rejected
```

## Troubleshooting

### Proposal Creation Fails

**Problem:** `Error: Failed to create proposal`

**Solutions:**
1. Verify project exists: `python apps/tui/main.py projects list`
2. Check command name is valid (no typos)
3. Ensure API is running: `python apps/tui/main.py health`
4. Check API logs: `docker compose logs api | tail -50`

### Apply Fails

**Problem:** `Error: Failed to apply proposal`

**Solutions:**
1. Verify proposal exists and is pending: `propose list --project <KEY>`
2. Check proposal ID is correct (copy/paste to avoid typos)
3. Ensure no Git conflicts in projectDocs
4. Check disk space: `df -h`

### Artifacts Not Visible

**Problem:** `artifacts list` returns empty

**Solutions:**
1. Verify proposal was applied (not just proposed)
2. Check proposal status: `propose show --project <KEY> --proposal <ID>`
3. Manually verify files exist: `ls projectDocs/<KEY>/artifacts/`
4. Refresh or restart TUI

### Export Fails

**Problem:** `Error: Failed to export artifacts`

**Solutions:**
1. Ensure artifacts exist: `artifacts list --project <KEY>`
2. Check write permissions in current directory: `pwd && ls -la`
3. Verify output filename doesn't already exist (will overwrite)
4. Use absolute path for output file

## Additional Resources

- [ISO 21500 Artifacts Guide](../shared/iso21500-artifacts.md) - Artifact types explained
- [Git Workflow Best Practices](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
- [API Documentation: Proposals](http://localhost:8000/docs#/proposals)
- [Tutorial 04: RAID Management](04-raid-management.md) - Next tutorial

## Success Checklist

Before moving to the next tutorial, ensure you can:

- [ ] Propose a command with `propose propose`
- [ ] List proposals with `propose list`
- [ ] View proposal details with `propose show`
- [ ] Apply a proposal with `propose apply`
- [ ] Reject a proposal with `propose reject`
- [ ] List artifacts with `artifacts list`
- [ ] Export artifacts with `artifacts export`
- [ ] Verify Git commits were created after applying proposals
- [ ] Understand the propose/apply workflow benefits

If all checkboxes are complete, you're ready for [Tutorial 04: RAID Management](04-raid-management.md)!

---

**Tutorial Series:** [TUI Basics](../README.md#tui-basics) | **Previous:** [02 - First Project](02-first-project.md) | **Next:** [04 - RAID Management](04-raid-management.md)
