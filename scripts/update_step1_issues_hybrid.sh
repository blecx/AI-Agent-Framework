#!/bin/bash
# Update GitHub issue descriptions to reflect chat-first hybrid approach
# Run from project root after reviewing changes in STEP-1-HYBRID-APPROACH-UPDATE.md

set -e

REPO="blecx/AI-Agent-Framework-Client"

echo "🔄 Updating GitHub issues to reflect chat-first hybrid approach..."
echo ""

# Issue #32: RAID List View
gh issue edit 32 --repo "$REPO" --body "## 📋 Description

**Browse RAID items created via AI chat or UI quick-add.**

Display RAID (Risks, Assumptions, Issues, Dependencies) items in a table with:
- All RAID types (Risk, Assumption, Issue, Dependency)
- Severity/priority badges with colors
- Status indicators
- Creation source (chat or UI)

### **Purpose in Hybrid Approach:**
- **Primary Use:** View artifacts created through AI chat conversations
- **Secondary:** Quick-add button for simple items (optional)

## ✅ Acceptance Criteria

- Table displays all RAID items from backend API
- Columns: ID, Type, Title, Status, Priority, Owner, Date
- Badge styling matches design system (#36)
- Click row to view details (#34)
- \"Add RAID\" button opens quick-add modal (#35) - optional feature
- Handles empty state when no items exist
- API errors shown to user

## 🔗 Dependencies

- ✅ Issue #30 (RAID types)
- ✅ Issue #31 (RAID API service)
- ⚠️ Blocked by Issue #24 (API service layer)

## 📊 Estimation

- **Complexity:** Medium
- **Estimated Time:** 4-6 hours
- **Priority:** High"

echo "✅ Updated Issue #32: RAID List View (chat-first context)"

# Issue #34: RAID Detail/Edit View
gh issue edit 34 --repo "$REPO" --body "## 📋 Description

**View and edit RAID items using chat OR UI.**

Detail view/modal for individual RAID items with:
- All fields displayed
- Both chat and UI editing support
- Change history/audit trail integration

### **Hybrid Approach:**
- **Chat Editing:** \"Update RAID-001's priority to Critical\" → Backend update
- **UI Editing:** Click item → inline edit or modal form
- Both methods update same backend API

## ✅ Acceptance Criteria

- Display full RAID item details (all fields)
- Inline editing OR modal form for UI edits
- Chat commands can update fields via backend
- Status badge and priority indicator
- \"Edit\" / \"Save\" / \"Cancel\" actions for UI
- Validation before saving
- Success/error notifications (both methods)
- Audit trail link (view who changed what)
- API errors handled gracefully

## 🔗 Dependencies

- ✅ Issue #30 (RAID types)
- ✅ Issue #31 (RAID API service)
- ✅ Issue #32 (RAID list view)
- ⚠️ Blocked by Issue #24 (API service layer)

## 📊 Estimation

- **Complexity:** Medium
- **Estimated Time:** 5-7 hours
- **Priority:** High"

echo "✅ Updated Issue #34: RAID Detail/Edit View (hybrid editing)"

# Issue #35: RAID Create Modal
gh issue edit 35 --repo "$REPO" --title "Optional quick-add RAID form (alternative to chat)" --body "## 📋 Description

**Quick-add form for simple RAID items (alternative to AI chat).**

### **Chat-First Paradigm:**
- **Primary Creation:** AI chat guides complex RAID creation with questions
- **Optional:** This form for quick simple items (\"Add security risk: API rate limiting\")
- **When to use:** Quick-add for straightforward items without guidance needed

Modal/form with:
- Type selector (Risk, Assumption, Issue, Dependency)
- Title, description, priority, owner fields
- Form validation
- Calls POST /projects/{key}/raid API

## ✅ Acceptance Criteria

- Modal opens from \"Add RAID\" button in #32
- Form fields: Type, Title, Description, Priority/Severity, Owner, Status
- Type-specific fields (e.g., Risk shows mitigation, Issue shows resolution)
- Field validation (required fields, formats)
- Calls POST /projects/{key}/raid endpoint
- Success notification + closes modal
- Error handling with user feedback
- **Label:** \"Optional - Chat is primary for complex RAID creation\"

## 🔗 Dependencies

- ✅ Issue #30 (RAID types)
- ✅ Issue #31 (RAID API service)
- ⚠️ Blocked by Issue #24 (API service layer)

## 📊 Estimation

- **Complexity:** Medium
- **Estimated Time:** 4-6 hours
- **Priority:** Medium (optional feature, chat is primary)"

echo "✅ Updated Issue #35: RAID Create Modal (optional quick-add)"

# Issue #40: Workflow Transition UI
gh issue edit 40 --repo "$REPO" --body "## 📋 Description

**Support workflow transitions via BOTH chat commands AND UI buttons.**

### **Hybrid Approach:**
- **Primary (Chat):** AI chat: \"Move to Planning phase\" → Backend transition
- **Optional (UI):** Button: Click \"Transition to Planning\" → Same backend call
- Both methods call PATCH /projects/{key}/workflow/state

UI Component:
- Button/dropdown showing available next states
- Confirmation if significant transition
- Respects workflow rules (blocked states)
- Real-time state updates from either source

## ✅ Acceptance Criteria

- Shows current workflow state prominently
- Displays valid next states (from API rules)
- Click triggers state transition via API
- Chat commands also trigger transitions
- Confirmation dialog for critical transitions
- Success/error notifications (both methods)
- Updates all views (chat + UI) after transition
- Handles errors (invalid transitions, blocked states)
- Disables button if no valid transitions

## 🔗 Dependencies

- ✅ Issue #37 (Workflow types)
- ✅ Issue #38 (Workflow API service)
- ✅ Issue #39 (Workflow indicator)
- ⚠️ Blocked by Issue #24 (API service layer)

## 📊 Estimation

- **Complexity:** Medium
- **Estimated Time:** 4-6 hours
- **Priority:** High"

echo "✅ Updated Issue #40: Workflow Transition UI (hybrid support)"

# Issue #42: Refactor WorkflowPanel
gh issue edit 42 --repo "$REPO" --title "Clarify WorkflowPanel purpose + add ISO 21500 indicator" --body "## 📋 Description

**Clarification: WorkflowPanel is CORRECT as-is!**

### **Current Understanding:**
- **WorkflowPanel shows AI agent conversation workflow steps** ✅ CORRECT
- This is for tracking the AI chat conversation state
- **Should NOT show ISO 21500 project workflow states** (that's #39)

### **What to Do:**
1. **Keep WorkflowPanel as-is** - It correctly shows AI agent conversation steps
2. **Add separate ISO 21500 workflow indicator** (Issue #39) - Shows project state
3. **Document the distinction:**
   - WorkflowPanel = AI chat conversation progress
   - WorkflowIndicator (#39) = ISO 21500 project state (Initiation → Planning → Execution → Closing)

## ✅ Acceptance Criteria

- Review WorkflowPanel.tsx code
- Confirm it shows AI agent conversation steps (CORRECT)
- Add code comments explaining purpose
- Ensure Issue #39 creates separate ISO 21500 state indicator
- Document in README: Two different workflows exist
  - AI conversation workflow (WorkflowPanel)
  - ISO 21500 project workflow (WorkflowIndicator)

## 🔗 Dependencies

- None - This is clarification/documentation work

## 📊 Estimation

- **Complexity:** Low (documentation + code comments)
- **Estimated Time:** 1-2 hours
- **Priority:** Low (clarification, not new feature)"

echo "✅ Updated Issue #42: WorkflowPanel clarification (keep as-is)"

# Issue #44: Project Creation Flow
gh issue edit 44 --repo "$REPO" --title "Optional quick-add project form (alternative to chat)" --body "## 📋 Description

**Quick-add form for simple projects (alternative to AI chat).**

### **Chat-First Paradigm:**
- **Primary Creation (Step 2):** AI chat guides project creation with governance questions
- **Optional:** This form for quick simple projects without governance guidance
- **When to use:** Quick project setup without ISO 21500 compliance guidance

Multi-step form with:
- Project name, key, description
- Basic settings
- Calls POST /projects API

## ✅ Acceptance Criteria

- Form wizard or stepper UI
- Steps: Basic Info → Settings → Confirmation
- Fields: Name, Key, Description (minimal)
- Project key validation (unique, format)
- Calls POST /projects endpoint
- Success: Redirect to project dashboard (#45)
- Error handling with user feedback
- **Label:** \"Optional - Step 2 chat provides governance guidance\"

## 🔗 Dependencies

- ✅ Issue #24 (API service layer)
- ⚠️ Blocked by Issue #24 (API service layer)

## 📊 Estimation

- **Complexity:** Medium-High
- **Estimated Time:** 6-8 hours
- **Priority:** Low (optional feature, Step 2 chat is primary)"

echo "✅ Updated Issue #44: Project Creation Flow (optional quick-add)"

# Issue #52-53: E2E Tests
gh issue edit 52 --repo "$REPO" --body "## 📋 Description

**End-to-end tests for chat AND UI artifact creation flows.**

Full user journey tests using Playwright covering:
- **Chat flows:** AI-guided artifact creation
- **UI flows:** Quick-add form creation
- **Viewing:** Browse artifacts from both sources
- **Editing:** Both chat and UI editing methods
- Multi-page workflows
- Error scenarios

### **Hybrid Testing:**
- Test chat command \"Create RAID risk\" → Backend → View in UI
- Test UI quick-add form → Backend → View in chat responses
- Test editing via chat: \"Update priority\" → UI shows change
- Test editing via UI form → Chat reflects change

## ✅ Acceptance Criteria

- E2E tests using Playwright
- Cover main user journeys (chat + UI)
- Create → View → Edit → Delete flows (both methods)
- Test error handling (both interfaces)
- Test responsive layouts
- Test accessibility
- Tests run in CI pipeline
- >90% critical path coverage

## 🔗 Dependencies

- ⚠️ Blocked by all UI implementation issues
- ⚠️ Blocked by chat-to-backend integration (new Issue #59)

## 📊 Estimation

- **Complexity:** High
- **Estimated Time:** 8-12 hours
- **Priority:** High (verify hybrid approach works)"

echo "✅ Updated Issue #52: E2E Tests (hybrid flows)"

# Issue #56: Update Client README
gh issue edit 56 --repo "$REPO" --body "## 📋 Description

**Update client README to accurately describe chat-first hybrid approach.**

Current README may describe traditional PM UI. Update to reflect:
- **Primary Interface:** AI chat for artifact creation
- **Secondary Interface:** UI for browsing + quick-adds
- Templates guide AI conversations (Step 2)
- Hybrid approach: Complex via chat, simple via UI

## ✅ Acceptance Criteria

- Remove outdated traditional PM UI descriptions
- Add \"Chat-First Hybrid Approach\" section
- Explain: AI guides artifact creation using templates
- Document: UI for viewing + optional quick-add forms
- Update architecture diagram (chat + UI + backend)
- Document chat command examples
- Document UI quick-add examples
- Explain Step 2: Templates guide AI conversations
- Add usage examples for both interfaces

## 🔗 Dependencies

- None - Documentation work

## 📊 Estimation

- **Complexity:** Low
- **Estimated Time:** 2-3 hours
- **Priority:** Medium"

echo "✅ Updated Issue #56: Update Client README (chat-first approach)"

echo ""
echo "🎉 Updated 8 GitHub issues with hybrid chat-first approach!"
echo ""
echo "📋 Summary:"
echo "  - Issue #32: RAID List View (browse chat-created items)"
echo "  - Issue #34: RAID Detail/Edit (hybrid editing)"
echo "  - Issue #35: RAID Create Modal (optional quick-add)"
echo "  - Issue #40: Workflow Transition UI (hybrid support)"
echo "  - Issue #42: WorkflowPanel (keep as-is, add comments)"
echo "  - Issue #44: Project Creation Flow (optional quick-add)"
echo "  - Issue #52: E2E Tests (hybrid flows)"
echo "  - Issue #56: Update Client README (chat-first docs)"
echo ""
echo "✅ Next: Create Issue #59 for chat-to-backend integration"
