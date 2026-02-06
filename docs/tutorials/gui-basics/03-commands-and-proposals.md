# GUI Commands and Proposals

**Duration:** 20 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Execute commands and review proposals using the web interface. This comprehensive tutorial walks you through the propose/apply workflow pattern, teaching you how to use the CommandPanel component, review proposals in the ProposalModal, view diff previews, and manage the complete artifact generation lifecycle through the GUI.

## Learning Objectives

By the end of this tutorial, you will:
- Understand the propose/apply workflow pattern in the GUI
- Use CommandPanel to propose commands with detailed descriptions
- Review proposal details in ProposalModal thoroughly
- Inspect artifact previews before applying changes
- View diff previews to understand what will change
- Apply proposals to commit artifacts to the project
- Reject proposals when changes aren't suitable
- Navigate proposal history and status
- Compare GUI workflow with TUI equivalent
- Troubleshoot common proposal workflow issues

## Prerequisites

- **Completed:** [Tutorial 02: Project Creation](02-project-creation.md)
- Project TODO-001 created and selected in UI
- Browser open to http://localhost:8080
- Web UI showing TODO-001 project details
- Understanding of Git concepts (commits, diffs) helpful but not required

### Quick Verification

Verify your environment before starting:

```bash
# Check project exists
docker exec -it $(docker compose ps -q api) ls projectDocs/TODO-001

# Expected: Directory exists (even if empty)
```

✅ **Pre-flight Checkpoint:** TODO-001 project visible in GUI sidebar

## The Propose/Apply Pattern in GUI

The AI-Agent Framework uses a **two-step workflow** for all artifact generation:

1. **Propose:** Generate artifacts as a proposal (doesn't modify project yet)
2. **Review:** Inspect proposed changes in modal dialog
3. **Apply or Reject:** Accept changes (commits to Git) or discard them

**Why this pattern matters:**
- **Safety:** Preview all changes before committing
- **Collaboration:** Team members can review proposals
- **Version Control:** Each application creates atomic Git commit
- **Rollback:** Easy to revert by reverting Git commits
- **Audit Trail:** All proposals logged with timestamps and descriptions

**GUI Workflow Visualization:**
```
User Action              UI Component           Backend Action
───────────────────────────────────────────────────────────────
Select command      →    CommandPanel       →   Validate command
Enter description   →    Description field  →   Store context
Click "Propose"     →    API POST request   →   Generate artifacts
                    ↓
Wait for proposal   →    Loading spinner    →   LLM/template processing
Proposal created    →    ProposalModal      →   Artifacts in temp storage
                    ↓
Review artifacts    →    Artifact previews  →   (No backend action)
View diff           →    Diff viewer        →   Git diff computation
                    ↓
Click "Apply"       →    API POST request   →   Write files + Git commit
Success message     →    Toast notification →   Artifacts persisted
                    ↓
Artifacts visible   →    ArtifactsList      →   (Read from disk)
```

## Steps

### Step 1: Access and Understand CommandPanel

#### 1.1: Locate CommandPanel

1. Ensure TODO-001 is selected in sidebar (highlighted in blue)
2. Main content area should show project dashboard
3. Find "Commands" tab or section (may be labeled "Execute Command")
4. Click to expand CommandPanel if collapsed

**CommandPanel Layout:**
```
┌─────────────────────────────────────────────┐
│  Execute Command                            │
├─────────────────────────────────────────────┤
│  Command: [Dropdown ▼]                      │
│           ┌─────────────────────────────┐   │
│           │ create_charter             │   │
│           │ assess_gaps                 │   │
│           │ define_wbs                  │   │
│           │ plan_schedule               │   │
│           └─────────────────────────────┘   │
│                                             │
│  Description:                               │
│  ┌─────────────────────────────────────┐   │
│  │ Enter command context here...       │   │
│  │                                     │   │
│  │ (Multi-line textarea)               │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [Propose Command]                          │
│                                             │
│  Recent Proposals (0)                       │
│  No proposals yet. Create one above!        │
└─────────────────────────────────────────────┘
```

✅ **Checkpoint 1.1:** CommandPanel visible with dropdown and description field

**Screenshot Reference:** `docs/screenshots/gui-03-commandpanel-overview.png`

#### 1.2: Explore Available Commands

Click on the Command dropdown to see all available commands:

**Available Commands (Step 1 Features):**
- **create_charter** - Generate project charter document with objectives, scope, stakeholders
- **assess_gaps** - Analyze project requirements and identify gaps
- **define_wbs** - Create Work Breakdown Structure
- **plan_schedule** - Generate project schedule

**Command Descriptions (shown on hover):**
```
create_charter: Creates initial project charter including:
  - Project objectives and success criteria
  - Stakeholder register
  - Assumptions log
  - High-level scope definition
  
assess_gaps: Analyzes current project state and identifies:
  - Missing requirements
  - Undefined scope areas
  - Stakeholder communication gaps
  - Resource planning needs
```

**Step 2 Features (REST API Available):**
- Template management (CRUD operations)
- Blueprint selection and management
- Artifact generation with custom templates
- Proposal workflow enhancements

See [Step 2 Status](../../../planning/step-2-complete-status.md) for REST API documentation.

✅ **Checkpoint 1.2:** Explored command dropdown, understand command purposes

#### 1.3: CommandPanel Keyboard Shortcuts

**Efficiency Tips:**
| Shortcut | Action |
|----------|--------|
| `Ctrl+K` or `/` | Focus command dropdown |
| `Ctrl+D` | Focus description field |
| `Ctrl+Enter` | Submit proposal (when fields valid) |
| `Esc` | Close dropdown or clear selection |
| `Tab` | Navigate between fields |

✅ **Checkpoint 1.3:** Tested keyboard shortcuts for faster workflow

### Step 2: Propose Your First Command (Project Charter)

Let's create a project charter for the Todo Application.

#### 2.1: Select create_charter Command

1. Click Command dropdown
2. Select "create_charter" from list
3. Dropdown closes, showing selected command
4. Description field becomes active (cursor moves there automatically)

**UI Feedback:**
- Command dropdown shows "create_charter"
- Description placeholder changes to: "Describe the charter requirements..."
- "Propose" button remains disabled until description entered

✅ **Checkpoint 2.1:** create_charter command selected

#### 2.2: Write Detailed Description

Enter a comprehensive description (best practice for better AI-generated artifacts):

**Example Description (Good):**
```
Generate initial project charter for Todo Application MVP. 

Context:
- Building a task management web app for small teams (5-20 users)
- Tech stack: React 19 frontend, Node.js 20 API, PostgreSQL 16 database
- MVP features: CRUD tasks, filtering, due dates, user assignment
- Target users: Software development teams, product managers
- Success criteria: Users can create and track tasks end-to-end

Stakeholders:
- Development team (3 engineers)
- Product owner (1)
- End users (initial 10 beta testers)

Timeline: 8-week MVP sprint
```

**Description Best Practices:**
- **Be specific:** Include concrete details about requirements
- **Provide context:** Explain project background
- **List stakeholders:** Name key project participants
- **Define success:** What does "done" look like?
- **Mention constraints:** Time, budget, resource limitations

**Description Character Limits:**
- Minimum: 50 characters (enforced)
- Recommended: 200-500 characters
- Maximum: 2000 characters

✅ **Checkpoint 2.2:** Description entered (200+ characters recommended)

**Screenshot Reference:** `docs/screenshots/gui-03-proposal-description.png`

#### 2.3: Submit Proposal

1. Review command + description one more time
2. Click blue "Propose Command" button
3. Button shows loading spinner: "Proposing..."
4. Wait 3-15 seconds (depending on LLM/template processing)

**What Happens Behind the Scenes:**
1. Frontend validates inputs (command selected, description non-empty)
2. POST request sent to `/api/commands/propose`
3. Backend validates request structure
4. Command service generates artifacts (via LLM or templates)
5. Artifacts stored in temporary proposal storage
6. Proposal ID generated and returned
7. ProposalModal opens automatically

**Expected Processing Time:**
- Template-based: 2-5 seconds
- LLM-based (if configured): 10-30 seconds
- Network latency: + 0.5-2 seconds

**UI Loading States:**
```
Proposing command...  [Spinner animation]
Generating artifacts...
Almost ready...
```

✅ **Checkpoint 2.3:** Proposal submitted, waiting for modal to appear

**Troubleshooting Step 2:**
- **Symptom:** "Propose" button stays disabled
  - **Cause:** Missing description or command not selected
  - **Fix:** Ensure both dropdown has selection AND description has 50+ characters

- **Symptom:** Request times out after 60 seconds
  - **Cause:** LLM service unavailable or slow
  - **Fix:** Check LLM Studio status, or wait and retry (API falls back to templates)

- **Symptom:** Error: "Command not found"
  - **Cause:** Backend doesn't recognize command name
  - **Fix:** Refresh page, ensure API version matches web UI version

### Step 3: Review Proposal in ProposalModal

When proposal creation succeeds, ProposalModal appears as an overlay.

#### 3.1: ProposalModal Layout and Components

**Modal Structure:**
```
┌──────────────────────────────────────────────────────────┐
│  Proposal Details                             [X] Close  │
├──────────────────────────────────────────────────────────┤
│  Proposal ID: prop-a1b2c3d4                              │
│  Command: create_charter                                 │
│  Status: PENDING                                         │
│  Created: 2026-02-06 14:45:30                           │
│  Description: Generate initial project charter...       │
├──────────────────────────────────────────────────────────┤
│  Artifacts Preview (3 files)                             │
│  ├─ artifacts/charters/project-charter.md      8.2 KB   │
│  ├─ artifacts/charters/stakeholder-register.md 2.1 KB   │
│  └─ artifacts/charters/assumptions-log.md      1.5 KB   │
│                                                          │
│  [View Diff] [Preview File]                             │
├──────────────────────────────────────────────────────────┤
│  Actions                                                 │
│  [Apply Proposal] [Reject Proposal] [Download Preview]  │
└──────────────────────────────────────────────────────────┘
```

**Modal Sections Explained:**

1. **Header:**
   - Proposal ID (unique identifier, format: `prop-{8-char-hash}`)
   - Command name
   - Status badge (PENDING, APPLIED, REJECTED)
   - Creation timestamp
   - Close button (X) - closes modal without applying

2. **Description Section:**
   - Shows your original proposal description
   - Read-only (cannot edit after proposal created)

3. **Artifacts Preview Section:**
   - List of all files that will be created
   - File paths relative to project root
   - File sizes (estimated)
   - File type icons (Markdown, JSON, etc.)

4. **Action Buttons:**
   - Apply Proposal (green) - commits artifacts
   - Reject Proposal (red) - discards proposal
   - Download Preview (blue) - download artifacts ZIP without applying

✅ **Checkpoint 3.1:** ProposalModal opened, showing proposal details

**Screenshot Reference:** `docs/screenshots/gui-03-proposal-modal.png`

#### 3.2: Inspect Artifact List

Click on each artifact name to see preview:

**Artifact 1: project-charter.md**
```markdown
# Project Charter: Todo Application MVP

## Project Overview

**Project Name:** Todo Application MVP  
**Project Manager:** [TBD]  
**Start Date:** 2026-02-06  
**Target Completion:** 2026-04-02 (8 weeks)

## Business Case

Small software teams need simple, effective task management...

## Objectives

1. Deliver functional CRUD task management system
2. Support 5-20 concurrent users
3. Integrate with existing authentication

## Success Criteria

- Users can create/edit/delete tasks
- Filter by status/priority/assignee
- 99% uptime during pilot
- <200ms average response time

... (continues for ~300 lines)
```

**Artifact 2: stakeholder-register.md**
```markdown
# Stakeholder Register

| Name | Role | Interest | Influence | Engagement |
|------|------|----------|-----------|------------|
| Product Owner | Decision Maker | High | High | Daily |
| Dev Team | Implementers | High | Medium | Daily |
| End Users | Consumers | High | Low | Weekly |
| QA Team | Quality Gate | Medium | Medium | Sprint |

... (continues)
```

**Artifact 3: assumptions-log.md**
```markdown
# Assumptions Log

## Technical Assumptions

1. **Modern Browser Support:** Users have Chrome 90+, Firefox 88+, or Safari 14+
2. **Database Access:** PostgreSQL 16 instance available
3. **Authentication:** Existing auth system can be integrated
...
```

✅ **Checkpoint 3.2:** Reviewed all artifact previews, content looks reasonable

#### 3.3: View Diff Preview (Git Changes)

Click "View Diff" button to see what Git changes will be made:

**Diff Viewer UI:**
```diff
diff --git a/artifacts/charters/project-charter.md b/artifacts/charters/project-charter.md
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/artifacts/charters/project-charter.md
@@ -0,0 +1,300 @@
+# Project Charter: Todo Application MVP
+
+## Project Overview
...
+
+(Shows full file content with + indicators for new lines)
```

**Diff Viewer Features:**
- Side-by-side view (if file existed before)
- Unified diff view (default for new files)
- Syntax highlighting for Markdown
- Line numbers
- Expand/collapse sections
- Download diff as .patch file

✅ **Checkpoint 3.3:** Viewed diff, understand what changes will be made

**Screenshot Reference:** `docs/screenshots/gui-03-diff-viewer.png`

#### 3.4: Download Preview (Optional)

To review artifacts offline or share with team:

1. Click "Download Preview" button
2. Browser downloads `TODO-001-prop-a1b2c3d4.zip`
3. Extract ZIP to see all artifacts
4. Review in your favorite editor

**ZIP Contents:**
```
TODO-001-prop-a1b2c3d4.zip
├── artifacts/
│   └── charters/
│       ├── project-charter.md
│       ├── stakeholder-register.md
│       └── assumptions-log.md
├── proposal-metadata.json
└── diff.patch
```

✅ **Checkpoint 3.4:** (Optional) Downloaded preview ZIP for offline review

### Step 4: Apply Proposal to Commit Artifacts

Once satisfied with the preview, apply the proposal.

#### 4.1: Click Apply Button

1. In ProposalModal, click green "Apply Proposal" button
2. Confirmation dialog appears (safety check)

**Confirmation Dialog:**
```
┌─────────────────────────────────────────┐
│  Apply Proposal?                        │
├─────────────────────────────────────────┤
│  This will commit 3 files to project    │
│  TODO-001 and create a Git commit.      │
│                                         │
│  Proposal: prop-a1b2c3d4                │
│  Command: create_charter                │
│  Files: 3 artifacts                     │
│                                         │
│  This action cannot be undone           │
│  (except via Git revert).               │
│                                         │
│  [Cancel] [Confirm Apply]               │
└─────────────────────────────────────────┘
```

3. Read confirmation message carefully
4. Click "Confirm Apply" button

✅ **Checkpoint 4.1:** Confirmation dialog appeared

#### 4.2: Wait for Application

**Application Process:**
1. Frontend sends POST to `/api/commands/apply`
2. Backend writes artifacts to `projectDocs/TODO-001/artifacts/`
3. Git stages all files: `git add artifacts/`
4. Git commits: `git commit -m "[TODO-001] Applied proposal: create_charter"`
5. Proposal status updated to "APPLIED"
6. Response returned to frontend

**Expected Application Time:** 1-3 seconds

**UI Loading State:**
```
Applying proposal...  [Progress bar]
Writing artifacts...
Creating Git commit...
Success!
```

#### 4.3: Verify Success

**Success Indicators:**
1. **Toast Notification (Green):**
   ```
   ✅ Proposal applied successfully!
   
   3 artifacts created
   Git commit: abc123def
   ```

2. **ProposalModal Updates:**
   - Status badge changes: PENDING → APPLIED
   - Apply button disabled (grayed out)
   - New badge: "Applied at 2026-02-06 14:46:15"

3. **Artifacts Appear in ArtifactsList:**
   - Navigate to "Artifacts" tab
   - See `artifacts/charters/` folder with 3 files

✅ **Checkpoint 4.3:** Success notification received, proposal marked APPLIED

**Screenshot Reference:** `docs/screenshots/gui-03-apply-success.png`

#### 4.4: Verify Git Commit (Advanced)

For advanced users, verify the Git commit was created:

**Using Docker CLI:**
```bash
# Access project Git repository
docker exec -it $(docker compose ps -q api) sh -c \
  "cd projectDocs/TODO-001 && git log --oneline -1"

# Expected Output:
# abc123d [TODO-001] Applied proposal prop-a1b2c3d4: create_charter
```

**Using GUI (Browser DevTools Console):**
```javascript
fetch('/api/projects/TODO-001/history')
  .then(res => res.json())
  .then(data => console.log('Latest commit:', data.commits[0]));

// Expected Output:
// Latest commit: {hash: 'abc123d', message: '[TODO-001] Applied proposal...', timestamp: '2026-02-06T14:46:15Z'}
```

✅ **Checkpoint 4.4:** Git commit verified in repository

### Step 5: Reject a Proposal (Alternative Workflow)

Sometimes you'll want to reject a proposal instead of applying it. Let's demonstrate this.

#### 5.1: Propose Another Command

1. Return to CommandPanel (close ProposalModal if still open)
2. Select "assess_gaps" command from dropdown
3. Enter description: "Analyze current project requirements and identify gaps"
4. Click "Propose Command"
5. Wait for new ProposalModal to appear

✅ **Checkpoint 5.1:** Second proposal created (assess_gaps)

#### 5.2: Review Proposal (Quick)

**Expected Artifacts for assess_gaps:**
- `artifacts/analysis/gaps-assessment.md` (~5 KB)
- `artifacts/analysis/requirements-gaps.md` (~3 KB)
- `artifacts/analysis/recommendations.md` (~2 KB)

Quickly review the content (don't need to read every line for this demo).

✅ **Checkpoint 5.2:** Reviewed assess_gaps proposal artifacts

#### 5.3: Reject the Proposal

1. Click red "Reject Proposal" button
2. Rejection dialog appears

**Rejection Dialog:**
```
┌─────────────────────────────────────────┐
│  Reject Proposal?                       │
├─────────────────────────────────────────┤
│  Reason for rejection (optional):       │
│  ┌───────────────────────────────────┐  │
│  │ Describe why you're rejecting    │  │
│  │ this proposal...                  │  │
│  └───────────────────────────────────┘  │
│                                         │
│  This will discard all artifacts and    │
│  mark proposal as REJECTED.             │
│                                         │
│  [Cancel] [Confirm Reject]              │
└─────────────────────────────────────────┘
```

3. Enter rejection reason (optional but recommended for audit trail):
   ```
   Gaps analysis not needed yet - still in early charter phase
   ```
4. Click "Confirm Reject" button

✅ **Checkpoint 5.3:** Rejection dialog submitted

#### 5.4: Verify Rejection

**Rejection Success Indicators:**
1. **Toast Notification (Yellow/Warning):**
   ```
   ⚠️ Proposal rejected
   
   Reason: Gaps analysis not needed yet...
   ```

2. **ProposalModal Updates:**
   - Status badge: PENDING → REJECTED
   - Both Apply and Reject buttons disabled
   - Shows rejection reason and timestamp

3. **No Artifacts Created:**
   - Check ArtifactsList - no `artifacts/analysis/` folder
   - Check Git log - no new commit

✅ **Checkpoint 5.4:** Proposal rejected, no artifacts created

**Screenshot Reference:** `docs/screenshots/gui-03-reject-success.png`

### Step 6: View Proposal History

Access historical proposals to audit workflow.

#### 6.1: Navigate to Proposal History

1. In CommandPanel, scroll down to "Recent Proposals" section
2. Or click "View All Proposals" link (if available)
3. Proposal history table appears

**Proposal History Table:**
```
| Proposal ID    | Command         | Status   | Created          | Actions |
|----------------|-----------------|----------|------------------|---------|
| prop-a1b2c3d4  | create_charter  | APPLIED  | Feb 6, 14:45:30 | [View]  |
| prop-e5f6g7h8  | assess_gaps     | REJECTED | Feb 6, 14:50:22 | [View]  |
```

✅ **Checkpoint 6.1:** Proposal history visible with 2 entries

#### 6.2: Re-open Past Proposal

1. Click "View" action button on first proposal (create_charter)
2. ProposalModal opens in read-only mode
3. Shows all original details + "APPLIED" status

**Read-Only Modal Differences:**
- Status badge shows APPLIED (green)
- Apply button replaced with "View Artifacts" link
- Shows applied timestamp and Git commit hash
- Cannot modify or re-apply

✅ **Checkpoint 6.2:** Re-opened past proposal in read-only mode

#### 6.3: Filter Proposal History

**Filter Options (if available):**
- Status: All | Pending | Applied | Rejected
- Date range: Last 24h | Last week | Last month | All time
- Command type: All | create_charter | assess_gaps | etc.

**Example Filter:**
1. Select "Status: Applied"
2. Table shows only applied proposals
3. Should see 1 result (create_charter)

✅ **Checkpoint 6.3:** Filtered proposal history by status

## UI Components Deep Dive

### CommandPanel Component

**Purpose:** Primary interface for proposing commands

**Props/State:**
- `selectedProject`: Current project (TODO-001)
- `availableCommands`: List of executable commands
- `recentProposals`: Last 5 proposals for quick access

**Events:**
- `onPropose`: Triggered when "Propose" button clicked
- `onCommandSelect`: Triggered when dropdown value changes
- `onDescriptionChange`: Real-time description updates

### ProposalModal Component

**Purpose:** Display proposal details and enable apply/reject actions

**Props/State:**
- `proposalId`: Unique proposal identifier
- `artifacts`: Array of artifact objects with paths/content/sizes
- `status`: Current proposal status (PENDING/APPLIED/REJECTED)
- `readonly`: Boolean (true for historical proposals)

**Features:**
- Lazy-loaded artifact previews (fetched on demand)
- Diff computation on-the-fly
- Optimistic UI updates (updates UI before backend confirms)

### DiffViewer Component

**Purpose:** Show Git-style diffs of proposed changes

**Features:**
- Syntax highlighting (Markdown, JSON, YAML, etc.)
- Side-by-side view (for file modifications)
- Unified view (for new files/deletions)
- Expand/collapse sections
- Copy diff to clipboard

## What You've Learned

By completing this tutorial, you can now:

✅ Use CommandPanel to propose commands with detailed context  
✅ Understand propose/apply workflow pattern and its benefits  
✅ Review proposal details thoroughly before applying  
✅ Inspect artifact previews to verify generated content  
✅ View Git diffs to understand exactly what will change  
✅ Apply proposals to commit artifacts to project repository  
✅ Reject proposals when changes aren't suitable  
✅ Download proposal previews for offline review or team sharing  
✅ Navigate proposal history to audit past workflow  
✅ Re-open past proposals in read-only mode  
✅ Filter proposal history by status/date/command type  
✅ Troubleshoot common proposal workflow issues  
✅ Compare GUI vs TUI workflow patterns  

**Key Concepts Mastered:**
- Propose/apply two-step workflow
- Artifact generation and management
- Git commit integration
- Proposal status lifecycle (PENDING → APPLIED/REJECTED)
- Modal-based review workflow
- Diff preview and verification

## Next Steps

Now that you've mastered the command proposal workflow:

1. **[Tutorial 04: Artifact Browsing](04-artifact-browsing.md)** ✨ NEXT - Navigate and export artifacts (20 min)
2. **[Tutorial 05: Workflow States](05-workflow-states.md)** - ISO 21500 phase management (20 min)
3. **[TUI Artifact Workflow](../tui-basics/03-artifact-workflow.md)** - Command-line equivalent for comparison (15 min)

**Recommended Practice:**
- Try all available commands (create_charter, assess_gaps, define_wbs, plan_schedule)
- Experiment with rejecting and re-proposing
- Practice reviewing diffs carefully before applying
- Build muscle memory for keyboard shortcuts

## TUI Equivalent

The TUI provides the same workflow via command-line:

**Propose Command (TUI):**
```bash
python apps/tui/main.py propose propose \
  --project TODO-001 \
  --command create_charter \
  --description "Generate initial project charter..."
  
# Output: Proposal ID prop-a1b2c3d4
```

**List Proposals (TUI):**
```bash
python apps/tui/main.py propose list --project TODO-001
```

**View Proposal (TUI):**
```bash
python apps/tui/main.py propose show \
  --project TODO-001 \
  --proposal prop-a1b2c3d4
```

**Apply Proposal (TUI):**
```bash
python apps/tui/main.py propose apply \
  --project TODO-001 \
  --proposal prop-a1b2c3d4
```

**Reject Proposal (TUI):**
```bash
python apps/tui/main.py propose reject \
  --project TODO-001 \
  --proposal prop-a1b2c3d4 \
  --reason "Gaps analysis not needed yet"
```

See [TUI Artifact Workflow](../tui-basics/03-artifact-workflow.md) for full command-line tutorial.

**GUI vs TUI Comparison:**
| Feature | GUI (Web) | TUI (CLI) |
|---------|-----------|-----------|
| **Proposal Creation** | Form + button | Command with flags |
| **Artifact Preview** | Interactive modal | JSON output to terminal |
| **Diff View** | Visual diff viewer | Unified diff text |
| **Apply/Reject** | Button click + confirmation | Command execution |
| **History** | Table with filters | JSON list or table |
| **Best For** | Visual learners, presentations | Automation, CI/CD, power users |

## Troubleshooting

Comprehensive troubleshooting for proposal workflow issues:

### Issue 1: Propose Button Disabled

**Symptoms:**
- "Propose" button grayed out
- Cannot click to submit proposal

**Diagnostic Steps:**
1. Check command dropdown - is a command selected?
2. Check description field - does it have 50+ characters?
3. Open browser console - any validation errors?

**Solutions:**
- Select a command from dropdown
- Write longer description (minimum 50 chars, recommended 200+)
- Clear browser cache and refresh if selection UI seems broken

**Expected Resolution Time:** 1-2 minutes

### Issue 2: Proposal Times Out

**Symptoms:**
- "Proposing..." spinner runs for 60+ seconds
- Eventually shows error: "Request timeout"
- No ProposalModal appears

**Diagnostic Steps:**
```bash
# Check API logs for errors
docker compose logs api --tail=50 | grep ERROR

# Check LLM service status (if using external LLM)
curl http://localhost:1234/v1/models  # LM Studio example

# Test API directly
curl -X POST http://localhost:8000/api/commands/propose \
  -H "Content-Type: application/json" \
  -d '{"project_key":"TODO-001","command":"create_charter","description":"Test"}'
```

**Solutions:**
- **LLM timeout:** Restart LLM service or increase timeout in API config
- **Template fallback:** API should auto-fallback to templates if LLM unavailable
- **Network issue:** Check Docker network connectivity between containers
- **Resource exhaustion:** Check `docker stats` for high CPU/memory usage

**Expected Resolution Time:** 5-15 minutes

### Issue 3: ProposalModal Doesn't Open

**Symptoms:**
- "Proposal created successfully!" toast appears
- But ProposalModal doesn't open
- Stuck on CommandPanel view

**Diagnostic Steps:**
1. Open browser console - any JavaScript errors?
2. Check Network tab - was proposal ID returned?
3. Try refreshing page and checking proposal history

**Solutions:**
- **React rendering error:** Hard refresh (Ctrl+Shift+R) to clear cached JS
- **Modal state bug:** Click "View All Proposals" and click "View" on latest proposal
- **Z-index issue:** Check if modal is behind other elements (use browser inspector)
- **JavaScript error:** Check console for errors, report bug if persistent

**Expected Resolution Time:** 3-7 minutes

### Issue 4: Artifacts Not Showing After Apply

**Symptoms:**
- "Proposal applied successfully!" message appears
- Git commit was created (verified in logs)
- But artifacts don't appear in ArtifactsList component

**Diagnostic Steps:**
```bash
# Verify artifacts exist on disk
docker exec -it $(docker compose ps -q api) \
  ls -la projectDocs/TODO-001/artifacts/

# Check Git log
docker exec -it $(docker compose ps -q api) \
  sh -c "cd projectDocs/TODO-001 && git log --oneline -1"

# Test API artifacts endpoint
curl http://localhost:8000/api/artifacts?project=TODO-001
```

**Solutions:**
- **UI refresh needed:** Click "Refresh" button in ArtifactsList or reload page
- **API not returning artifacts:** Check API logs for errors in artifacts endpoint
- **File permissions:** Ensure API container can read `projectDocs/` directory
- **Cache issue:** Clear browser cache, hard refresh page

**Expected Resolution Time:** 2-5 minutes

### Issue 5: Cannot Reject Proposal

**Symptoms:**
- Click "Reject" button but nothing happens
- Or rejection fails with error

**Diagnostic Steps:**
1. Check proposal status - is it already APPLIED?
2. Check browser console for errors
3. Test API rejection endpoint directly:
```bash
curl -X POST http://localhost:8000/api/commands/reject \
  -H "Content-Type: application/json" \
  -d '{"project_key":"TODO-001","proposal_id":"prop-xxx","reason":"Test rejection"}'
```

**Solutions:**
- **Already applied:** Cannot reject applied proposals (use Git revert instead)
- **API error:** Check logs for backend validation errors
- **Concurrent modification:** Another user/session applied it simultaneously

**Expected Resolution Time:** 2-5 minutes

### Issue 6: Diff Viewer Shows Garbled Text

**Symptoms:**
- Diff viewer opens but shows unreadable characters
- Or diff computation fails with error

**Diagnostic Steps:**
1. Check artifact file encoding (should be UTF-8)
2. Try downloading preview ZIP and viewing diff.patch file locally
3. Check browser console for diff parsing errors

**Solutions:**
- **Encoding issue:** Report bug if artifacts have non-UTF-8 encoding
- **Large file:** Diff viewer may struggle with >1MB files (use download instead)
- **Binary file:** Some files (images) cannot be diffed textually

**Expected Resolution Time:** 5-10 minutes

## Success Checklist

Before proceeding to Tutorial 04, verify you can:

- [ ] Access CommandPanel in web UI for TODO-001 project
- [ ] Open command dropdown and see all available commands
- [ ] Understand what each command does (create_charter, assess_gaps, etc.)
- [ ] Select a command from dropdown
- [ ] Write detailed description (200+ characters)
- [ ] Submit proposal by clicking "Propose" button
- [ ] Wait for proposal creation (3-15 seconds)
- [ ] ProposalModal opens automatically after creation
- [ ] Review proposal ID, command, status, timestamp
- [ ] See artifacts preview list (3 files for create_charter)
- [ ] Click on artifact to preview content
- [ ] Open diff viewer to see Git changes
- [ ] Download preview ZIP for offline review (optional)
- [ ] Click "Apply Proposal" button
- [ ] Confirm application in dialog
- [ ] Wait for success notification (1-3 seconds)
- [ ] Verify artifacts appear in ArtifactsList
- [ ] Verify Git commit created (advanced check)
- [ ] Propose second command (assess_gaps)
- [ ] Review second proposal
- [ ] Reject second proposal with reason
- [ ] Verify no artifacts created for rejected proposal
- [ ] View proposal history (2 proposals)
- [ ] Re-open past proposal in read-only mode
- [ ] Filter proposal history by status
- [ ] Understand difference between PENDING/APPLIED/REJECTED statuses
- [ ] Know when to apply vs reject proposals
- [ ] Troubleshoot common issues (disabled button, timeouts, etc.)
- [ ] Compare GUI workflow with TUI equivalent

**Estimated Total Time:** 20-30 minutes (35-50 minutes with practice and troubleshooting)

**If all checkpoints passed:** ✅ Ready for Tutorial 04!

---

**Tutorial Series:** [GUI Basics](../README.md#gui-basics) | **Previous:** [02 - Project Creation](02-project-creation.md) | **Next:** [04 - Artifact Browsing](04-artifact-browsing.md)

**Related Tutorials:**
- [TUI Artifact Workflow](../tui-basics/03-artifact-workflow.md) - Command-line equivalent (15 min)
- [Advanced: Proposal Automation](../advanced/02-proposal-automation.md) - Scripting proposals (30 min)

**Additional Resources:**
- [Command Reference](../../api/commands-reference.md) - All available commands documented
- [Proposal Workflow Architecture](../../architecture/proposal-workflow.md) - Technical implementation details
- [Git Integration Guide](../../howto/git-workflow.md) - How proposals interact with Git
