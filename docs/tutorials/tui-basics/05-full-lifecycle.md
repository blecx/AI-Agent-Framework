# TUI Full Project Lifecycle

**Duration:** 30 minutes | **Difficulty:** Beginner | **Interface:** Command-Line (TUI)

## Overview

Experience the complete ISO 21500 project lifecycle from initiation to closure. Walk through all five phases with the Todo Application MVP, applying best practices at each stage.

## Learning Objectives

By the end of this tutorial, you will:
- Understand all five ISO 21500 phases
- Transition between workflow states
- Apply appropriate commands at each phase
- Track project progress
- Complete a full project lifecycle

## Prerequisites

- **Completed:** [Tutorial 04: RAID Management](04-raid-management.md)
- Docker services running
- Understanding of RAID and artifacts

## 🎥 Video Walkthrough

> **Coming Soon:** A video walkthrough of this tutorial will be available.
> 
> **What to expect:**
> - Complete project lifecycle demonstration (30 minutes)
> - Transition between all five ISO 21500 phases
> - Best practices for each phase
> - Common pitfalls and how to avoid them
> 
> **Interested in contributing?** See [VIDEO-PLAN.md](../VIDEO-PLAN.md) for recording guidelines.

## ISO 21500 Phases

The ISO 21500 standard defines five process groups:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Initiating  │───>│   Planning   │───>│  Executing   │───>│  Monitoring  │───>│   Closing    │
│              │    │              │    │              │    │              │    │              │
│ - Charter    │    │ - WBS        │    │ - Artifacts  │    │ - Progress   │    │ - Lessons    │
│ - Stake      │    │ - Schedule   │    │ - Develop    │    │ - Gap assess │    │ - Handover   │
│   holders    │    │ - Budget     │    │ - Test       │    │ - Issues     │    │ - Archive    │
│ - High-level │    │ - RAID plan  │    │ - Deploy     │    │ - Adjust     │    │ - Closure    │
│   risks      │    │              │    │              │    │              │    │   report     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

**Typical Timeline:**
- Initiating: Week 1
- Planning: Weeks 2-3  
- Executing: Weeks 4-8
- Monitoring: Continuous during Executing
- Closing: Week 9

## Steps

### Phase 1: Initiating (Week 1)

**Goals:** Define project, identify stakeholders, establish charter

#### Step 1.1: Create Project

```bash
python apps/tui/main.py projects create \
  --key TODO-002 \
  --name "Todo Application MVP - Full Lifecycle" \
  --description "Complete walkthrough of ISO 21500 lifecycle for a CRUD task manager"
```

✅ **Checkpoint:** Project created in "initiating" phase

#### Step 1.2: Generate Project Charter

```bash
python apps/tui/main.py propose propose \
  --project TODO-002 \
  --command create_charter \
  --description "Initial project charter with stakeholders"
```

Review and apply:
```bash
# Get proposal ID from previous output (e.g., prop-abc123)
python apps/tui/main.py propose show --project TODO-002 --proposal <ID>
python apps/tui/main.py propose apply --project TODO-002 --proposal <ID>
```

✅ **Checkpoint:** Charter, stakeholder register, and assumptions created

#### Step 1.3: Identify Initial Risks

```bash
# Add high-level risks identified during initiation
python apps/tui/main.py raid add \
  --project TODO-002 \
  --type risk \
  --title "Unclear requirements from product team" \
  --description "User stories not fully defined, may cause scope creep" \
  --priority high \
  --owner "Project Manager"

python apps/tui/main.py raid add \
  --project TODO-002 \
  --type risk \
  --title "Key developer may leave during project" \
  --description "Senior React developer considering another opportunity" \
  --priority medium \
  --owner "HR Manager"
```

✅ **Checkpoint:** Initial risks logged

#### Step 1.4: Document Key Decision

```bash
python apps/tui/main.py raid add \
  --project TODO-002 \
  --type decision \
  --title "Project approved to proceed to planning phase" \
  --description "Steering committee approved project charter and allocated $180K budget. Proceed to detailed planning." \
  --owner "Steering Committee" \
  --context "Initiation gate review on 2026-02-03"
```

✅ **Checkpoint:** Initiation phase complete

### Phase 2: Planning (Weeks 2-3)

**Goals:** Create detailed plans, WBS, schedule, budget, RAID plans

#### Step 2.1: Transition to Planning Phase

```bash
python apps/tui/main.py workflow update \
  --project TODO-002 \
  --phase planning \
  --reason "Initiation complete, charter approved"
```

**Expected Output:**
```json
✅ Workflow phase updated!

Updated State
{
  "project_key": "TODO-002",
  "previous_phase": "initiating",
  "current_phase": "planning",
  "updated_at": "2026-02-03T14:00:00.000Z",
  "transition_reason": "Initiation complete, charter approved"
}
```

✅ **Checkpoint:** Project now in "planning" phase

#### Step 2.2: Create Work Breakdown Structure

```bash
python apps/tui/main.py propose propose \
  --project TODO-002 \
  --command define_wbs \
  --description "Create WBS for Todo App development"

# Apply WBS proposal
python apps/tui/main.py propose apply --project TODO-002 --proposal <ID>
```

✅ **Checkpoint:** WBS artifact created

#### Step 2.3: Plan Schedule

```bash
python apps/tui/main.py propose propose \
  --project TODO-002 \
  --command plan_schedule \
  --description "8-week development schedule with milestones"

python apps/tui/main.py propose apply --project TODO-002 --proposal <ID>
```

✅ **Checkpoint:** Schedule and Gantt chart created

#### Step 2.4: Add Detailed Actions

```bash
# Sprint 1 actions
python apps/tui/main.py raid add \
  --project TODO-002 \
  --type action \
  --title "Set up development environment and CI/CD" \
  --description "Configure Docker, GitHub Actions, staging environment" \
  --priority high \
  --owner "DevOps Team" \
  --due-date "2026-02-10"

python apps/tui/main.py raid add \
  --project TODO-002 \
  --type action \
  --title "Design database schema for tasks and users" \
  --description "Create ERD, define tables, relationships, indexes" \
  --priority high \
  --owner "Database Team" \
  --due-date "2026-02-12"

# Sprint 2 actions
python apps/tui/main.py raid add \
  --project TODO-002 \
  --type action \
  --title "Implement REST API endpoints" \
  --description "CRUD for tasks, user authentication, filtering, pagination" \
  --priority high \
  --owner "Backend Team" \
  --due-date "2026-02-24"

python apps/tui/main.py raid add \
  --project TODO-002 \
  --type action \
  --title "Develop React components for task list and forms" \
  --description "TaskList, TaskForm, Filters, DatePicker components" \
  --priority high \
  --owner "Frontend Team" \
  --due-date "2026-02-26"
```

✅ **Checkpoint:** Sprint actions planned

#### Step 2.5: Check Project State

```bash
python apps/tui/main.py projects state --project TODO-002
```

**Expected Output:**
```json
{
  "phase": "planning",
  "status": "active",
  "artifacts_count": 5,
  "raid_summary": {
    "risks": 2,
    "actions": 4,
    "issues": 0,
    "decisions": 1
  },
  "phase_completion": 0.7,
  "next_recommended_actions": [
    "Complete risk mitigation plans",
    "Finalize budget allocation",
    "Review plans with stakeholders"
  ]
}
```

✅ **Checkpoint:** Planning ~70% complete

### Phase 3: Executing (Weeks 4-8)

**Goals:** Build, test, deploy artifacts

#### Step 3.1: Transition to Executing Phase

```bash
python apps/tui/main.py workflow update \
  --project TODO-002 \
  --phase executing \
  --reason "Planning complete, development starting"
```

✅ **Checkpoint:** Project now in "executing" phase

#### Step 3.2: Mark Actions as Complete

```bash
# Complete Sprint 1 actions
python apps/tui/main.py raid update \
  --project TODO-002 \
  --id raid-003 \
  --status closed \
  --resolution "CI/CD configured with GitHub Actions, staging deployed to AWS"

python apps/tui/main.py raid update \
  --project TODO-002 \
  --id raid-004 \
  --status closed \
  --resolution "Database schema finalized: users, tasks, tags tables with proper indexes"
```

✅ **Checkpoint:** Sprint 1 actions closed

#### Step 3.3: Log an Issue

```bash
python apps/tui/main.py raid add \
  --project TODO-002 \
  --type issue \
  --title "Staging environment intermittent 502 errors" \
  --description "Nginx gateway timeout when API response > 30s. Affects task list with 1000+ items." \
  --priority high \
  --owner "DevOps Lead"
```

✅ **Checkpoint:** Issue logged during execution

#### Step 3.4: Document Technical Decision

```bash
python apps/tui/main.py raid add \
  --project TODO-002 \
  --type decision \
  --title "Use Redis for session storage instead of PostgreSQL" \
  --description "Decision: Redis for faster session lookups, PostgreSQL for persistent data only. Improves API response time by 40%." \
  --owner "Tech Lead" \
  --context "Sprint 2 retrospective"
```

✅ **Checkpoint:** Technical decision documented

### Phase 4: Monitoring (Continuous)

**Goals:** Track progress, identify gaps, resolve issues

#### Step 4.1: Run Gap Assessment

```bash
python apps/tui/main.py propose propose \
  --project TODO-002 \
  --command assess_gaps \
  --description "Mid-project gap analysis"

python apps/tui/main.py propose apply --project TODO-002 --proposal <ID>
```

✅ **Checkpoint:** Gap analysis artifact created

#### Step 4.2: Review Gap Analysis

```bash
cd projectDocs/TODO-002/artifacts/assessments
cat gap-analysis.md | head -50
```

**Expected content:**
```markdown
# Gap Analysis: TODO-002

## Summary
- **Completion:** 65%
- **On Track:** 12/18 milestones
- **At Risk:** 4/18 milestones
- **Blocked:** 2/18 milestones

## Identified Gaps

### Gap 1: Performance Testing Behind Schedule
- **Impact:** High
- **Recommendation:** Allocate 2 additional QA engineers

### Gap 2: Frontend Unit Test Coverage at 58%
- **Target:** 80%
- **Gap:** 22%
- **Recommendation:** Code freeze until coverage reaches 75%

...
```

✅ **Checkpoint:** Gaps identified

#### Step 4.3: Create Actions to Close Gaps

```bash
python apps/tui/main.py raid add \
  --project TODO-002 \
  --type action \
  --title "Increase frontend test coverage to 75%" \
  --description "Add missing unit tests, focus on TaskForm and FilterPanel" \
  --priority critical \
  --owner "Frontend Lead" \
  --due-date "2026-03-01"

python apps/tui/main.py raid add \
  --project TODO-002 \
  --type action \
  --title "Allocate additional QA resources" \
  --description "Request 2 contractors for performance testing sprint" \
  --priority high \
  --owner "Project Manager" \
  --due-date "2026-02-28"
```

✅ **Checkpoint:** Actions created to address gaps

### Phase 5: Closing (Week 9)

**Goals:** Finalize deliverables, lessons learned, handover

#### Step 5.1: Mark Final Actions Complete

```bash
# Close remaining actions
python apps/tui/main.py raid list --project TODO-002 --type action --status open

# For each open action, update:
python apps/tui/main.py raid update \
  --project TODO-002 \
  --id <ACTION_ID> \
  --status closed \
  --resolution "Completed successfully"
```

✅ **Checkpoint:** All actions closed

#### Step 5.2: Resolve Remaining Issues

```bash
python apps/tui/main.py raid update \
  --project TODO-002 \
  --id <ISSUE_ID> \
  --status closed \
  --resolution "502 errors fixed by increasing Nginx timeout to 60s"
```

✅ **Checkpoint:** All issues resolved

#### Step 5.3: Transition to Closing Phase

```bash
python apps/tui/main.py workflow update \
  --project TODO-002 \
  --phase closing \
  --reason "All deliverables complete, ready for handover"
```

✅ **Checkpoint:** Project in "closing" phase

#### Step 5.4: Document Lessons Learned

```bash
python apps/tui/main.py raid add \
  --project TODO-002 \
  --type decision \
  --title "Lessons Learned - Project Retrospective" \
  --description "SUCCESS: Early risk identification prevented major issues. IMPROVEMENT: Need better initial estimates for testing effort. RECOMMENDATION: Allocate 30% more time for QA in future projects." \
  --owner "Project Manager" \
  --context "Final retrospective"
```

✅ **Checkpoint:** Lessons learned documented

#### Step 5.5: Export All Artifacts

```bash
python apps/tui/main.py artifacts export \
  --project TODO-002 \
  --output todo-002-complete.zip

python apps/tui/main.py raid export \
  --project TODO-002 \
  --format json \
  --output todo-002-raid-final.json
```

✅ **Checkpoint:** All artifacts exported

#### Step 5.6: Mark Project Complete

```bash
python apps/tui/main.py workflow update \
  --project TODO-002 \
  --status completed \
  --reason "Project successfully delivered on 2026-03-05"
```

**Expected Output:**
```json
✅ Project status updated!

Final State
{
  "project_key": "TODO-002",
  "phase": "closing",
  "status": "completed",
  "completion_date": "2026-03-05T16:00:00.000Z",
  "duration_weeks": 9,
  "artifacts_count": 12,
  "raid_summary": {
    "risks": 2,
    "actions": 8,
    "issues": 1,
    "decisions": 4
  }
}
```

✅ **Checkpoint:** Project complete!

## What You've Learned

Congratulations! You've completed the Full Lifecycle tutorial. You now know:

✅ All five ISO 21500 phases  
✅ How to transition between phases  
✅ Appropriate commands for each phase  
✅ How to track project progress  
✅ Gap assessment and corrective actions  
✅ Proper project closure procedures  
✅ Complete ISO 21500 workflow

## Key Milestones by Phase

| Phase | Duration | Key Activities | Exit Criteria |
|-------|----------|----------------|---------------|
| **Initiating** | Week 1 | Charter, Stakeholders, High-level Risks | Charter approved |
| **Planning** | Weeks 2-3 | WBS, Schedule, RAID plans | Plans approved, resources allocated |
| **Executing** | Weeks 4-8 | Build, Test, Deploy | All deliverables complete |
| **Monitoring** | Continuous | Track progress, Assess gaps | Issues resolved, on track |
| **Closing** | Week 9 | Handover, Lessons learned, Archive | Sign-off, documentation complete |

## Next Steps

1. **[GUI Workflow States](../gui-basics/05-workflow-states.md)** - Visualize lifecycle in web UI (20 min)
2. **[Advanced: Complete ISO21500](../advanced/02-complete-iso21500.md)** - Deep dive into each phase (60 min)
3. **[Advanced: Automation](../advanced/03-automation-scripting.md)** - Automate workflows with scripts (30 min)

**Recommended next:** GUI Workflow States tutorial

## Reference

### Phase Transition Commands

```bash
# Update phase
python apps/tui/main.py workflow update \
  --project <KEY> \
  --phase <initiating|planning|executing|monitoring|closing> \
  --reason "<REASON>"

# Update status
python apps/tui/main.py workflow update \
  --project <KEY> \
  --status <active|on-hold|completed|archived> \
  --reason "<REASON>"

# Get current state
python apps/tui/main.py projects state --project <KEY>
```

## Troubleshooting

See [Troubleshooting Guide](../shared/troubleshooting.md) for common issues.

## Success Checklist

- [ ] Create project in initiating phase
- [ ] Generate charter artifacts
- [ ] Transition through all five phases
- [ ] Add RAID entries appropriate to each phase
- [ ] Run gap assessment during monitoring
- [ ] Export artifacts and RAID register
- [ ] Mark project as completed

If complete, congratulations on mastering the ISO 21500 lifecycle!

---

**Tutorial Series:** [TUI Basics](../README.md#tui-basics) | **Previous:** [04 - RAID Management](04-raid-management.md)
