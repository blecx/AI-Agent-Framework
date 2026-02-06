# GUI Workflow States and ISO 21500 Phase Management

**Duration:** 20 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Master ISO 21500 workflow state management in the AI-Agent Framework web interface. This comprehensive guide walks you through understanding the five ISO 21500 project phases, visualizing current project state, transitioning between phases with proper justification, tracking phase completion metrics, understanding allowed transitions, managing phase-specific artifacts, and integrating workflow states with RAID entries. You'll learn to effectively guide projects through the complete ISO 21500 lifecycle using the visual workflow interface.

## Learning Objectives

By the end of this tutorial, you will be able to:
- Understand all five ISO 21500 project management phases (Initiating, Planning, Executing, Monitoring, Closing)
- View current workflow state and phase details in the GUI
- Transition projects between phases with proper approval workflow
- Track phase completion percentage and metrics
- Understand which phase transitions are allowed and why
- See phase-specific actions and recommended next steps
- Integrate workflow states with artifact generation
- Monitor RAID entries by phase
- Visualize the complete project lifecycle
- Use workflow state diagram for project status communication
- Compare workflow management between GUI and TUI interfaces
- Troubleshoot common workflow state issues

## Prerequisites

- **Completed Tutorials:**
  - [Tutorial 01: Web Interface](01-web-interface.md) - UI navigation fundamentals
  - [Tutorial 02: Project Creation](02-project-creation.md) - Have active project
  - [Tutorial 03: Commands and Proposals](03-commands-and-proposals.md) - Execute commands
  - [Tutorial 04: Artifact Browsing](04-artifact-browsing.md) - View generated artifacts
- **Active Project:** TODO-001 (or any project) with completed charter command
- **Docker running:** `docker ps` shows both web and API containers
- **Understanding:** Basic knowledge of project management lifecycle
- **No external tools required** - all interaction is browser-based

## 🎥 Video Walkthrough

> **Coming Soon:** A video walkthrough of this tutorial will be available.
> 
> **What to expect:**
> - Live demonstration of workflow state transitions
> - ISO 21500 phase explanations
> - Phase completion tracking
> - RAID integration with workflow states
> 
> **Interested in contributing?** See [VIDEO-PLAN.md](../VIDEO-PLAN.md) for recording guidelines.

### Quick Verification

Verify your project is in a workflow state:

```bash
# Check project state in backend
cd projectDocs/TODO-001/.workflow/
cat state.json

# Expected: JSON with current phase (e.g., "initiating")
```

**Expected Output:**
```json
{
  "phase": "initiating",
  "status": "active",
  "updated": "2026-02-06T14:30:00Z"
}
```

✅ **Pre-flight Checkpoint:** Project exists with workflow state file

## ISO 21500 Phases Overview

Before diving into the GUI, understand the five ISO 21500 phases:

### Phase Descriptions

| Phase | Purpose | Key Outputs | Typical Duration |
|-------|---------|-------------|------------------|
| **Initiating** | Define project, authorize start | Project charter, stakeholder register | 5-10% of project |
| **Planning** | Establish scope, schedule, resources | Project management plan, WBS, schedule | 20-30% of project |
| **Executing** | Perform work to produce deliverables | Work deliverables, progress updates | 40-50% of project |
| **Monitoring** | Track progress, manage changes | Status reports, change log, performance data | Parallel with Executing |
| **Closing** | Finalize activities, document lessons | Final deliverables, lessons learned, closure docs | 5-10% of project |

**Phase Sequence:**
```
[Initiating] → [Planning] → [Executing] → [Monitoring] → [Closing]
     ↑                           ↓             ↑
     └───────────────────────────┴─────────────┘
            (Monitoring runs parallel to Executing)
```

**Important Notes:**
- **Linear progression:** Projects generally move forward through phases
- **Monitoring is parallel:** Monitoring happens alongside Executing
- **No backward transitions:** Cannot go from Planning back to Initiating (requires new project)
- **Phase gates:** Transitions require approval/justification
- **Partial overlap:** Some activities span multiple phases

### Phase-Specific Commands

Each phase has typical commands executed:

**Initiating Phase:**
- `charter` - Create project charter
- `stakeholders` - Identify stakeholders
- `assumptions` - Document assumptions

**Planning Phase:**
- `plan` - Create project management plan
- `scope` - Define scope statement and WBS
- `schedule` - Develop schedule
- `risks` - Identify and analyze risks

**Executing Phase:**
- `execute` - Perform project work
- `quality` - Quality assurance activities
- `team` - Team management

**Monitoring Phase:**
- `monitor` - Track progress
- `status` - Generate status reports
- `changes` - Manage change requests

**Closing Phase:**
- `closeout` - Finalize deliverables
- `lessons` - Document lessons learned
- `archive` - Archive project documentation

## Steps

### Step 1: Access Workflow State View

Navigate to the workflow state visualization for your project.

#### 1.1: Select Project (If Not Already Selected)

1. Look at left sidebar for project list
2. Click "TODO-001" to select
3. Main content area updates with project details

**Visual Confirmation:**
- Project name "TODO-001" highlighted
- Main content shows project dashboard

✅ **Checkpoint 1.1:** Project TODO-001 is selected

#### 1.2: Locate Workflow Section/Tab

**The workflow view may appear as:**

**Option A: Workflow Tab**
1. Look for horizontal tabs: "Commands", "Artifacts", "RAID", **"Workflow"**
2. Click "Workflow" tab
3. Workflow diagram appears

**Option B: Dashboard Widget**
1. Main dashboard shows workflow widget
2. Current phase indicator visible
3. Click "View Details" or "Expand" to see full diagram

**Option C: State Panel (Sidebar)**
1. Look for "Project State" or "Workflow" panel in sidebar
2. Shows current phase and quick stats
3. Click to expand full view

**Expected Visual Elements:**
- Workflow diagram showing all 5 phases
- Current phase highlighted (e.g., "Initiating" in blue/green)
- Phase transition buttons or links
- Completion percentage or progress bar
- Metadata: phase start date, duration, status

✅ **Checkpoint 1.2:** Workflow view is visible and loaded

**Screenshot Reference:** `docs/screenshots/gui-05-workflow-overview.png`

#### 1.3: Understand Workflow View Layout

**Workflow Panel Components:**

1. **Phase Diagram (Main Visual)**
   - Horizontal timeline or vertical list
   - 5 boxes/cards representing phases
   - Current phase highlighted with color/border
   - Completed phases marked (checkmark icon)
   - Future phases grayed out or faded
   - Arrows showing progression flow

2. **Current Phase Card (Detail Panel)**
   - Phase name: "Initiating"
   - Status: "Active" or "In Progress"
   - Start date: "2026-02-06"
   - Duration: "2 days" or "40% complete"
   - Artifacts generated: Count or list
   - RAID summary: Risks, actions, issues, decisions count
   - Next actions: Recommendations
   - Transition button: "Move to Planning"

3. **Phase History Timeline (Optional)**
   - List of phase changes with timestamps
   - Shows: "Moved to Initiating on 2026-02-06 at 14:30"
   - Transition reasons recorded

4. **Allowed Transitions Indicator**
   - Shows which phases are valid next steps
   - Grayed out invalid transitions
   - Tooltip explains why transition is blocked

5. **Completion Metrics (Dashboard View)**
   - Overall project completion: "15%"
   - Phase completion: "Initiating: 80%"
   - Artifacts: "4 of 6 expected"
   - RAID: "2 risks identified"

✅ **Checkpoint 1.3:** Understand complete workflow view layout

**Screenshot Reference:** `docs/screenshots/gui-05-workflow-layout.png`

### Step 2: View Current Workflow State (Initiating Phase)

Examine the current phase details in depth.

#### 2.1: Identify Current Phase Indicator

**Look for visual cues:**
- **Color highlighting:** Current phase box in bright color (e.g., blue, green)
- **Bold text:** "Initiating" in bold or larger font
- **Icon:** ▶️ play icon or ● dot indicator on current phase
- **Border:** Thick border around current phase card
- **Label:** "CURRENT" badge or label above phase

**Current Phase: Initiating**

**Expected Display:**
```
┌────────────────────────────────────────────────┐
│ CURRENT PHASE: Initiating                      │
├────────────────────────────────────────────────┤
│ Status:       Active                           │
│ Started:      2026-02-06 10:00                 │
│ Duration:     2 days                           │
│ Completion:   80%                              │
│                                                │
│ Artifacts:    4 generated                      │
│  ✓ project-charter.md                          │
│  ✓ stakeholder-register.md                     │
│  ✓ assumptions-log.md                          │
│  ✓ constraints-log.md                          │
│                                                │
│ RAID Summary:                                  │
│  Risks:       2 identified                     │
│  Actions:     1 open                           │
│  Issues:      0 open                           │
│  Decisions:   1 made                           │
│                                                │
│ Next Actions:                                  │
│  • Review and approve charter                  │
│  • Identify additional stakeholders            │
│  • Transition to Planning when ready           │
│                                                │
│ [Move to Planning] button                      │
└────────────────────────────────────────────────┘
```

✅ **Checkpoint 2.1:** Current phase clearly identified as "Initiating"

**Screenshot Reference:** `docs/screenshots/gui-05-initiating-phase.png`

#### 2.2: Interpret Phase Metadata

**Understanding displayed fields:**

**Status Field:**
- **"Active"** - Phase currently in progress, work ongoing
- **"Completed"** - Phase finished, transitioned to next
- **"Paused"** - Temporarily stopped (some UIs support this)
- **"Blocked"** - Cannot proceed due to dependencies

**Started/Updated Timestamps:**
- Shows when phase began
- Format: "2026-02-06 10:00" or "2 days ago"
- Hover for full ISO timestamp

**Duration:**
- Time spent in current phase
- Absolute: "2 days" or "48 hours"
- Percentage: "80% complete" based on expected phase duration

**Completion Percentage:**
- Calculated based on:
  - Artifacts generated vs. expected
  - Commands executed
  - RAID entries created
  - Manual progress updates (if supported)
- Example: 4 of 5 artifacts = 80% completion

**Artifact Count:**
- Lists key artifacts created in this phase
- Checkmarks indicate completion
- Click artifact name to view content

**RAID Summary:**
- Quick count of RAID entries related to this phase
- Helps assess phase health (many issues = potential problems)

✅ **Checkpoint 2.2:** Understand all phase metadata fields

#### 2.3: Review Phase-Specific Recommendations

**The "Next Actions" section guides you:**

**Typical Initiating Phase Actions:**
- ✓ Complete project charter (already done in Tutorial 03)
- ✓ Identify key stakeholders (already done)
- ⊙ Get charter approval from sponsor
- ⊙ Assign project manager role
- ⊙ Prepare to transition to Planning

**Action Status Icons:**
- ✓ **Completed** - Action finished
- ⊙ **Pending** - Action not yet done
- ⚠️ **Attention needed** - Overdue or blocked

**Recommendations are contextual:**
- Based on current phase
- Reflect what's typically done in ISO 21500
- Suggest commands to execute
- Indicate when phase is ready for transition

✅ **Checkpoint 2.3:** Review and understand next actions

### Step 3: Understand Workflow Diagram Visualization

Explore the visual phase diagram showing complete lifecycle.

#### 3.1: Identify All Five Phases in Diagram

**Typical Diagram Layout (Horizontal):**
```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│Initiating│──▶│ Planning │──▶│Executing │──▶│Monitoring│──▶│  Closing │
│   🟢      │   │          │   │          │   │          │   │          │
│ CURRENT  │   │          │   │          │   │          │   │          │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
     80%            0%             0%             0%             0%
```

**Or Vertical Layout:**
```
1. Initiating ●────▶ CURRENT (80%)
2. Planning  ○
3. Executing ○
4. Monitoring ○
5. Closing ○
```

**Phase States:**
- **Current:** Highlighted, bold, colored indicator
- **Completed:** Checkmark, green color, grayed out
- **Future:** Faded, gray color, dotted border
- **Blocked:** Red border, lock icon, tooltip explains why

✅ **Checkpoint 3.1:** See all five phases in diagram

**Screenshot Reference:** `docs/screenshots/gui-05-phase-diagram.png`

#### 3.2: Understand Phase Transition Arrows

**Arrows indicate allowed transitions:**

**Valid transitions shown with:**
- Solid line arrow
- Clickable/interactive
- Labeled with transition name

**Invalid transitions shown with:**
- Dotted/dashed line
- Grayed out or absent
- Tooltip: "Cannot skip phases"

**Standard Transition Flow:**
1. Initiating → Planning ✓ (always allowed after initiating)
2. Planning → Executing ✓ (after planning complete)
3. Executing → Monitoring ✓ (when work starts)
4. Monitoring → Executing ↔ (can switch back and forth)
5. Monitoring → Closing ✓ (when monitoring complete)
6. Closing → [End] ✓ (project complete)

**Blocked Transitions:**
- Initiating → Executing ✗ (must plan first)
- Planning → Closing ✗ (cannot skip execution)
- Any phase → Initiating ✗ (no backward moves)

✅ **Checkpoint 3.2:** Understand transition arrows and rules

#### 3.3: View Phase Completion Indicators

**Each phase shows completion status:**

**Percentage Indicators:**
- Below or inside phase box
- "80%" for current phase (Initiating)
- "0%" for future phases (not started)
- "100%" for completed phases (if any)

**Progress Bars:**
- Horizontal bar inside phase card
- Filled portion shows completion (e.g., 80% filled)
- Color-coded: green (>75%), yellow (50-75%), red (<50%)

**Completion Criteria (Hover or Detail View):**
```
Initiating Phase Completion: 80%
  ✓ Charter created (25%)
  ✓ Stakeholders identified (25%)
  ✓ Assumptions documented (15%)
  ✓ Constraints documented (15%)
  ⊙ Charter approval (20%) - PENDING
```

✅ **Checkpoint 3.3:** See completion metrics for phases

### Step 4: Transition to Planning Phase

Execute your first phase transition with proper justification.

#### 4.1: Locate Phase Transition Button

**Find "Move to Planning" or "Update Phase" button:**

**Button locations:**
- Inside current phase card (bottom)
- Toolbar above workflow diagram
- Action menu (three dots) on phase card
- Floating action button (FAB) in corner

**Button Visual:**
- Label: "Move to Planning", "Transition to Planning", or "Update Phase"
- Icon: ▶️ arrow or 🔄 transition icon
- Color: Primary button color (blue/green)
- May show arrow pointing to Planning phase

✅ **Checkpoint 4.1:** Transition button located

#### 4.2: Click Transition Button

1. Click the "Move to Planning" button
2. **Transition Modal/Dialog** opens

**Expected Modal Layout:**
```
┌────────────────────────────────────────────────┐
│ Confirm Phase Transition                       │
├────────────────────────────────────────────────┤
│ Current Phase:   Initiating (80% complete)     │
│ New Phase:       Planning                      │
│                                                │
│ Transition Reason (required):                  │
│ ┌────────────────────────────────────────────┐ │
│ │                                            │ │
│ │ [Text area for reason]                     │ │
│ │                                            │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ Checklist (confirm all):                       │
│ [ ] Charter approved by sponsor                │
│ [ ] Key stakeholders identified                │
│ [ ] Ready to begin detailed planning           │
│                                                │
│ [Cancel]  [Confirm Transition]                 │
└────────────────────────────────────────────────┘
```

**Modal Components:**
- **Current and new phase** - Shows what's changing
- **Reason text area** - Required justification field
- **Checklist** - Optional pre-transition verification
- **Cancel button** - Abort transition, return to workflow view
- **Confirm button** - Execute transition (enabled only after reason entered)

✅ **Checkpoint 4.2:** Transition modal opened

**Screenshot Reference:** `docs/screenshots/gui-05-transition-modal.png`

#### 4.3: Enter Transition Reason

**Why reason is required:**
- ISO 21500 mandates phase gate approval
- Creates audit trail for phase changes
- Documents decision-making process
- Useful for project retrospectives

**Enter a meaningful reason:**

**Good Example:**
```
Charter approved by sponsor on 2026-02-06. All stakeholders identified 
and engaged. Project objectives are clear and feasible. Team is ready 
to begin detailed planning activities.
```

**Poor Example (avoid):**
```
Done
```

**Reason Best Practices:**
- Be specific: Mention key accomplishments or approvals
- Reference artifacts: "Charter v1.2 approved"
- Include date: "Approved on 2026-02-06"
- Mention decision-maker: "Sponsor signed off"
- Length: 1-3 sentences (50-200 characters)

**Type or paste reason into text area.**

✅ **Checkpoint 4.3:** Transition reason entered

#### 4.4: Complete Pre-Transition Checklist (If Present)

**If checklist shown, verify each item:**

1. Read each checklist item
2. Ensure it's actually done
3. Check the box

**Example Checklist:**
- [x] Charter approved by sponsor
- [x] Key stakeholders identified
- [x] Ready to begin detailed planning
- [x] Budget allocated
- [x] Project team assigned (or in progress)

**If you cannot check all items:**
- **Option A:** Cancel transition, complete missing items first
- **Option B:** Add note in reason explaining what's pending
- **Option C:** Some UIs allow transition with warnings

**Note:** Some UIs don't have checklists; reason field is sufficient.

✅ **Checkpoint 4.4:** Checklist completed (if present)

#### 4.5: Confirm and Execute Transition

1. Review entered reason and checklist
2. Ensure "Confirm Transition" button is enabled (not grayed out)
3. Click "Confirm Transition" button

**What Happens Behind the Scenes:**
1. UI sends POST request to `/workflow/{project}/transition` API endpoint
2. Request body: `{"from": "initiating", "to": "planning", "reason": "Charter approved..."}`
3. API validates transition is allowed
4. API updates `projectDocs/TODO-001/.workflow/state.json`
5. API creates workflow transition record in project history
6. API responds with new state
7. UI updates workflow diagram

**Expected Loading State:**
- Modal shows spinner or "Processing transition..."
- Button disabled during processing
- Takes 0.5-2 seconds

**Expected Success:**
- Modal closes
- Workflow diagram updates
- "Planning" phase now highlighted as current
- "Initiating" phase marked as completed
- Success toast/notification: "Phase transitioned to Planning"

✅ **Checkpoint 4.5:** Transition successful, now in Planning phase

**Screenshot Reference:** `docs/screenshots/gui-05-planning-phase.png`

#### 4.6: Verify Planning Phase State

**Confirm transition worked:**

**Visual Changes:**
- Planning phase card now highlighted (blue/green border)
- "CURRENT" label moved to Planning
- Initiating phase shows checkmark and "Completed"
- Completion percentages updated:
  - Initiating: 100%
  - Planning: 0% (just started)

**Planning Phase Details:**
```
┌────────────────────────────────────────────────┐
│ CURRENT PHASE: Planning                        │
├────────────────────────────────────────────────┤
│ Status:       Active                           │
│ Started:      2026-02-06 14:45                 │
│ Duration:     Just now                         │
│ Completion:   0%                               │
│                                                │
│ Artifacts:    0 generated                      │
│  ⊙ Project management plan (pending)           │
│  ⊙ Scope statement (pending)                   │
│  ⊙ WBS (pending)                               │
│  ⊙ Schedule baseline (pending)                 │
│                                                │
│ Next Actions:                                  │
│  • Execute 'plan' command                      │
│  • Define scope statement                      │
│  • Create work breakdown structure             │
│  • Develop project schedule                    │
│  • Identify and assess risks                   │
│                                                │
│ [Move to Executing] button (grayed out)        │
└────────────────────────────────────────────────┘
```

**Note:** "Move to Executing" button may be grayed out until planning completion reaches certain threshold (e.g., 50%).

✅ **Checkpoint 4.6:** Planning phase active, UI updated correctly

### Step 5: View Phase Transition History

Review the audit trail of phase changes.

#### 5.1: Locate Transition History

**History may appear as:**

**Option A: Timeline Panel**
- Below workflow diagram
- Chronological list of phase changes
- Expandable details per transition

**Option B: History Tab**
- Separate tab within workflow view
- Table of transitions with columns: Date, From, To, User, Reason

**Option C: Phase Details Dropdown**
- Click "History" or "View Changes" button
- Modal shows transition log

**Typical History View:**
```
Workflow Transition History for TODO-001:

┌─────────────────────────────────────────────────────────────┐
│ 2026-02-06 14:45:00 - Initiating → Planning                 │
│ Reason: Charter approved by sponsor on 2026-02-06. All...   │
│ User: admin                                                 │
│ Duration in Initiating: 2 days                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2026-02-04 10:00:00 - Project Created (Initiating)          │
│ Reason: New project initialized                             │
│ User: admin                                                 │
└─────────────────────────────────────────────────────────────┘
```

✅ **Checkpoint 5.1:** Transition history visible

**Screenshot Reference:** `docs/screenshots/gui-05-transition-history.png`

#### 5.2: Interpret History Records

**Each history entry shows:**

| Field | Example | Meaning |
|-------|---------|---------|
| **Timestamp** | `2026-02-06 14:45:00` | When transition occurred (UTC or local time) |
| **From Phase** | `Initiating` | Previous phase |
| **To Phase** | `Planning` | New phase after transition |
| **Reason** | `Charter approved by sponsor...` | Justification entered during transition |
| **User** | `admin` | Who triggered transition (if auth enabled) |
| **Duration** | `2 days` | Time spent in previous phase |

**History is immutable:**
- Cannot edit or delete history records
- Creates permanent audit trail
- Useful for compliance and retrospectives

✅ **Checkpoint 5.2:** Understand history record format

### Step 6: Explore Phase Completion Tracking

Learn how completion percentage is calculated and displayed.

#### 6.1: View Completion Metrics

**Current Planning Phase Completion: 0%**

**Completion is based on:**

**Artifact Generation (40% weight):**
- Project management plan: 10%
- Scope statement: 10%
- WBS: 10%
- Schedule baseline: 10%

**Command Execution (30% weight):**
- `plan` command: 15%
- `scope` command: 10%
- `schedule` command: 5%

**RAID Entries (20% weight):**
- Risks identified: 10%
- Actions defined: 5%
- Decisions documented: 5%

**Manual Updates (10% weight):**
- Manual progress slider (if supported)
- Phase completion checkboxes

**Total: 100%**

✅ **Checkpoint 6.1:** Understand completion calculation

#### 6.2: Execute Planning Commands to Increase Completion

**Let's generate planning artifacts to see completion increase:**

**Execute 'plan' command (see Tutorial 03 for full steps):**

1. Navigate to Command Panel (if not visible)
2. Select command: "plan" from dropdown
3. Click "Propose"
4. Review proposal
5. Click "Apply"
6. Wait for command to complete

**Expected Result:**
- Artifact generated: `artifacts/plans/project-management-plan.md`
- Planning phase completion increases: 0% → 25%
- Artifact checklist updated:
  - ✓ Project management plan (completed)
  - ⊙ Scope statement (pending)
  - ⊙ WBS (pending)

**Return to Workflow view and refresh:**
- Planning phase card updates
- Completion: 25%
- Progress bar fills 25%

✅ **Checkpoint 6.2:** Completion percentage increased after command

**Screenshot Reference:** `docs/screenshots/gui-05-completion-update.png`

#### 6.3: Track Multiple Artifacts

**Execute additional planning commands:**

**Exercise (Optional - demonstrates completion tracking):**

1. Execute `scope` command → Completion: 25% → 45%
2. Execute `schedule` command → Completion: 45% → 60%
3. Add 2 risk entries via RAID → Completion: 60% → 70%

**Observe changes:**
- Each action increments completion
- Progress bar visually fills
- Artifact checklist gets checkmarks
- "Next Actions" list updates (completed items removed or checked)

**Phase completion threshold:**
- Many UIs require 70-80% completion before allowing next transition
- "Move to Executing" button enables at threshold
- Prevents premature phase transitions

✅ **Checkpoint 6.3:** Understand multi-artifact completion tracking

### Step 7: Understand Allowed vs Blocked Transitions

Learn why some phase transitions are prevented.

#### 7.1: Attempt Invalid Transition (Demonstration)

**While in Planning phase, try to transition to Closing:**

**Expected: Transition blocked**

**Indicators:**
- "Move to Closing" button not present OR grayed out
- Tooltip on hover: "Cannot skip Executing and Monitoring phases"
- Workflow diagram: No arrow from Planning to Closing

**Why blocked:**
- ISO 21500 requires sequential progression
- Cannot skip Executing phase (actual work must be performed)
- Cannot skip Monitoring phase (progress must be tracked)

✅ **Checkpoint 7.1:** Understand blocked transitions

#### 7.2: View Allowed Transitions from Current Phase

**From Planning phase, allowed transitions:**
- Planning → Executing ✓ (once planning is 70%+ complete)

**From Executing phase (future), allowed transitions:**
- Executing → Monitoring ✓ (when work begins)

**From Monitoring phase (future), allowed transitions:**
- Monitoring → Executing ↔ (can go back to execution)
- Monitoring → Closing ✓ (when monitoring complete)

**Transition Rules Table:**

| From Phase | To Phase | Allowed? | Condition |
|------------|----------|----------|-----------|
| Initiating | Planning | ✓ | Always (after charter) |
| Initiating | Executing | ✗ | Must plan first |
| Planning | Executing | ✓ | Planning 70%+ complete |
| Planning | Monitoring | ✗ | Must execute first |
| Executing | Monitoring | ✓ | Work in progress |
| Monitoring | Executing | ✓ | Can iterate |
| Monitoring | Closing | ✓ | Monitoring complete |
| Any phase | Initiating | ✗ | No backward transitions |
| Closing | Any phase | ✗ | Project finalized |

✅ **Checkpoint 7.2:** Understand transition rules

### Step 8: Integrate Workflow with RAID Management (Brief)

See how workflow states relate to RAID entries.

#### 8.1: View RAID Summary in Workflow

**Workflow panel shows RAID counts:**
```
RAID Summary (Planning Phase):
  Risks:       5 identified
  Actions:     3 open, 1 closed
  Issues:      0 open
  Decisions:   2 made
```

**RAID entries are phase-aware:**
- Risks identified during Planning
- Actions assigned during Executing
- Issues tracked during Monitoring
- Decisions documented throughout

✅ **Checkpoint 8.1:** See RAID integration in workflow view

#### 8.2: Add RAID Entry (Optional Exercise)

**Navigate to RAID section and add a risk:**

**Quick Steps (see RAID tutorial for full details):**
1. Click "RAID" tab or navigate to RAID register
2. Click "Add Entry" or "+ New Risk"
3. Fill form:
   - Type: Risk
   - Title: "Budget overrun risk"
   - Description: "Scope creep may cause budget overrun"
   - Severity: High
   - Status: Open
4. Click "Save" or "Add"

**Expected Result:**
- RAID entry created
- Workflow RAID summary updates: "Risks: 5 → 6"
- Planning completion may increase slightly (RAID contributes to completion)

✅ **Checkpoint 8.2:** RAID entry added, workflow updated

### Step 9: Complete Full Lifecycle (Advanced - Optional)

Walk through remaining phase transitions to see complete project lifecycle.

#### 9.1: Transition to Executing Phase

**Once Planning reaches 70%+ completion:**

1. Click "Move to Executing" button
2. Enter reason: "Planning complete. Scope, schedule, and budget approved. Team ready to begin work."
3. Click "Confirm Transition"
4. Executing phase becomes current
5. Planning phase marked complete (100%)

**Executing Phase Characteristics:**
- Focus on work deliverables
- Commands: `execute`, `quality`, `team`
- Artifacts: Work outputs, progress reports
- Duration: Longest phase (40-50% of project)

✅ **Checkpoint 9.1:** Transitioned to Executing (optional)

#### 9.2: Transition to Monitoring Phase

**From Executing phase:**

1. Click "Move to Monitoring" button
2. Enter reason: "Work in progress. Need to track performance metrics and progress."
3. Click "Confirm"
4. Monitoring phase active

**Monitoring Phase Characteristics:**
- Runs parallel to Executing
- Can switch back: Monitoring → Executing
- Commands: `monitor`, `status`, `changes`
- Artifacts: Status reports, performance data
- Focus: Variance analysis, change management

✅ **Checkpoint 9.2:** Transitioned to Monitoring (optional)

#### 9.3: Iterate Between Executing and Monitoring

**Demonstrate bidirectional transition:**

1. From Monitoring, click "Return to Executing" (if available)
2. Enter reason: "Additional work identified. Returning to execution."
3. Transition back to Executing
4. Later, transition to Monitoring again

**This models real-world project management:**
- Work and monitoring happen concurrently
- May need to focus on one or the other
- Can switch as needed

✅ **Checkpoint 9.3:** Demonstrated iteration (optional)

#### 9.4: Transition to Closing Phase

**From Monitoring phase (when complete):**

1. Click "Move to Closing" button
2. Enter reason: "All deliverables complete and accepted. Performance metrics met. Ready for project closure."
3. Click "Confirm"
4. Closing phase active

**Closing Phase Characteristics:**
- Finalize all deliverables
- Commands: `closeout`, `lessons`, `archive`
- Artifacts: Lessons learned, final reports, closure docs
- Actions: Stakeholder acceptance, team release, knowledge transfer

✅ **Checkpoint 9.4:** Transitioned to Closing (optional)

#### 9.5: Complete Project

**In Closing phase:**

1. Execute closing commands (`closeout`, `lessons`)
2. Reach 100% completion
3. Click "Complete Project" or "Finalize"
4. Project status changes: "Active" → "Closed"
5. No further phase transitions allowed

**Closed Project Indicator:**
- Workflow diagram shows all phases at 100%
- Current phase: "Closing (Complete)"
- Status: "Closed" or "Archived"
- Badge: "✓ PROJECT COMPLETE"

✅ **Checkpoint 9.5:** Project lifecycle complete (optional)

**Screenshot Reference:** `docs/screenshots/gui-05-project-complete.png`

## Workflow State Advanced Features

### Workflow State Persistence

**How state is stored:**

**Backend Storage:**
```bash
# Workflow state file
projectDocs/TODO-001/.workflow/state.json

# Content:
{
  "phase": "planning",
  "status": "active",
  "started": "2026-02-06T14:45:00Z",
  "updated": "2026-02-06T15:30:00Z",
  "completion": 25,
  "history": [
    {
      "timestamp": "2026-02-06T14:45:00Z",
      "from": "initiating",
      "to": "planning",
      "reason": "Charter approved by sponsor...",
      "user": "admin"
    }
  ]
}
```

**State is Git-tracked:**
- Each transition creates Git commit
- Full audit trail in Git log
- Can restore previous states via Git

**View state via command line:**
```bash
cd projectDocs/TODO-001/
cat .workflow/state.json
git log .workflow/state.json  # See state change history
```

### Workflow State API Endpoints

**API endpoints for workflow:**

**Get current state:**
```bash
curl http://localhost:8000/workflow/TODO-001
```

**Response:**
```json
{
  "project_key": "TODO-001",
  "phase": "planning",
  "status": "active",
  "completion": 25,
  "started": "2026-02-06T14:45:00Z"
}
```

**Transition phase:**
```bash
curl -X POST http://localhost:8000/workflow/TODO-001/transition \
  -H "Content-Type: application/json" \
  -d '{
    "to": "executing",
    "reason": "Planning complete..."
  }'
```

**List allowed transitions:**
```bash
curl http://localhost:8000/workflow/TODO-001/transitions
```

**Response:**
```json
{
  "current": "planning",
  "allowed": ["executing"],
  "blocked": ["initiating", "monitoring", "closing"],
  "reasons": {
    "initiating": "Cannot move backward",
    "monitoring": "Must execute first",
    "closing": "Must execute and monitor first"
  }
}
```

## What You've Learned

By completing this tutorial, you can now:

✅ Understand all five ISO 21500 project management phases  
✅ View current workflow state and phase details in GUI  
✅ Transition projects between phases with proper justification  
✅ Track phase completion percentage and metrics  
✅ Understand which phase transitions are allowed and why  
✅ View phase-specific actions and recommendations  
✅ Integrate workflow states with artifact generation  
✅ Monitor RAID entries within workflow context  
✅ Visualize complete project lifecycle in workflow diagram  
✅ Review phase transition history and audit trail  
✅ Compare workflow management between GUI and TUI  
✅ Troubleshoot common workflow state issues  

**Key Concepts Mastered:**
- ISO 21500 five-phase lifecycle model
- Phase gate approval process (transition justification)
- Completion percentage calculation methodology
- Allowed vs. blocked transitions (sequential progression rules)
- Workflow state persistence in Git
- Phase-specific artifact and command recommendations
- RAID integration with workflow phases
- Workflow history and audit trails
- Parallel Executing/Monitoring phases

## Next Steps

Congratulations! You've completed the GUI Basics tutorial series. Now explore advanced topics:

1. **[Advanced: TUI+GUI Hybrid Workflows](../advanced/01-tui-gui-hybrid.md)** ✨ NEXT - Combine CLI and web interfaces (20 min)
2. **[TUI Full Lifecycle](../tui-basics/05-full-lifecycle.md)** - Complete project via command-line (30 min)
3. **[Advanced: Multi-Project Management](../advanced/04-multi-project.md)** - Manage multiple concurrent projects (25 min)
4. **[Advanced: Custom Workflows](../advanced/05-custom-workflows.md)** - Adapt phases to your methodology (30 min)

**Recommended Path:** Explore TUI tutorials to see command-line alternatives, then dive into advanced multi-project management.

## TUI Equivalent

The TUI provides similar workflow functionality via command-line:

**View current workflow state:**
```bash
python apps/tui/main.py workflow status --project TODO-001
```

**Expected Output:**
```
Workflow State for TODO-001:
  Current Phase: Planning
  Status:        Active
  Started:       2026-02-06 14:45:00
  Completion:    25%
  
  Allowed Transitions:
    → Executing (requires 70% completion)
  
  Recent History:
    2026-02-06 14:45 | Initiating → Planning | Charter approved by sponsor...
    2026-02-04 10:00 | Project Created | New project initialized
```

**Transition to new phase:**
```bash
python apps/tui/main.py workflow transition --project TODO-001 \
  --to executing \
  --reason "Planning complete. Team ready to begin work."
```

**List allowed transitions:**
```bash
python apps/tui/main.py workflow transitions --project TODO-001
```

**View transition history:**
```bash
python apps/tui/main.py workflow history --project TODO-001
```

**Update completion manually (if supported):**
```bash
python apps/tui/main.py workflow update --project TODO-001 --completion 50
```

See [TUI Full Lifecycle](../tui-basics/05-full-lifecycle.md) for complete command-line workflow tutorial.

**GUI vs TUI Workflow Comparison:**
| Feature | GUI (Web) | TUI (CLI) |
|---------|-----------|-----------|
| **Phase Visualization** | Visual diagram, colors | Text table, ASCII arrows |
| **Transition** | Click button, modal form | Command with flags |
| **History** | Timeline with expandable details | Text list, chronological |
| **Completion Tracking** | Progress bars, percentages | Text percentage, completion check |
| **Allowed Transitions** | Grayed out buttons, tooltips | List of allowed phases |
| **RAID Integration** | Live count updates | Command to view RAID summary |
| **Speed** | Point-and-click | Fast for automation |
| **Scripting** | Not scriptable | Excellent for CI/CD |

**When to use GUI vs TUI:**
- **GUI:** Learning ISO 21500, visual project status, stakeholder demos, one-time transitions
- **TUI:** Automation, scripting, remote SSH access, CI/CD pipelines, bulk project management

## Troubleshooting

Comprehensive troubleshooting guide for workflow state issues:

### Issue 1: Workflow Panel Not Loading

**Symptoms:**
- Workflow tab/section shows "Loading..." indefinitely
- Or shows "Workflow unavailable"
- Workflow diagram doesn't render

**Diagnostic Steps:**
```bash
# 1. Verify workflow state file exists
ls -la projectDocs/TODO-001/.workflow/state.json

# Expected: state.json file present

# 2. Check workflow state API endpoint
curl http://localhost:8000/workflow/TODO-001

# Expected: JSON with phase, status, completion

# 3. Check browser DevTools Console for errors
```

**Solutions:**
- **State file missing:** Initialize workflow: `echo '{"phase":"initiating","status":"active"}' > projectDocs/TODO-001/.workflow/state.json`
- **API not responding:** Restart API: `docker compose restart api`
- **Corrupted state file:** Restore from Git: `cd projectDocs/TODO-001 && git checkout .workflow/state.json`
- **Permission error:** Fix permissions: `chmod 644 projectDocs/TODO-001/.workflow/state.json`

**Expected Resolution Time:** 3-8 minutes

### Issue 2: Transition Button Grayed Out or Missing

**Symptoms:**
- "Move to [NextPhase]" button is disabled
- Or button not present at all
- Cannot progress to next phase

**Diagnostic Steps:**
```bash
# 1. Check current phase and completion
curl http://localhost:8000/workflow/TODO-001

# 2. Check allowed transitions
curl http://localhost:8000/workflow/TODO-001/transitions

# 3. Review completion percentage
```

**Solutions:**
- **Completion too low:** Execute commands to reach threshold (typically 70%)
  - Run planning commands: `plan`, `scope`, `schedule`
  - Add RAID entries
  - Generate required artifacts
- **Phase sequence violation:** Cannot skip phases (e.g., Planning → Closing)
- **Project completed:** If in Closing at 100%, no further transitions
- **Permission issue:** Check if user has workflow update permission (if auth enabled)

**Expected Resolution Time:** 5-15 minutes (depending on completion requirements)

### Issue 3: Completion Percentage Not Updating

**Symptoms:**
- Execute commands but completion stays at same value
- Progress bar doesn't fill
- Artifact checklist doesn't update

**Diagnostic Steps:**
```bash
# 1. Check if artifacts were actually created
ls -la projectDocs/TODO-001/artifacts/

# 2. Refresh browser (hard refresh: Ctrl+Shift+R)

# 3. Check API response for current state
curl http://localhost:8000/workflow/TODO-001

# 4. Look for API errors during command execution
docker compose logs api --tail=100 | grep -i "workflow\|completion"
```

**Solutions:**
- **Browser cache:** Hard refresh browser (Ctrl+Shift+R)
- **API calculation lag:** Wait 10-30 seconds, completion recalculation may be async
- **Command failed:** Check command execution logs, ensure artifacts were generated
- **Incorrect phase:** Ensure you're in correct phase for command (e.g., `plan` in Planning)
- **Manual recalculation:** Some UIs have "Refresh" or "Recalculate" button

**Expected Resolution Time:** 2-10 minutes

### Issue 4: Transition Modal Stuck or Won't Submit

**Symptoms:**
- Click "Confirm Transition" but nothing happens
- Modal shows spinner indefinitely
- Error: "Transition failed"

**Diagnostic Steps:**
```bash
# 1. Check API logs
docker compose logs api --tail=50 | grep -i "transition\|error"

# 2. Test transition via API directly
curl -X POST http://localhost:8000/workflow/TODO-001/transition \
  -H "Content-Type: application/json" \
  -d '{"to":"planning","reason":"Test transition"}'

# 3. Check browser Network tab for failed requests
```

**Solutions:**
- **Validation error:** Ensure reason field is not empty (min 10 characters usually required)
- **Invalid transition:** Check if transition is actually allowed
- **API timeout:** Check API container health: `docker compose ps` and `docker compose logs api`
- **Network issue:** Check browser Network tab for 4xx/5xx errors
- **Concurrent transition:** Another user may have transitioned project; refresh and retry
- **Close and retry:** Close modal, refresh page, attempt transition again

**Expected Resolution Time:** 5-15 minutes

### Issue 5: Transition History Empty or Missing

**Symptoms:**
- History panel shows no transitions
- Or shows "No history available"
- Recent transition not appearing in history

**Diagnostic Steps:**
```bash
# 1. Check workflow state file history
cd projectDocs/TODO-001/
cat .workflow/state.json | jq .history

# 2. Check Git log for workflow changes
git log .workflow/state.json

# 3. Test history API endpoint
curl http://localhost:8000/workflow/TODO-001/history
```

**Solutions:**
- **History not recorded:** Older projects may not have history; only new transitions will appear
- **State file missing history field:** Recreate state file or add empty history array: `{"phase":"...","history":[]}`
- **Git repository issue:** Ensure projectDocs is a Git repo: `cd projectDocs/TODO-001 && git status`
- **Refresh needed:** Browser cache may be stale; hard refresh (Ctrl+Shift+R)
- **API bug:** Check API logs for history endpoint errors

**Expected Resolution Time:** 5-10 minutes

### Issue 6: RAID Summary Not Updating in Workflow

**Symptoms:**
- Add RAID entry but workflow RAID count doesn't change
- RAID summary shows 0 even though entries exist

**Diagnostic Steps:**
```bash
# 1. Check if RAID entries exist
curl http://localhost:8000/raid/TODO-001

# 2. Refresh workflow view
# 3. Check API logs for RAID integration errors
docker compose logs api --tail=100 | grep -i "raid"
```

**Solutions:**
- **Cache issue:** Refresh browser or navigate away and back to workflow view
- **RAID not associated with project:** Ensure RAID entries created for correct project key
- **Phase filter:** Some UIs only show RAID for current phase; check "Show All" toggle
- **API aggregation lag:** RAID counts may take 10-30 seconds to update
- **Separate RAID service:** If RAID is Step 2+ feature, ensure it's enabled and running

**Expected Resolution Time:** 3-8 minutes

## Success Checklist

Before declaring this tutorial complete, verify you can:

- [ ] Navigate to Workflow view for your project
- [ ] See workflow diagram with all 5 phases visualized
- [ ] Identify current phase (Initiating initially)
- [ ] Understand phase metadata (status, started, completion)
- [ ] See phase-specific next actions and recommendations
- [ ] Understand completion percentage calculation
- [ ] Locate "Move to Planning" transition button
- [ ] Click transition button to open modal
- [ ] Enter meaningful transition reason (50+ characters)
- [ ] Complete pre-transition checklist (if present)
- [ ] Confirm and execute transition successfully
- [ ] Verify Planning phase is now current
- [ ] See Initiating phase marked as completed
- [ ] View transition history with timestamp and reason
- [ ] Execute planning command (`plan`) to increase completion
- [ ] Observe completion percentage increase (e.g., 0% → 25%)
- [ ] See artifact checklist update with checkmark
- [ ] Understand allowed vs. blocked transitions
- [ ] See RAID integration in workflow panel
- [ ] (Optional) Complete full lifecycle: Planning → Executing → Monitoring → Closing
- [ ] Compare GUI workflow with TUI equivalent commands

**Estimated Total Time:** 20-30 minutes (45-60 minutes with optional full lifecycle)

**If all checkpoints passed:** ✅ Tutorial 05 Complete! You've mastered workflow state management.

---

**Tutorial Series:** [GUI Basics](../README.md#gui-basics) | **Previous:** [04 - Artifact Browsing](04-artifact-browsing.md)

**Related Tutorials:**
- [TUI Full Lifecycle](../tui-basics/05-full-lifecycle.md) - Complete project lifecycle via CLI
- [Advanced: Custom Workflows](../advanced/05-custom-workflows.md) - Adapt ISO 21500 phases
- [Advanced: Multi-Project Workflows](../advanced/04-multi-project.md) - Manage multiple projects

**Additional Resources:**
- [ISO 21500 Standard Guide](../../spec/iso21500-overview.md) - Official phase descriptions
- [Workflow State API Documentation](http://localhost:8000/docs#/workflow) - API reference
- [Project Governance Guide](../../governance.md) - Phase gate approval process
- [Workflow Architecture](../../architecture/workflow-engine.md) - Technical implementation details
- [Error Catalog](../ERROR-CATALOG.md) - Comprehensive error solutions
