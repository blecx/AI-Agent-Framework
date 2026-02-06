# TUI + GUI Hybrid Workflows

**Estimated Time:** 20 minutes  
**Difficulty:** Advanced  
**Prerequisites:** TUI Basics, GUI Basics tutorials

## 🎥 Video Walkthrough

> **Coming Soon:** A video walkthrough of this tutorial will be available.
> 
> **What to expect:**
> - Live demonstration of hybrid workflows
> - Interface switching techniques
> - Real-world productivity examples
> - When to use TUI vs GUI decision-making
> 
> **Interested in contributing?** See [VIDEO-PLAN.md](../VIDEO-PLAN.md) for recording guidelines.

## Overview

This tutorial demonstrates how to combine the TUI (Terminal User Interface) and GUI (Graphical User Interface) to maximize productivity. Learn when to use each interface and how to leverage their complementary strengths.

## When to Use Which Interface

| Task | Best Interface | Reason |
|------|---------------|--------|
| Bulk operations | TUI | Scriptable, faster for repeated tasks |
| Visual exploration | GUI | Better UX, easier navigation |
| Proposal review | GUI | Diff viewer shows changes clearly |
| RAID bulk entry | TUI | Faster data entry with scripts |
| Initial project setup | TUI | Automation-friendly, reproducible |
| Artifact browsing | GUI | Visual file tree and preview |
| Script-based workflows | TUI | Can be automated in CI/CD |
| Ad-hoc exploration | GUI | Point-and-click is faster |

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Choose the appropriate interface for different tasks
2. Switch seamlessly between TUI and GUI
3. Automate common workflows with TUI scripts
4. Verify results visually in the GUI
5. Build hybrid workflows that combine both interfaces

## Part 1: Setup and Basic Hybrid Flow

### Step 1: Ensure Both Interfaces Are Running

Start the full stack (API + TUI + GUI):

```bash
# Terminal 1: Start API server
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Terminal 2: TUI is available immediately
cd apps/tui
python main.py --help

# Terminal 3: Start GUI dev server (optional, or use Docker)
cd apps/web
npm run dev
```

**Verify:**
- API health: `curl http://localhost:8000/health`
- TUI: `python apps/tui/main.py projects list`
- GUI: Open http://localhost:5173 (or :8080 if using Docker)

### Step 2: Create Project via TUI (Fast)

```bash
cd apps/tui
python main.py projects create \
  --key "TODO" \
  --name "Todo App MVP" \
  --description "Task management application with user authentication"
```

**Output:**
```
✓ Project created: TODO
  Name: Todo App MVP
  Workflow State: Initiating
  Path: projectDocs/TODO/
```

**Why TUI?** Creating a project via TUI is faster than clicking through GUI forms, and the command can be saved in a script for reproducibility.

### Step 3: Verify in GUI (Visual Confirmation)

1. Open http://localhost:5173 in your browser
2. Select "TODO" from the project dropdown
3. Observe:
   - Project name and description displayed
   - Workflow state: "Initiating"
   - Empty RAID register (no entries yet)
   - Empty artifacts list

**Why GUI?** Visual confirmation is easier than parsing TUI output. You can see the project structure at a glance.

## Part 2: Hybrid Workflow for RAID Management

### Step 4: Bulk-Add RAID Entries via TUI

Create a file with initial risks and issues:

```bash
cat > /tmp/raid-entries.txt << 'EOF'
# Initial project risks
risk,High,Database scaling under high load,Plan for horizontal sharding
risk,Medium,Third-party auth API downtime,Implement retry logic with exponential backoff
risk,Low,UI framework version upgrade,Lock dependencies in package.json

# Known issues from planning
issue,Medium,User story for bulk task import is unclear,Schedule stakeholder workshop
issue,Low,Performance baseline not yet established,Add benchmark tests in sprint 2
EOF
```

Add entries via TUI script:

```bash
cd apps/tui

# Add risks
python main.py raid add --project TODO --type risk --severity High \
  --description "Database scaling under high load" \
  --mitigation "Plan for horizontal sharding"

python main.py raid add --project TODO --type risk --severity Medium \
  --description "Third-party auth API downtime" \
  --mitigation "Implement retry logic with exponential backoff"

python main.py raid add --project TODO --type risk --severity Low \
  --description "UI framework version upgrade" \
  --mitigation "Lock dependencies in package.json"

# Add issues
python main.py raid add --project TODO --type issue --severity Medium \
  --description "User story for bulk task import is unclear" \
  --mitigation "Schedule stakeholder workshop"

python main.py raid add --project TODO --type issue --severity Low \
  --description "Performance baseline not yet established" \
  --mitigation "Add benchmark tests in sprint 2"
```

**Output (per command):**
```
✓ RAID entry added: RAID-001 (Risk)
  Severity: High
  Description: Database scaling under high load
```

**Why TUI?** Entering multiple RAID items is much faster via CLI, especially when reading from a prepared list. Can be scripted for recurring patterns.

### Step 5: Review and Update in GUI

1. Refresh the GUI (or it auto-updates if WebSocket is enabled)
2. Navigate to the RAID Register section
3. Observe all 5 entries displayed in a table:
   - Type (Risk/Issue with color coding)
   - Severity (High/Medium/Low with badges)
   - Description (truncated with "Read more" link)
   - Status (Open/Mitigated)
   - Actions (Edit, Resolve, Delete buttons)

4. Click on a risk entry to view details
5. Use the GUI form to update severity or add notes
6. Save changes

**Why GUI?** The GUI provides a clearer overview of all RAID entries with visual indicators (colors, badges). Updating individual entries is easier with form fields than CLI flags.

### Step 6: Verify Updates in TUI

```bash
cd apps/tui
python main.py raid list --project TODO
```

**Output:**
```
TODO RAID Register (5 entries)

Risks (3):
  RAID-001 [High]    Database scaling under high load
               Status: Open
               Mitigation: Plan for horizontal sharding
  RAID-002 [Medium]  Third-party auth API downtime
               Status: Open
               Mitigation: Implement retry logic with exponential backoff
  ...

Issues (2):
  RAID-004 [Medium]  User story for bulk task import is unclear
               Status: Open
               Mitigation: Schedule stakeholder workshop
  ...
```

**Observation:** Changes made in the GUI are immediately visible in the TUI (both read from the same `projectDocs/TODO/` git repository).

## Part 3: Command Proposals with Hybrid Review

### Step 7: Propose Command via TUI

Update workflow state to "Planning":

```bash
cd apps/tui
python main.py workflow update --project TODO --state Planning
```

**Output:**
```
✓ Proposal created: proposals/workflow-update-YYYYMMDD-HHMMSS.json
  Changes:
    workflow.state: Initiating → Planning
  
  Review with: python main.py proposals show <id>
  Apply with: python main.py proposals apply <id>
  Or view in GUI for diff visualization
```

**Why TUI?** Proposing commands via TUI is faster when you know exactly what you want to do. No need to navigate through GUI menus.

### Step 8: Review Proposal in GUI (Best Experience)

1. In the GUI, a notification appears: "New proposal available"
2. Click "Review Proposal"
3. View the diff in a side-by-side comparison:
   - **Before (Left):** `"state": "Initiating"`
   - **After (Right):** `"state": "Planning"`
4. Review the command metadata:
   - Command: `workflow update`
   - User: `<your-user>`
   - Timestamp: `2026-02-03 14:23:45`
5. Decision buttons at bottom: "Apply" or "Reject"

**Why GUI?** The GUI's diff viewer is far superior to text-based diffs in the terminal. Color-coded changes and side-by-side comparison make review much faster.

### Step 9: Apply Proposal via TUI (Automation-Friendly)

Instead of clicking "Apply" in GUI, apply via TUI for scriptability:

```bash
cd apps/tui
python main.py proposals list --project TODO
# Note the proposal ID from output (e.g., proposal-001)

python main.py proposals apply --project TODO --id proposal-001
```

**Output:**
```
✓ Proposal applied: proposal-001
  Workflow state updated: Initiating → Planning
  Git commit: [TODO] Workflow state updated to Planning
```

**Why TUI?** Applying via TUI allows you to automate the apply step in a script (e.g., "auto-apply low-risk proposals"). The GUI is for review; the TUI is for automation.

## Part 4: Artifact Management Hybrid Workflow

### Step 10: Generate Artifacts via TUI

Create multiple artifacts in batch:

```bash
cd apps/tui

# Generate project charter
python main.py artifacts create --project TODO \
  --type charter \
  --title "Todo App Project Charter" \
  --prompt "Create a project charter for a todo application with user auth"

# Generate software requirements specification
python main.py artifacts create --project TODO \
  --type requirements \
  --title "Software Requirements Specification" \
  --prompt "Detail functional and non-functional requirements for a task management app"

# Generate architecture design document
python main.py artifacts create --project TODO \
  --type design \
  --title "System Architecture Design" \
  --prompt "Design a scalable architecture for a web-based todo application"
```

**Output (per command):**
```
✓ Artifact created: artifacts/charter.md
  Title: Todo App Project Charter
  Generated with LLM: Yes
  Size: 3.2 KB
```

**Why TUI?** Generating multiple artifacts is faster via CLI. You can script the entire artifact generation sequence.

### Step 11: Browse and Edit in GUI

1. In the GUI, navigate to the "Artifacts" section
2. View all artifacts in a tree view:
   ```
   projectDocs/TODO/
   ├── artifacts/
   │   ├── charter.md
   │   ├── requirements.md
   │   └── design.md
   ├── raid/
   │   └── register.json
   └── workflow/
       └── state.json
   ```
3. Click on `charter.md` to view content
4. Use the inline editor to make changes:
   - Add a section
   - Fix formatting
   - Update dates
5. Save changes (creates a git commit)

**Why GUI?** The GUI's markdown editor with preview is much better for editing documents than a CLI text editor. Syntax highlighting, preview, and easy navigation make editing faster.

### Step 12: Verify Artifact Changes via TUI

```bash
cd projectDocs/TODO
git log --oneline -5
```

**Output:**
```
a1b2c3d [TODO] Updated charter.md - added success criteria section
d4e5f6g [TODO] Created artifact: design.md
h7i8j9k [TODO] Created artifact: requirements.md
l0m1n2o [TODO] Created artifact: charter.md
p3q4r5s [TODO] Workflow state updated to Planning
```

**Observation:** Every GUI edit creates a git commit, visible via git log. The TUI and GUI share the same underlying git repository.

## Part 5: Advanced Hybrid Patterns

### Pattern 1: TUI for Automation, GUI for Verification

**Use Case:** Daily standup report generation

```bash
#!/bin/bash
# daily-standup-report.sh

PROJECT="TODO"
DATE=$(date +%Y-%m-%d)

# Generate report via TUI
cd apps/tui
python main.py reports standup --project $PROJECT --date $DATE > /tmp/standup-$DATE.md

# Open in GUI for review
echo "✓ Report generated: /tmp/standup-$DATE.md"
echo "→ View in GUI: http://localhost:5173/reports"
```

**Benefit:** Automate report generation, but review the formatted output in the GUI before sharing.

### Pattern 2: GUI for Exploration, TUI for Execution

**Use Case:** Gap assessment workflow

1. **GUI:** Browse current project state, identify missing artifacts
2. **TUI:** Run `assess-gaps` command to get LLM recommendations
3. **GUI:** Review gap assessment report with visual indicators
4. **TUI:** Execute commands to create missing artifacts in batch

```bash
cd apps/tui
python main.py assess-gaps --project TODO

# Output suggests missing artifacts
# Use TUI to batch-create them
python main.py artifacts create --project TODO --type test-plan --title "Test Plan"
python main.py artifacts create --project TODO --type deployment --title "Deployment Guide"
```

### Pattern 3: Scripted Workflow with GUI Checkpoints

**Use Case:** Multi-project setup

```bash
#!/bin/bash
# setup-projects.sh

PROJECTS=("PROJ-A" "PROJ-B" "PROJ-C")

for PROJ in "${PROJECTS[@]}"; do
  echo "Setting up $PROJ..."
  
  # Create project
  python apps/tui/main.py projects create --key "$PROJ" --name "Project $PROJ"
  
  # Add initial RAID entries
  python apps/tui/main.py raid add --project "$PROJ" --type risk --severity Medium \
    --description "Initial project risk" --mitigation "To be assessed"
  
  # Update to Planning state
  python apps/tui/main.py workflow update --project "$PROJ" --state Planning
  
  echo "→ Verify in GUI: http://localhost:5173?project=$PROJ"
  read -p "Press Enter to continue to next project..."
done
```

**Benefit:** Automate repetitive setup tasks, but pause at checkpoints to verify in GUI before proceeding.

## Part 6: Troubleshooting Hybrid Workflows

### Issue: GUI Not Showing TUI Changes

**Symptoms:**
- Run a TUI command
- GUI doesn't update immediately

**Causes:**
1. Browser cache (GUI is cached static site)
2. WebSocket connection lost (if real-time updates are enabled)
3. API server restarted (state reload needed)

**Solution:**
```bash
# Hard refresh in browser: Ctrl+Shift+R (Linux/Windows) or Cmd+Shift+R (Mac)
# Or check API is running:
curl http://localhost:8000/health

# Check project state via API directly:
curl http://localhost:8000/api/projects/TODO
```

### Issue: TUI Commands Fail After GUI Edits

**Symptoms:**
- Edit file in GUI
- TUI command returns "Git merge conflict" error

**Causes:**
- Git working directory is dirty (uncommitted changes)
- Proposal system detected conflicting changes

**Solution:**
```bash
cd projectDocs/TODO
git status

# If there are uncommitted changes:
git add -A
git commit -m "[TODO] Manual edits via GUI"

# Then retry TUI command
cd ../../apps/tui
python main.py <command>
```

### Issue: Different Results in TUI vs GUI

**Symptoms:**
- TUI shows 5 RAID entries
- GUI shows 3 RAID entries

**Causes:**
- GUI is filtering (e.g., only showing "Open" items)
- Different API endpoints being called
- Cache inconsistency

**Solution:**
```bash
# Check raw data:
cat projectDocs/TODO/raid/register.json | jq '.entries | length'

# Clear browser cache and reload GUI
# Verify API endpoint:
curl http://localhost:8000/api/projects/TODO/raid
```

## Best Practices for Hybrid Workflows

### 1. Use TUI for Bulk Operations

```bash
# Bad: Clicking "Add RAID Entry" 20 times in GUI
# Good: Script it
for i in {1..20}; do
  python main.py raid add --project TODO --type risk --severity Low \
    --description "Risk $i" --mitigation "Mitigation $i"
done
```

### 2. Use GUI for Visual Review

```bash
# Bad: Reviewing a complex diff in terminal
python main.py proposals show proposal-123 | less

# Good: Open GUI and use visual diff viewer
echo "Review at: http://localhost:5173/proposals/123"
```

### 3. Document Your Hybrid Workflows

Create a `WORKFLOWS.md` file in your project:

```markdown
# Project Workflows

## Daily Standup
1. Generate report: `./scripts/daily-standup.sh`
2. Review in GUI: http://localhost:5173/reports
3. Copy to Slack

## Weekly RAID Review
1. Export current RAID: `python apps/tui/main.py raid export --project TODO`
2. Review in GUI: http://localhost:5173/raid
3. Update severities as needed
4. Generate report: `python apps/tui/main.py reports raid --project TODO`
```

### 4. Leverage Both Interfaces' Strengths

| Task | Interface | Command/Action |
|------|-----------|---------------|
| Create 10 projects | TUI | `for` loop with `projects create` |
| Review project dashboard | GUI | Open project selector, browse visually |
| Bulk RAID entry | TUI | Script with `raid add` |
| Update single RAID entry | GUI | Click entry, edit form, save |
| Generate artifact | TUI | `artifacts create` with prompt |
| Edit artifact content | GUI | Markdown editor with preview |
| Apply proposal | TUI | `proposals apply` (for automation) |
| Review proposal diff | GUI | Visual diff viewer |
| Run gap assessment | TUI | `assess-gaps --project TODO` |
| View gap report | GUI | Formatted report with visual indicators |

## Summary

**Key Takeaways:**

1. **TUI excels at:**
   - Bulk operations and batch processing
   - Scriptable, repeatable workflows
   - Automation and CI/CD integration
   - Fast command execution for known tasks

2. **GUI excels at:**
   - Visual exploration and browsing
   - Editing rich content (Markdown, forms)
   - Reviewing diffs and proposals
   - Ad-hoc tasks and learning the system

3. **Hybrid workflows combine:**
   - TUI for speed and automation
   - GUI for clarity and ease of use
   - Git as the shared source of truth
   - API as the unified backend

4. **Best practices:**
   - Choose the right tool for each task
   - Script repetitive TUI tasks
   - Verify results visually in GUI
   - Document your hybrid workflows
   - Use git to understand what changed

## Next Steps

- **Practice:** Try converting your current GUI workflows to hybrid (TUI + GUI)
- **Advanced:** Complete Tutorial 02 (Full ISO 21500 Lifecycle)
- **Automation:** Complete Tutorial 03 (Automation Scripting)
- **Customize:** Create your own hybrid workflow scripts for your team's needs

## Additional Resources

- [TUI Command Reference](../tui-basics/03-tui-command-cheatsheet.md)
- [GUI Feature Guide](../gui-basics/02-web-interface-tour.md)
- [API Documentation](http://localhost:8000/docs)
- [Git Best Practices for Project Docs](../../development.md#git-workflow)
