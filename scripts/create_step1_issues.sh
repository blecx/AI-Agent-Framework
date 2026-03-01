#!/bin/bash
# Create all Step 1 GitHub issues from STEP-1-ISSUES-PLAN.md

set -e

REPO="blecx/AI-Agent-Framework-Client"
MILESTONE="Step 1 - Client Implementation"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Creating Step 1 GitHub Issues for ${REPO}${NC}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# API-friendly pacing for all gh calls in this script.
# Uses a minimum interval between requests to avoid bursty traffic.
GH_MIN_INTERVAL_SECONDS="${GH_MIN_INTERVAL_SECONDS:-1}"
__GH_LAST_CALL_TS=""

gh() {
  local min_interval
  min_interval="${GH_MIN_INTERVAL_SECONDS:-0}"

  if [[ -n "${__GH_LAST_CALL_TS}" && "${min_interval}" != "0" ]]; then
    local now elapsed
    now="$(date +%s)"
    elapsed="$(( now - __GH_LAST_CALL_TS ))"
    if [[ "$elapsed" -lt "$min_interval" ]]; then
      sleep "$(( min_interval - elapsed ))"
    fi
  fi

  command gh "$@"
  __GH_LAST_CALL_TS="$(date +%s)"
}

# Note: Milestones must be created via web UI
# We'll create issues without milestones and add them later

echo ""
echo -e "${GREEN}Creating issues...${NC}"
echo "(Note: Add issues to milestone manually via web UI)"
echo "(GitHub throttle: ${GH_MIN_INTERVAL_SECONDS}s min interval)"
echo ""

# Infrastructure Issues (1-6)

echo "Creating Issue #1: Set up client API service layer"
gh issue create --repo "${REPO}" \
  --title "Set up client API service layer" \
  --label "step:1,client,infrastructure,blocker" \
  \
  --body "**Priority:** 🔴 Critical - BLOCKER
**Estimated:** 4-6 hours

## Description
Create typed API client service for backend integration.

## Tasks
- [ ] Create \`src/services/apiClient.ts\` with typed fetch wrapper
- [ ] Add error handling and loading states
- [ ] Add API response type definitions
- [ ] Configure base URL and environment variables
- [ ] Add request/response interceptors
- [ ] Write unit tests for API client

## Dependencies
None (MUST BE FIRST)

## Acceptance Criteria
- API client can make typed requests to backend
- Error handling works for 4xx/5xx responses
- Unit tests pass"

echo "Creating Issue #2: Add project management routing"
gh issue create --repo "${REPO}" \
  --title "Add project management routing" \
  --label "step:1,client,infrastructure,blocker" \
  \
  --body "**Priority:** 🔴 Critical - BLOCKER
**Estimated:** 3-4 hours

## Description
Set up routing for RAID and workflow management pages.

## Tasks
- [ ] Update \`App.tsx\` to add project management routes
- [ ] Create route structure: \`/projects/:key/raid\`, \`/projects/:key/workflow\`
- [ ] Add navigation links in sidebar/header
- [ ] Create project context provider
- [ ] Add route guards if needed

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #1 (API service layer)

## Acceptance Criteria
- Routes are accessible and render placeholder pages
- Navigation works between routes
- Project context is available to child components"

echo "Creating Issue #3: Create shared UI component library"
gh issue create --repo "${REPO}" \
  --title "Create shared UI component library" \
  --label "step:1,client,infrastructure,ui" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-5 hours

## Description
Build reusable UI components for consistent design.

## Tasks
- [ ] Create \`Button\` component with variants
- [ ] Create \`Modal\` component with overlay
- [ ] Create \`Table\` component with sorting
- [ ] Create \`Badge\` component for status indicators
- [ ] Create \`Form\` components (Input, Select, Textarea)
- [ ] Add TypeScript prop types
- [ ] Write Storybook stories (optional)

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #2 (routing setup)

## Acceptance Criteria
- All components are typed and reusable
- Components follow consistent styling
- Examples/documentation exists"

echo "Creating Issue #4: Implement state management layer"
gh issue create --repo "${REPO}" \
  --title "Implement state management layer" \
  --label "step:1,client,infrastructure,state-management" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-5 hours

## Description
Set up state management for projects, RAID, and workflow data.

## Tasks
- [ ] Choose state management solution (React Context or Zustand)
- [ ] Create project context provider
- [ ] Create RAID state management
- [ ] Create workflow state management
- [ ] Implement loading and error states
- [ ] Add state persistence (localStorage for UI preferences)
- [ ] Write unit tests for state logic

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #1 (API service)
- ⚠️ **DEPENDS ON:** Issue #2 (routing)

## Acceptance Criteria
- State is accessible throughout app via hooks
- Loading/error states managed consistently
- State updates trigger re-renders correctly
- Unit tests pass"

echo "Creating Issue #5: Build global error handling and notifications"
gh issue create --repo "${REPO}" \
  --title "Build global error handling and notifications" \
  --label "step:1,client,infrastructure,ux" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 3-4 hours

## Description
Create global error boundary and toast notification system.

## Tasks
- [ ] Create \`ErrorBoundary\` component for React errors
- [ ] Create toast notification system (success/error/info/warning)
- [ ] Add global error handler for API errors
- [ ] Create \`useNotification\` hook
- [ ] Style notifications (top-right corner, auto-dismiss)
- [ ] Add notification queue management
- [ ] Write unit tests

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #3 (UI components)

## Acceptance Criteria
- React errors are caught and displayed gracefully
- API errors show user-friendly notifications
- Notifications auto-dismiss after 5 seconds
- Multiple notifications queue properly
- Unit tests pass"

echo "Creating Issue #6: Create project context and selection UI"
gh issue create --repo "${REPO}" \
  --title "Create project context and selection UI" \
  --label "step:1,client,infrastructure,project-mgmt" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 5-6 hours

## Description
Build project selector dropdown and context management.

## Tasks
- [ ] Create \`ProjectContext\` provider
- [ ] Create \`ProjectSelector\` dropdown component
- [ ] Fetch projects from backend
- [ ] Store selected project in localStorage
- [ ] Add project switching logic
- [ ] Show current project in header/navigation
- [ ] Handle no-project-selected state

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #1 (API service)
- ⚠️ **DEPENDS ON:** Issue #4 (state management)

## Acceptance Criteria
- Users can select a project from dropdown
- Selected project persists across page reloads
- All child components have access to current project
- UI gracefully handles no project selected"

# RAID UI Issues (7-13)

echo "Creating Issue #7: Create RAID data models and types"
gh issue create --repo "${REPO}" \
  --title "Create RAID data models and types" \
  --label "step:1,client,raid,types" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 2-3 hours

## Description
Define TypeScript types matching backend RAID models.

## Tasks
- [ ] Create \`src/types/raid.ts\` with RAID interfaces
- [ ] Define \`RAIDType\` enum: Risk, Assumption, Issue, Dependency
- [ ] Define \`RAIDStatus\` enum: Open, InProgress, Closed, Resolved, Monitored
- [ ] Define \`RAIDPriority\` enum: Low, Medium, High, Critical
- [ ] Define \`RAIDImpactLevel\` and \`RAIDLikelihood\` enums
- [ ] Define \`RAIDItem\` interface matching backend schema
- [ ] Add JSDoc comments for each type

## Dependencies
None (parallel with Issue #6)

## Acceptance Criteria
- Types match backend API contracts exactly
- Types are exported and reusable
- No \`any\` types used"

echo "Creating Issue #8: Implement RAID API service"
gh issue create --repo "${REPO}" \
  --title "Implement RAID API service" \
  --label "step:1,client,raid,api" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 3-4 hours

## Description
Create service layer for RAID CRUD operations.

## Tasks
- [ ] Create \`src/services/raidService.ts\`
- [ ] Implement \`listRAIDItems(projectKey, filters)\`
- [ ] Implement \`getRAIDItem(projectKey, raidId)\`
- [ ] Implement \`createRAIDItem(projectKey, data)\`
- [ ] Implement \`updateRAIDItem(projectKey, raidId, data)\`
- [ ] Implement \`deleteRAIDItem(projectKey, raidId)\`
- [ ] Add TypeScript types for all parameters and returns
- [ ] Write unit tests with mock fetch

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #1 (API client)
- ⚠️ **DEPENDS ON:** Issue #7 (RAID types)

## Acceptance Criteria
- All CRUD operations work with backend API
- Proper error handling for API failures
- Unit tests pass with 80%+ coverage"

echo "Creating Issue #9: Build RAID list view component"
gh issue create --repo "${REPO}" \
  --title "Build RAID list view component" \
  --label "step:1,client,raid,ui" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 6-8 hours

## Description
Create main RAID list view with filtering and sorting.

## Tasks
- [ ] Create \`src/components/raid/RAIDList.tsx\`
- [ ] Display RAID items in table format
- [ ] Add columns: Type, Title, Status, Priority, Owner, Due Date
- [ ] Implement client-side sorting by column
- [ ] Add loading skeleton
- [ ] Add empty state (\"No RAID items\")
- [ ] Add \"Create RAID\" button
- [ ] Integrate with RAID API service
- [ ] Handle API errors gracefully

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #3 (UI components)
- ⚠️ **DEPENDS ON:** Issue #8 (RAID service)

## Acceptance Criteria
- RAID items display correctly in table
- Sorting works for all columns
- Loading and empty states render correctly
- Clicking item navigates to detail view"

echo "Creating Issue #10: Build RAID filter panel"
gh issue create --repo "${REPO}" \
  --title "Build RAID filter panel" \
  --label "step:1,client,raid,ui" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 4-5 hours

## Description
Add filter panel for RAID list view.

## Tasks
- [ ] Create \`src/components/raid/RAIDFilters.tsx\`
- [ ] Add filter by Type (Risk/Assumption/Issue/Dependency)
- [ ] Add filter by Status (Open/InProgress/Closed/Resolved/Monitored)
- [ ] Add filter by Priority (Low/Medium/High/Critical)
- [ ] Add filter by Owner (dropdown)
- [ ] Add filter by Due Date (date range)
- [ ] Add \"Clear Filters\" button
- [ ] Update URL query params when filters change
- [ ] Restore filters from URL on page load

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #9 (RAID list)

## Acceptance Criteria
- Filters update list view correctly
- Multiple filters can be applied simultaneously
- Filters persist in URL
- Clear filters resets to default view"

echo "Creating Issue #11: Build RAID detail/edit view"
gh issue create --repo "${REPO}" \
  --title "Build RAID detail/edit view" \
  --label "step:1,client,raid,ui" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 5-6 hours

## Description
Create detailed view for viewing and editing RAID items.

## Tasks
- [ ] Create \`src/components/raid/RAIDDetail.tsx\`
- [ ] Display all RAID item fields (read-only mode)
- [ ] Add \"Edit\" button to enable editing
- [ ] Create editable form fields
- [ ] Add validation for required fields
- [ ] Add \"Save\" and \"Cancel\" buttons
- [ ] Integrate with update API
- [ ] Show success notification on save
- [ ] Handle API errors with notifications

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #3 (UI components)
- ⚠️ **DEPENDS ON:** Issue #8 (RAID service)
- ⚠️ **DEPENDS ON:** Issue #5 (notifications)

## Acceptance Criteria
- Detail view displays all RAID fields
- Edit mode allows field updates
- Validation prevents invalid data
- Save/cancel work correctly"

echo "Creating Issue #12: Build RAID create modal"
gh issue create --repo "${REPO}" \
  --title "Build RAID create modal" \
  --label "step:1,client,raid,ui" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-5 hours

## Description
Create modal dialog for creating new RAID items.

## Tasks
- [ ] Create \`src/components/raid/RAIDCreateModal.tsx\`
- [ ] Add form fields: Type, Title, Description, Status, Priority, Owner, Due Date
- [ ] Add field validation
- [ ] Add \"Create\" and \"Cancel\" buttons
- [ ] Integrate with create API
- [ ] Show success notification on create
- [ ] Navigate to detail view after creation
- [ ] Handle API errors with notifications

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #3 (UI components - Modal)
- ⚠️ **DEPENDS ON:** Issue #8 (RAID service)
- ⚠️ **DEPENDS ON:** Issue #5 (notifications)

## Acceptance Criteria
- Modal opens when \"Create RAID\" button clicked
- All fields are editable
- Validation prevents invalid submissions
- Successfully created items appear in list"

echo "Creating Issue #13: Build RAID status badge component"
gh issue create --repo "${REPO}" \
  --title "Build RAID status badge component" \
  --label "step:1,client,raid,ui" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 2-3 hours

## Description
Create reusable badge components for RAID type, status, and priority.

## Tasks
- [ ] Create \`src/components/raid/RAIDBadge.tsx\`
- [ ] Add color coding for Type (Risk=red, Assumption=blue, Issue=orange, Dependency=purple)
- [ ] Add color coding for Status (Open=yellow, InProgress=blue, Closed=gray, etc.)
- [ ] Add color coding for Priority (Low=green, Medium=yellow, High=orange, Critical=red)
- [ ] Add icon support (optional)
- [ ] Make badges consistent across all RAID views

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #3 (UI components - Badge)

## Acceptance Criteria
- Badges display with correct colors
- Badges are readable and accessible
- Badges are used consistently throughout RAID UI"

# Workflow UI Issues (14-19)

echo "Creating Issue #14: Create workflow data models and types"
gh issue create --repo "${REPO}" \
  --title "Create workflow data models and types" \
  --label "step:1,client,workflow,types" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 2-3 hours

## Description
Define TypeScript types for ISO 21500 workflow states.

## Tasks
- [ ] Create \`src/types/workflow.ts\`
- [ ] Define \`WorkflowState\` enum: Initiating, Planning, Executing, Monitoring, Closing, Closed
- [ ] Define \`WorkflowTransition\` interface
- [ ] Define \`AuditEvent\` interface
- [ ] Add JSDoc comments explaining each state
- [ ] Add valid state transitions documentation

## Dependencies
None (parallel with RAID types)

## Acceptance Criteria
- Types match backend API contracts
- All ISO 21500 states are defined
- Types are exported and reusable"

echo "Creating Issue #15: Implement workflow API service"
gh issue create --repo "${REPO}" \
  --title "Implement workflow API service" \
  --label "step:1,client,workflow,api" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 3-4 hours

## Description
Create service layer for workflow state management and audit events.

## Tasks
- [ ] Create \`src/services/workflowService.ts\`
- [ ] Implement \`getWorkflowState(projectKey)\`
- [ ] Implement \`transitionState(projectKey, newState, note)\`
- [ ] Implement \`getAllowedTransitions(projectKey)\`
- [ ] Create \`src/services/auditService.ts\`
- [ ] Implement \`getAuditEvents(projectKey, filters)\`
- [ ] Add TypeScript types for all parameters and returns
- [ ] Write unit tests with mock fetch

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #1 (API client)
- ⚠️ **DEPENDS ON:** Issue #14 (workflow types)

## Acceptance Criteria
- Workflow state operations work with backend
- Audit events can be retrieved and filtered
- Unit tests pass with 80%+ coverage"

echo "Creating Issue #16: Build workflow stage indicator component"
gh issue create --repo "${REPO}" \
  --title "Build workflow stage indicator component" \
  --label "step:1,client,workflow,ui" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 5-6 hours

## Description
Create visual stage indicator for ISO 21500 workflow states.

## Tasks
- [ ] Create \`src/components/workflow/WorkflowStageIndicator.tsx\`
- [ ] Display all 6 stages: Initiating → Planning → Executing → Monitoring → Closing → Closed
- [ ] Highlight current stage
- [ ] Show completed stages with checkmark
- [ ] Show locked future stages as grayed out
- [ ] Make stages clickable to view transition options
- [ ] Add tooltips with stage descriptions
- [ ] Integrate with workflow API service

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #3 (UI components)
- ⚠️ **DEPENDS ON:** Issue #15 (workflow service)

## Acceptance Criteria
- Stage indicator displays current state correctly
- Visual design is clear and intuitive
- Component updates when state changes"

echo "Creating Issue #17: Build workflow transition UI"
gh issue create --repo "${REPO}" \
  --title "Build workflow transition UI" \
  --label "step:1,client,workflow,ui" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-5 hours

## Description
Create UI for transitioning between workflow states.

## Tasks
- [ ] Create \`src/components/workflow/WorkflowTransitionModal.tsx\`
- [ ] Show allowed transitions from current state
- [ ] Add confirmation dialog before transition
- [ ] Add optional note/reason field
- [ ] Display transition consequences (if any)
- [ ] Integrate with workflow API
- [ ] Show success notification after transition
- [ ] Handle invalid transitions with error messages

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #3 (UI components - Modal)
- ⚠️ **DEPENDS ON:** Issue #15 (workflow service)
- ⚠️ **DEPENDS ON:** Issue #5 (notifications)

## Acceptance Criteria
- Only valid transitions are shown
- Confirmation prevents accidental transitions
- Transitions create audit events
- UI updates after successful transition"

echo "Creating Issue #18: Build audit trail viewer"
gh issue create --repo "${REPO}" \
  --title "Build audit trail viewer" \
  --label "step:1,client,workflow,ui" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 4-5 hours

## Description
Create read-only audit trail viewer for project events.

## Tasks
- [ ] Create \`src/components/workflow/AuditTrail.tsx\`
- [ ] Display audit events in reverse chronological order
- [ ] Show event type, timestamp, actor, and summary
- [ ] Add filtering by event type
- [ ] Add date range filtering
- [ ] Add pagination (show 50 events per page)
- [ ] Add expand/collapse for event details
- [ ] Integrate with audit API service

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #3 (UI components - Table)
- ⚠️ **DEPENDS ON:** Issue #15 (audit service)

## Acceptance Criteria
- Audit events display correctly
- Filtering and pagination work
- Events are read-only (no editing)
- Timestamps display in user's timezone"

echo "Creating Issue #19: Refactor existing WorkflowPanel for ISO 21500"
gh issue create --repo "${REPO}" \
  --title "Refactor existing WorkflowPanel for ISO 21500" \
  --label "step:1,client,workflow,refactor" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 3-4 hours

## Description
Refactor the existing WorkflowPanel component to support ISO 21500 project workflows instead of agent workflows.

## Tasks
- [ ] Analyze current \`WorkflowPanel.tsx\` implementation
- [ ] Remove agent workflow logic
- [ ] Replace with ISO 21500 workflow state display
- [ ] Use new workflow components (stage indicator, transitions)
- [ ] Update types and interfaces
- [ ] Remove unused agent-related code
- [ ] Update component tests

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #16 (stage indicator)
- ⚠️ **DEPENDS ON:** Issue #17 (transition UI)

## Acceptance Criteria
- WorkflowPanel displays project workflow states
- Agent workflow code is completely removed
- Component integrates with new workflow services
- Tests pass"

# Project Management UI Issues (20-22)

echo "Creating Issue #20: Build project list view"
gh issue create --repo "${REPO}" \
  --title "Build project list view" \
  --label "step:1,client,project-mgmt,ui" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-5 hours

## Description
Create main project list view for browsing all projects.

## Tasks
- [ ] Create \`src/components/projects/ProjectList.tsx\`
- [ ] Display projects in grid or list format
- [ ] Show project key, name, status, workflow state
- [ ] Add search bar for filtering projects
- [ ] Add sorting by name, date, status
- [ ] Add \"Create Project\" button
- [ ] Make projects clickable to select
- [ ] Integrate with projects API
- [ ] Add loading and empty states

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #1 (API service)
- ⚠️ **DEPENDS ON:** Issue #3 (UI components)
- ⚠️ **DEPENDS ON:** Issue #6 (project context)

## Acceptance Criteria
- All projects display correctly
- Search and sorting work
- Clicking project selects it
- Empty state shows \"No projects yet\""

echo "Creating Issue #21: Build project creation flow"
gh issue create --repo "${REPO}" \
  --title "Build project creation flow" \
  --label "step:1,client,project-mgmt,ui" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-6 hours

## Description
Create project creation form with governance metadata.

## Tasks
- [ ] Create \`src/components/projects/ProjectCreateModal.tsx\`
- [ ] Add fields: Project Key, Name, Description
- [ ] Add fields: Sponsor, Manager, Start Date, End Date
- [ ] Add field validation (key format, required fields)
- [ ] Integrate with create project API
- [ ] Show success notification on create
- [ ] Automatically select new project after creation
- [ ] Handle API errors with notifications

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #1 (API service)
- ⚠️ **DEPENDS ON:** Issue #3 (UI components - Modal)
- ⚠️ **DEPENDS ON:** Issue #5 (notifications)

## Acceptance Criteria
- All governance fields are editable
- Validation prevents invalid submissions
- New projects appear in list immediately
- User is automatically switched to new project"

echo "Creating Issue #22: Build project dashboard"
gh issue create --repo "${REPO}" \
  --title "Build project dashboard" \
  --label "step:1,client,project-mgmt,ui" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 4-5 hours

## Description
Create project dashboard landing page with overview and quick stats.

## Tasks
- [ ] Create \`src/components/projects/ProjectDashboard.tsx\`
- [ ] Display project name, key, description
- [ ] Show current workflow state prominently
- [ ] Display RAID summary (count by type and status)
- [ ] Show recent audit events (last 10)
- [ ] Add quick action buttons (Add RAID, Transition Workflow)
- [ ] Add navigation to RAID and Workflow pages
- [ ] Integrate with project, RAID, workflow, and audit APIs

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #8 (RAID service)
- ⚠️ **DEPENDS ON:** Issue #15 (workflow/audit service)
- ⚠️ **DEPENDS ON:** Issue #6 (project context)

## Acceptance Criteria
- Dashboard shows accurate project overview
- Quick stats update in real-time
- Quick actions navigate to correct pages
- Dashboard is the default landing page after project selection"

# UX & Polish Issues (23-26)

echo "Creating Issue #23: Implement responsive design"
gh issue create --repo "${REPO}" \
  --title "Implement responsive design" \
  --label "step:1,client,ux,responsive" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 4-5 hours

## Description
Make all UI components responsive for mobile and tablet devices.

## Tasks
- [ ] Add responsive breakpoints (mobile: <640px, tablet: 640-1024px, desktop: >1024px)
- [ ] Make RAID list responsive (switch to card view on mobile)
- [ ] Make workflow stage indicator responsive (vertical on mobile)
- [ ] Ensure modals are mobile-friendly
- [ ] Test all forms on mobile devices
- [ ] Add touch-friendly interactions (larger tap targets)
- [ ] Ensure navigation works on mobile
- [ ] Test on actual devices (iOS, Android)

## Dependencies
- ⚠️ **DEPENDS ON:** All UI components (Issues #9-22)

## Acceptance Criteria
- All pages work on mobile (320px width)
- All pages work on tablet (768px width)
- Touch interactions work smoothly
- No horizontal scrolling on any device"

echo "Creating Issue #24: Implement accessibility (A11y)"
gh issue create --repo "${REPO}" \
  --title "Implement accessibility (A11y)" \
  --label "step:1,client,ux,accessibility" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-5 hours

## Description
Ensure all UI components meet WCAG 2.1 Level AA accessibility standards.

## Tasks
- [ ] Add keyboard navigation support (Tab, Enter, Escape)
- [ ] Add ARIA labels to all interactive elements
- [ ] Add ARIA live regions for dynamic content
- [ ] Ensure focus indicators are visible
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Ensure color contrast meets WCAG AA (4.5:1 ratio)
- [ ] Add skip-to-content links
- [ ] Ensure all forms have proper labels
- [ ] Test with keyboard only (no mouse)

## Dependencies
- ⚠️ **DEPENDS ON:** All UI components (Issues #9-22)

## Acceptance Criteria
- All pages are keyboard navigable
- Screen reader announces content correctly
- Color contrast passes WCAG AA
- Focus indicators are visible
- No accessibility errors in Lighthouse audit"

echo "Creating Issue #25: Add empty states and loading states"
gh issue create --repo "${REPO}" \
  --title "Add empty states and loading states" \
  --label "step:1,client,ux,polish" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 3-4 hours

## Description
Add helpful empty states and skeleton loaders throughout the app.

## Tasks
- [ ] Create \"No projects yet\" empty state with \"Create Project\" CTA
- [ ] Create \"No RAID items\" empty state with \"Add RAID\" CTA
- [ ] Create \"No audit events\" empty state
- [ ] Add skeleton loaders for RAID list
- [ ] Add skeleton loaders for workflow state
- [ ] Add skeleton loaders for project list
- [ ] Add loading spinners for buttons during API calls
- [ ] Ensure loading states show immediately (no delay)

## Dependencies
- ⚠️ **DEPENDS ON:** All list/table components

## Acceptance Criteria
- Empty states show helpful messages
- Empty states have clear CTAs
- Skeleton loaders match final content shape
- Loading states prevent double-clicks"

echo "Creating Issue #26: Add success messages and confirmations"
gh issue create --repo "${REPO}" \
  --title "Add success messages and confirmations" \
  --label "step:1,client,ux,polish" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 3-4 hours

## Description
Add success notifications and confirmation dialogs for critical actions.

## Tasks
- [ ] Add success toast after creating RAID item
- [ ] Add success toast after updating RAID item
- [ ] Add success toast after workflow transition
- [ ] Add success toast after creating project
- [ ] Add confirmation dialog before deleting RAID item
- [ ] Add confirmation dialog before critical workflow transitions
- [ ] Add undo functionality for delete actions (stretch goal)
- [ ] Ensure all success messages are specific and helpful

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #5 (notifications)
- ⚠️ **DEPENDS ON:** All CRUD operations

## Acceptance Criteria
- Success messages appear after every create/update
- Confirmation dialogs prevent accidental deletes
- Messages are specific (\"RAID item created\" not \"Success\")
- Toasts auto-dismiss after 5 seconds"

# Testing Issues (27-32)

echo "Creating Issue #27: Write RAID component unit tests"
gh issue create --repo "${REPO}" \
  --title "Write RAID component unit tests" \
  --label "step:1,client,testing,raid" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-5 hours

## Description
Write comprehensive unit tests for all RAID components.

## Tasks
- [ ] Test RAIDList renders items correctly
- [ ] Test RAIDFilters updates filters correctly
- [ ] Test RAIDDetail displays and edits items
- [ ] Test RAIDCreateModal validates and submits
- [ ] Test RAIDBadge renders with correct colors
- [ ] Mock API calls with test data
- [ ] Achieve 80%+ code coverage
- [ ] Use React Testing Library

## Dependencies
- ⚠️ **DEPENDS ON:** All RAID components (Issues #9-13)

## Acceptance Criteria
- All RAID components have unit tests
- Tests pass consistently
- Coverage is 80%+ for RAID components"

echo "Creating Issue #28: Write workflow component unit tests"
gh issue create --repo "${REPO}" \
  --title "Write workflow component unit tests" \
  --label "step:1,client,testing,workflow" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-5 hours

## Description
Write comprehensive unit tests for all workflow components.

## Tasks
- [ ] Test WorkflowStageIndicator displays states correctly
- [ ] Test WorkflowTransitionModal shows valid transitions
- [ ] Test AuditTrail renders events correctly
- [ ] Test WorkflowPanel integrates components
- [ ] Mock API calls with test data
- [ ] Achieve 80%+ code coverage
- [ ] Use React Testing Library

## Dependencies
- ⚠️ **DEPENDS ON:** All workflow components (Issues #16-19)

## Acceptance Criteria
- All workflow components have unit tests
- Tests pass consistently
- Coverage is 80%+ for workflow components"

echo "Creating Issue #29: Write Playwright E2E tests for RAID"
gh issue create --repo "${REPO}" \
  --title "Write Playwright E2E tests for RAID" \
  --label "step:1,client,testing,e2e,raid" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 5-6 hours

## Description
Write end-to-end tests for RAID workflows using Playwright.

## Tasks
- [ ] Test: Create project → Open RAID list → List is empty
- [ ] Test: Create RAID risk → Verify appears in list
- [ ] Test: Filter RAID items by type → Verify filtering works
- [ ] Test: Click RAID item → Detail view opens → Edit → Save → Verify update
- [ ] Test: Delete RAID item → Confirm → Verify removed from list
- [ ] Ensure tests use test database (not production)
- [ ] Add CI integration
- [ ] Document test setup in e2e/README.md

## Dependencies
- ⚠️ **DEPENDS ON:** All RAID UI components complete
- ⚠️ **DEPENDS ON:** Backend API running

## Acceptance Criteria
- E2E tests pass consistently (no flakiness)
- Tests cover happy path and error cases
- Tests run in CI successfully"

echo "Creating Issue #30: Write Playwright E2E tests for workflow"
gh issue create --repo "${REPO}" \
  --title "Write Playwright E2E tests for workflow" \
  --label "step:1,client,testing,e2e,workflow" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 4-5 hours

## Description
Write end-to-end tests for workflow transitions using Playwright.

## Tasks
- [ ] Test: Create project → Verify starts in Initiating state
- [ ] Test: Transition Initiating → Planning → Verify state changes
- [ ] Test: Transition Planning → Executing → Verify state changes
- [ ] Test: Verify invalid transitions are blocked
- [ ] Test: View audit trail → Verify transitions are logged
- [ ] Ensure tests use test database
- [ ] Add CI integration
- [ ] Document test setup

## Dependencies
- ⚠️ **DEPENDS ON:** All workflow UI components complete
- ⚠️ **DEPENDS ON:** Backend API running

## Acceptance Criteria
- E2E tests pass consistently
- Tests cover all valid workflow transitions
- Tests run in CI successfully"

echo "Creating Issue #31: Write integration tests for API services"
gh issue create --repo "${REPO}" \
  --title "Write integration tests for API services" \
  --label "step:1,client,testing,integration" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 2-3 hours

## Description
Write integration tests for API service layers with mock server.

## Tasks
- [ ] Set up MSW (Mock Service Worker) or similar
- [ ] Test RAID service with mocked API responses
- [ ] Test workflow service with mocked API responses
- [ ] Test audit service with mocked API responses
- [ ] Test error handling (4xx, 5xx responses)
- [ ] Test retry logic and timeouts
- [ ] Achieve 80%+ coverage for services

## Dependencies
- ⚠️ **DEPENDS ON:** Issue #8 (RAID service)
- ⚠️ **DEPENDS ON:** Issue #15 (workflow service)

## Acceptance Criteria
- Integration tests pass consistently
- Services handle errors gracefully
- Coverage is 80%+ for service layer"

echo "Creating Issue #32: Write performance tests"
gh issue create --repo "${REPO}" \
  --title "Write performance tests" \
  --label "step:1,client,testing,performance" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 2-4 hours

## Description
Test app performance with large datasets.

## Tasks
- [ ] Test RAID list with 100+ items
- [ ] Test RAID list with 500+ items
- [ ] Test workflow transitions under load
- [ ] Measure render times for key pages
- [ ] Test filtering/sorting performance
- [ ] Identify performance bottlenecks
- [ ] Add pagination if lists are too slow
- [ ] Document performance benchmarks

## Dependencies
- ⚠️ **DEPENDS ON:** All UI components complete

## Acceptance Criteria
- RAID list with 100 items loads in <1 second
- Filtering/sorting is instant (<100ms)
- No UI freezing or lag
- Performance baseline documented"

# Documentation Issues (33-35)

echo "Creating Issue #33: Update client README to reflect actual features"
gh issue create --repo "${REPO}" \
  --title "Update client README to reflect actual features" \
  --label "step:1,client,documentation" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 2-3 hours

## Description
Rewrite README.md to accurately describe the project management UI.

## Tasks
- [ ] Remove outdated chat interface description
- [ ] Add section on RAID management features
- [ ] Add section on ISO 21500 workflow features
- [ ] Add section on project management features
- [ ] Update screenshots to show RAID and workflow UI
- [ ] Update feature list
- [ ] Update setup instructions if needed
- [ ] Add troubleshooting section

## Dependencies
- ⚠️ **DEPENDS ON:** All UI features complete

## Acceptance Criteria
- README accurately describes current features
- Screenshots show actual UI (not chat interface)
- Setup instructions are correct
- No mention of unimplemented features"

echo "Creating Issue #34: Update PLAN.md to clarify Step 1 scope"
gh issue create --repo "${REPO}" \
  --title "Update PLAN.md to clarify Step 1 scope" \
  --label "step:1,documentation" \
  \
  --body "**Priority:** 🟡 High
**Estimated:** 2-3 hours

## Description
Update main project plan to clarify Step 1 vs Step 2 scope.

## Tasks
- [ ] Clarify that Step 1 = RAID + Workflow only
- [ ] Move templates/blueprints to Step 2
- [ ] Move proposal system to Step 2
- [ ] Move cross-artifact audits to Step 2
- [ ] Update Step 1 definition to match step-1.yml
- [ ] Add \"What's NOT in Step 1\" section
- [ ] Update project timeline if needed
- [ ] Ensure consistency between PLAN.md and step-1.yml

## Dependencies
- ⚠️ **DEPENDS ON:** Step 1 implementation complete

## Acceptance Criteria
- Step 1 scope is clearly defined
- No confusion about what's in Step 1 vs Step 2
- PLAN.md and step-1.yml are consistent
- Timeline is realistic"

echo "Creating Issue #35: Write client test documentation"
gh issue create --repo "${REPO}" \
  --title "Write client test documentation" \
  --label "step:1,client,documentation,testing" \
  \
  --body "**Priority:** 🟢 Medium
**Estimated:** 2-3 hours

## Description
Document testing strategy, setup, and execution for client tests.

## Tasks
- [ ] Create or update \`client/tests/README.md\`
- [ ] Document unit test setup and execution
- [ ] Document integration test setup and execution
- [ ] Document E2E test setup and execution
- [ ] Add CI/CD testing documentation
- [ ] Document test coverage requirements (80%+)
- [ ] Add examples of writing new tests
- [ ] Document mocking strategies

## Dependencies
- ⚠️ **DEPENDS ON:** All testing issues complete (Issues #27-32)

## Acceptance Criteria
- Test documentation is comprehensive
- New developers can run tests following docs
- All test types are documented
- Examples are clear and helpful"

echo ""
echo -e "${GREEN}✅ All 35 GitHub issues created successfully!${NC}"
echo ""
echo "View issues at: https://github.com/${REPO}/issues"
echo "View milestone at: https://github.com/${REPO}/milestone/1"
