# GUI Workflow States

**Duration:** 20 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

⚠️ **Note**: This feature is planned for a future release. Current GUI implementation is in development.

## Overview

Visualize and manage ISO 21500 workflow states using the web interface. Learn phase transitions and state management.

## Learning Objectives

- Understand ISO 21500 phases in GUI
- View current workflow state
- Transition between phases
- Track phase completion
- See allowed transitions

## Prerequisites

- Completed: [Tutorial 04: Artifact Browsing](04-artifact-browsing.md)
- Project TODO-001 active

## ISO 21500 Phases in GUI

**Visual indicators:**
- Initiating → Planning → Executing → Monitoring → Closing
- Progress bar showing phase completion
- Current phase highlighted
- Allowed transitions shown

## Steps

### Step 1: View Current State

1. Select TODO-001
2. Find "Workflow" or "State" panel
3. See current phase: Initiating

**Displayed Info:**
- Current phase
- Status: Active
- Completion: 0-100%
- Next actions

✅ **Checkpoint:** Workflow state visible

### Step 2: Transition to Planning

1. Click "Update Phase" button
2. Select "Planning" from dropdown
3. Enter reason: "Charter approved"
4. Click "Confirm"

**Expected:** Phase changes to Planning

✅ **Checkpoint:** Phase transition successful

### Step 3: View Phase Progress

Progress bar shows:
- Phase completion percentage
- Artifacts count
- RAID summary

✅ **Checkpoint:** Progress visible

### Step 4: Add RAID Entries (Brief)

1. Navigate to RAID section
2. Add risk entry via form
3. See RAID count update

✅ **Checkpoint:** RAID integration works

### Step 5: Complete Full Lifecycle (Optional)

Continue transitions:
- Planning → Executing
- Executing → Monitoring
- Monitoring → Closing

Each transition requires reason

✅ **Checkpoint:** All phases accessible

## Workflow Visualization

**GUI Shows:**
- Phase diagram/flowchart
- Current position
- Allowed next phases
- Completion metrics
- Phase-specific actions

## What You've Learned

✅ View ISO 21500 phases in GUI  
✅ Transition between workflow states  
✅ Track phase completion  
✅ Understand allowed transitions  
✅ Visualize project lifecycle

## Next Steps

1. **[Advanced: TUI+GUI Hybrid](../advanced/01-tui-gui-hybrid.md)** - Combined workflows (20 min)
2. **[TUI Full Lifecycle](../tui-basics/05-full-lifecycle.md)** - CLI workflow (30 min)

## TUI Equivalent

```bash
python apps/tui/main.py workflow update --project TODO-001 --phase planning
python apps/tui/main.py projects state --project TODO-001
```

## Success Checklist

- [ ] View current workflow state
- [ ] Transition to new phase
- [ ] See phase completion
- [ ] Understand ISO 21500 phases
- [ ] Compare GUI vs TUI

---

**Tutorial Series:** [GUI Basics](../README.md#gui-basics) | **Previous:** [04 - Artifact Browsing](04-artifact-browsing.md)
