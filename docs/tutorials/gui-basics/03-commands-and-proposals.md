# GUI Commands and Proposals

**Duration:** 15 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

⚠️ **Note**: This feature is planned for a future release. Current GUI implementation is in development.

## Overview

Execute commands and review proposals using the web interface. Learn the CommandPanel component and ProposalModal workflow.

## Learning Objectives

- Use CommandPanel to propose commands
- Review proposals in ProposalModal
- Apply/reject proposals via GUI
- View diff previews
- Compare with TUI workflow

## Prerequisites

- Completed: [Tutorial 02: Project Creation](02-project-creation.md)
- Project TODO-001 created
- Browser at http://localhost:8080

## Steps

### Step 1: Access CommandPanel

1. Select TODO-001 project
2. Find CommandPanel in main content area
3. See available commands dropdown

✅ **Checkpoint:** CommandPanel visible with command options

### Step 2: Propose Create Charter Command

1. Select "create_charter" from dropdown
2. Enter description: "Generate project charter for Todo App"
3. Click "Propose" button
4. Wait for proposal confirmation

✅ **Checkpoint:** Proposal created, modal appears

### Step 3: Review Proposal in Modal

ProposalModal shows:
- Proposal ID
- Command name
- Artifacts preview (3 files)
- Diff view (optional)

Review artifacts:
- project-charter.md
- stakeholder-register.md
- assumptions-log.md

✅ **Checkpoint:** See artifact previews

### Step 4: Apply Proposal

1. Click "Apply" button in modal
2. Confirmation dialog appears
3. Click "Confirm"
4. Wait for success notification

**Expected:** "Proposal applied successfully!"

✅ **Checkpoint:** Proposal applied, artifacts created

### Step 5: Reject a Proposal (Demo)

1. Propose another command (e.g., assess_gaps)
2. Click "Reject" instead of Apply
3. Enter rejection reason
4. Confirm rejection

✅ **Checkpoint:** Proposal rejected, no artifacts created

## UI Components

**CommandPanel:**
- Command dropdown
- Description textarea
- Propose button
- Proposals list

**ProposalModal:**
- Proposal details
- Artifacts preview
- Diff viewer
- Apply/Reject buttons

## What You've Learned

✅ Use CommandPanel to propose  
✅ Review proposals in modal  
✅ Apply/reject proposals  
✅ View artifact previews  
✅ Compare GUI vs TUI workflow

## Next Steps

1. **[Tutorial 04: Artifact Browsing](04-artifact-browsing.md)** - Navigate artifacts (15 min)
2. **[TUI Artifact Workflow](../tui-basics/03-artifact-workflow.md)** - CLI version (15 min)

## TUI Equivalent

```bash
python apps/tui/main.py propose propose --project TODO-001 --command create_charter
python apps/tui/main.py propose apply --project TODO-001 --proposal <ID>
```

## Success Checklist

- [ ] Propose command via CommandPanel
- [ ] Review proposal in modal
- [ ] Apply proposal successfully
- [ ] Reject a proposal
- [ ] Understand GUI workflow

---

**Tutorial Series:** [GUI Basics](../README.md#gui-basics) | **Previous:** [02 - Project Creation](02-project-creation.md) | **Next:** [04 - Artifact Browsing](04-artifact-browsing.md)
