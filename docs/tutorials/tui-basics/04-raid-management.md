# TUI RAID Management

**Duration:** 15 minutes | **Difficulty:** Beginner | **Interface:** Command-Line (TUI)

## Overview

Learn to manage the RAID register (Risks, Actions, Issues, Decisions) for your ISO 21500 project using the TUI. RAID management is essential for tracking project constraints and making informed decisions.

## Learning Objectives

By the end of this tutorial, you will:
- Understand RAID concepts (Risks, Actions, Issues, Decisions)
- Add entries to the RAID register via TUI
- List and filter RAID entries
- Update RAID entry status
- Delete RAID entries
- Export RAID register

## Prerequisites

- **Completed:** [Tutorial 03: Artifact Workflow](03-artifact-workflow.md)
- Docker services running
- Project TODO-001 created

## 🎥 Video Walkthrough

> **Coming Soon:** A video walkthrough of this tutorial will be available.
> 
> **What to expect:**
> - Live demonstration of RAID management commands
> - Real-world risk and issue examples
> - RAID register filtering techniques
> - Status transition workflows
> 
> **Interested in contributing?** See [VIDEO-PLAN.md](../VIDEO-PLAN.md) for recording guidelines.

## What is RAID?

**RAID** is an acronym for:
- **R**isks - Potential problems that might occur
- **A**ctions - Tasks that need to be completed
- **I**ssues - Problems that are currently happening
- **D**ecisions - Important decisions made

**Why track RAID?**
- **Visibility:** All stakeholders see project constraints
- **Proactive:** Identify risks before they become issues
- **Accountability:** Track actions and decisions
- **Compliance:** ISO 21500 requires risk management

## Steps

### Step 1: Add a Risk

Add a risk to the RAID register:

```bash
python apps/tui/main.py raid add \
  --project TODO-001 \
  --type risk \
  --title "PostgreSQL performance degradation with large datasets" \
  --description "Database queries may slow down significantly when task count exceeds 10,000 records. Risk of poor user experience." \
  --priority high \
  --owner "Database Team"
```

**Expected Output:**
```json
✅ RAID entry added successfully!

Entry Details
{
  "id": "raid-001",
  "project_key": "TODO-001",
  "type": "risk",
  "title": "PostgreSQL performance degradation with large datasets",
  "description": "Database queries may slow down...",
  "priority": "high",
  "status": "open",
  "owner": "Database Team",
  "created_at": "2026-02-03T13:00:00.000Z"
}
```

✅ **Checkpoint:** Risk entry created with ID `raid-001`

### Step 2: Add Multiple Risks

Add more risks to build a realistic register:

```bash
# Risk 2: Security
python apps/tui/main.py raid add \
  --project TODO-001 \
  --type risk \
  --title "XSS vulnerabilities in task description field" \
  --description "User-generated content not properly sanitized, risk of cross-site scripting attacks" \
  --priority high \
  --owner "Security Team"

# Risk 3: Timeline
python apps/tui/main.py raid add \
  --project TODO-001 \
  --type risk \
  --title "React 19 migration may cause delays" \
  --description "New React version has breaking changes, migration could take 2-3 weeks longer than planned" \
  --priority medium \
  --owner "Frontend Lead"
```

✅ **Checkpoint:** Three risks added to the register

### Step 3: Add Actions

Add action items that need to be completed:

```bash
# Action 1: Design review
python apps/tui/main.py raid add \
  --project TODO-001 \
  --type action \
  --title "Complete UI/UX design review with stakeholders" \
  --description "Schedule and conduct design review meeting, gather feedback, iterate on mockups" \
  --priority high \
  --owner "Design Team" \
  --due-date "2026-02-10"

# Action 2: Security audit
python apps/tui/main.py raid add \
  --project TODO-001 \
  --type action \
  --title "Conduct security audit of authentication flow" \
  --description "Third-party penetration testing for JWT implementation and session management" \
  --priority high \
  --owner "Security Team" \
  --due-date "2026-02-15"

# Action 3: Performance testing
python apps/tui/main.py raid add \
  --project TODO-001 \
  --type action \
  --title "Run load tests with 1000+ concurrent users" \
  --description "Use JMeter to simulate high traffic, identify bottlenecks, optimize API endpoints" \
  --priority medium \
  --owner "QA Team" \
  --due-date "2026-02-20"
```

✅ **Checkpoint:** Three actions added with due dates

### Step 4: Add an Issue

Add a current issue:

```bash
python apps/tui/main.py raid add \
  --project TODO-001 \
  --type issue \
  --title "Docker build failing on Windows environments" \
  --description "Node modules installation fails with EPERM errors on Windows. Affects 3 team members. Workaround: use WSL2." \
  --priority high \
  --owner "DevOps Lead"
```

✅ **Checkpoint:** Issue logged

### Step 5: Add Decisions

Document important decisions:

```bash
# Decision 1: Database choice
python apps/tui/main.py raid add \
  --project TODO-001 \
  --type decision \
  --title "Use PostgreSQL instead of MongoDB for data storage" \
  --description "Decision rationale: Need ACID compliance for task management. Relational model better suits our data. Team has more PostgreSQL experience." \
  --owner "Tech Lead" \
  --context "Architecture meeting on 2026-02-01"

# Decision 2: Testing strategy
python apps/tui/main.py raid add \
  --project TODO-001 \
  --type decision \
  --title "Adopt Jest + React Testing Library for frontend tests" \
  --description "Decision: Use Jest for unit tests, RTL for component tests, Playwright for E2E. Target 80% code coverage." \
  --owner "QA Lead" \
  --context "Sprint planning meeting"
```

✅ **Checkpoint:** Two decisions documented

### Step 6: List All RAID Entries

View all RAID entries:

```bash
python apps/tui/main.py raid list --project TODO-001
```

**Expected Output:**
```json
RAID Register for TODO-001 (9 entries)

[
  {
    "id": "raid-001",
    "type": "risk",
    "title": "PostgreSQL performance degradation...",
    "priority": "high",
    "status": "open",
    "owner": "Database Team"
  },
  {
    "id": "raid-002",
    "type": "risk",
    "title": "XSS vulnerabilities...",
    "priority": "high",
    "status": "open",
    "owner": "Security Team"
  },
  ...
]
```

✅ **Checkpoint:** All 9 entries listed

### Step 7: Filter RAID Entries

Filter by type:

```bash
# List only risks
python apps/tui/main.py raid list --project TODO-001 --type risk
```

**Expected Output:** Only 3 risk entries shown.

```bash
# List only actions
python apps/tui/main.py raid list --project TODO-001 --type action
```

**Expected Output:** Only 3 action entries shown.

```bash
# List only high priority
python apps/tui/main.py raid list --project TODO-001 --priority high
```

**Expected Output:** All high-priority entries (risks, actions, issues).

✅ **Checkpoint:** Filtering works correctly

### Step 8: Update Entry Status

Mark an action as completed:

```bash
python apps/tui/main.py raid update \
  --project TODO-001 \
  --id raid-004 \
  --status closed \
  --resolution "Design review completed. Stakeholders approved mockups with minor changes."
```

**Expected Output:**
```json
✅ RAID entry updated successfully!

Updated Entry
{
  "id": "raid-004",
  "status": "closed",
  "closed_at": "2026-02-03T13:10:00.000Z",
  "resolution": "Design review completed..."
}
```

✅ **Checkpoint:** Action marked as closed

### Step 9: View Entry Details

Get detailed view of an entry:

```bash
python apps/tui/main.py raid show --project TODO-001 --id raid-001
```

**Expected Output:**
```json
RAID Entry: raid-001

{
  "id": "raid-001",
  "project_key": "TODO-001",
  "type": "risk",
  "title": "PostgreSQL performance degradation with large datasets",
  "description": "Database queries may slow down significantly...",
  "priority": "high",
  "status": "open",
  "owner": "Database Team",
  "created_at": "2026-02-03T13:00:00.000Z",
  "updated_at": "2026-02-03T13:00:00.000Z",
  "history": [
    {
      "action": "created",
      "timestamp": "2026-02-03T13:00:00.000Z",
      "user": "system"
    }
  ]
}
```

✅ **Checkpoint:** Entry details displayed with history

### Step 10: Export RAID Register

Export to JSON for reporting:

```bash
python apps/tui/main.py raid export \
  --project TODO-001 \
  --format json \
  --output todo-raid-register.json
```

**Expected Output:**
```
✅ RAID register exported successfully!

Export Details
{
  "project_key": "TODO-001",
  "output_file": "todo-raid-register.json",
  "entries_count": 9,
  "format": "json",
  "created_at": "2026-02-03T13:15:00.000Z"
}
```

View the export:
```bash
cat todo-raid-register.json | jq '.[] | {type, title, priority, status}'
```

✅ **Checkpoint:** RAID register exported

## What You've Learned

Congratulations! You've completed the RAID Management tutorial. You now know:

✅ RAID concepts (Risks, Actions, Issues, Decisions)  
✅ How to add RAID entries with `raid add`  
✅ How to list entries with `raid list`  
✅ How to filter by type and priority  
✅ How to update entry status with `raid update`  
✅ How to view details with `raid show`  
✅ How to export the register with `raid export`

## Key Concepts Review

| Concept | Description |
|---------|-------------|
| **Risk** | Potential problem that might occur |
| **Action** | Task that needs completion |
| **Issue** | Current problem happening now |
| **Decision** | Important choice made |
| **Priority** | low, medium, high, critical |
| **Status** | open, in-progress, closed |

## Best Practices

### Writing Good RAID Entries

**Risks:**
- State the risk clearly: "X might happen"
- Include probability and impact
- Propose mitigation strategy
- Assign owner for monitoring

**Actions:**
- Use action verbs: "Complete", "Conduct", "Review"
- Set realistic due dates
- Assign clear owners
- Break large actions into smaller tasks

**Issues:**
- Describe current impact
- Include workarounds if available
- Escalate high-priority issues
- Link to related risks

**Decisions:**
- Document rationale
- Include alternatives considered
- Note who made the decision
- Add context (meeting, discussion)

## Next Steps

1. **[Tutorial 05: Full Lifecycle](05-full-lifecycle.md)** - Complete ISO 21500 workflow (30 min)
2. **[GUI Workflow States](../gui-basics/05-workflow-states.md)** - Visualize RAID in web UI (20 min)
3. **[Advanced: Automation](../advanced/03-automation-scripting.md)** - Bulk RAID entry scripts (30 min)

**Recommended next:** Tutorial 05 - Full Lifecycle

## Reference

### Quick Command Reference

```bash
# Add entry
python apps/tui/main.py raid add \
  --project <KEY> \
  --type <risk|action|issue|decision> \
  --title "<TITLE>" \
  --description "<DESC>" \
  --priority <low|medium|high|critical> \
  --owner "<OWNER>"

# List entries
python apps/tui/main.py raid list --project <KEY>
python apps/tui/main.py raid list --project <KEY> --type risk
python apps/tui/main.py raid list --project <KEY> --priority high

# Show entry
python apps/tui/main.py raid show --project <KEY> --id <ID>

# Update entry
python apps/tui/main.py raid update \
  --project <KEY> \
  --id <ID> \
  --status <open|in-progress|closed>

# Export register
python apps/tui/main.py raid export \
  --project <KEY> \
  --format <json|csv|markdown> \
  --output <FILE>
```

## Troubleshooting

See [Troubleshooting Guide](../shared/troubleshooting.md) for common issues.

## Success Checklist

- [ ] Add risk entries with different priorities
- [ ] Add action entries with due dates
- [ ] Add issue and decision entries
- [ ] List and filter RAID entries
- [ ] Update entry status
- [ ] Export RAID register

If complete, you're ready for [Tutorial 05: Full Lifecycle](05-full-lifecycle.md)!

---

**Tutorial Series:** [TUI Basics](../README.md#tui-basics) | **Previous:** [03 - Artifact Workflow](03-artifact-workflow.md) | **Next:** [05 - Full Lifecycle](05-full-lifecycle.md)
