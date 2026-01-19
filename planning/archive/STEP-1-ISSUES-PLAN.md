# Step 1 Issues Plan - Missing Client Implementation

**Date:** 2026-01-18  
**Purpose:** Break down missing Step 1 client features into actionable GitHub issues

---

## 📊 Issue Summary

**Total Issues:** 35 issues (expanded for full solution)

**Breakdown by Category:**

- 🏗️ Infrastructure & Setup: 6 issues (+3 for project context, state mgmt, error handling)
- 🎨 RAID UI Components: 7 issues (unchanged)
- 🔄 Workflow UI Components: 6 issues (unchanged)
- 💼 Project Management UI: 3 issues (NEW - project list, create, dashboard)
- 🎯 UX & Polish: 4 issues (NEW - notifications, responsive, accessibility, empty states)
- 🧪 Testing: 6 issues (+2 for integration tests, performance)
- 📚 Documentation: 3 issues (unchanged)

**Estimated Timeline:** 5-6 weeks for full production-ready solution

**Changes from Original Plan:**

- Added project context management and selection UI
- Added state management layer (Context/Zustand)
- Added global error handling and notifications
- Added UX polish (responsive, accessible, empty states)
- Added integration tests and performance testing
- Total issues: 23 → 35 (still under 40 limit)

---

## 🎯 Issue Categories & Dependencies

### Category 1: Infrastructure & Setup (Issues #1-3)

**Must be completed FIRST - All other issues depend on these**

#### Issue #1: Set up client API service layer

**Priority:** 🔴 Critical - BLOCKER  
**Estimated:** 4-6 hours  
**Labels:** `step:1`, `client`, `infrastructure`, `blocker`

**Description:**
Create typed API client service for backend integration.

**Tasks:**

- [ ] Create `src/services/apiClient.ts` with typed fetch wrapper
- [ ] Add error handling and loading states
- [ ] Add API response type definitions
- [ ] Configure base URL and environment variables
- [ ] Add request/response interceptors
- [ ] Write unit tests for API client

**Dependencies:** None (MUST BE FIRST)

**Acceptance Criteria:**

- API client can make typed requests to backend
- Error handling works for 4xx/5xx responses
- Unit tests pass

---

#### Issue #2: Add project management routing

**Priority:** 🔴 Critical - BLOCKER  
**Estimated:** 3-4 hours  
**Labels:** `step:1`, `client`, `infrastructure`, `blocker`

**Description:**
Set up routing for RAID and workflow management pages.

**Tasks:**

- [ ] Update `App.tsx` to add project management routes
- [ ] Create route structure: `/projects/:key/raid`, `/projects/:key/workflow`
- [ ] Add navigation links in sidebar/header
- [ ] Create project context provider
- [ ] Add route guards if needed

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #1 (API service layer)

**Acceptance Criteria:**

- Routes are accessible and render placeholder pages
- Navigation works between routes
- Project context is available to child components

---

#### Issue #3: Create shared UI component library

**Priority:** 🟡 High  
**Estimated:** 4-5 hours  
**Labels:** `step:1`, `client`, `infrastructure`, `ui`

**Description:**
Build reusable UI components for consistent design.

**Tasks:**

- [ ] Create `Button` component with variants
- [ ] Create `Modal` component with overlay
- [ ] Create `Table` component with sorting
- [ ] Create `Badge` component for status indicators
- [ ] Create `Form` components (Input, Select, Textarea)
- [ ] Add TypeScript prop types
- [ ] Write Storybook stories (optional)

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #2 (routing setup)

**Acceptance Criteria:**

- All components are typed and reusable
- Components follow consistent styling
- Examples/documentation exists

---

#### Issue #4: Implement state management layer

**Priority:** 🟡 High  
**Estimated:** 4-5 hours  
**Labels:** `step:1`, `client`, `infrastructure`, `state-management`

**Description:**
Set up state management for projects, RAID, and workflow data.

**Tasks:**

- [ ] Choose state management solution (React Context or Zustand)
- [ ] Create project context provider
- [ ] Create RAID state management
- [ ] Create workflow state management
- [ ] Implement loading and error states
- [ ] Add state persistence (localStorage for UI preferences)
- [ ] Write unit tests for state logic

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #1 (API service)
- ⚠️ **DEPENDS ON:** Issue #2 (routing)

**Acceptance Criteria:**

- State is accessible throughout app via hooks
- Loading/error states managed consistently
- State updates trigger re-renders correctly
- Unit tests pass

---

#### Issue #5: Build global error handling and notifications

**Priority:** 🟡 High  
**Estimated:** 3-4 hours  
**Labels:** `step:1`, `client`, `infrastructure`, `ux`

**Description:**
Create global error boundary and toast notification system.

**Tasks:**

- [ ] Create `ErrorBoundary` component for React errors
- [ ] Create toast notification system (success/error/info/warning)
- [ ] Add global error handler for API errors
- [ ] Create `useNotification` hook
- [ ] Style notifications (top-right corner, auto-dismiss)
- [ ] Add notification queue management
- [ ] Write unit tests

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #3 (UI components)

**Acceptance Criteria:**

- React errors are caught and displayed gracefully
- API errors show user-friendly notifications
- Notifications auto-dismiss after 5 seconds
- Multiple notifications queue properly
- Unit tests pass

---

#### Issue #6: Create project context and selection UI

**Priority:** 🟡 High  
**Estimated:** 5-6 hours  
**Labels:** `step:1`, `client`, `infrastructure`, `project-mgmt`

**Description:**
Build UI for selecting/switching between projects.

**Tasks:**

- [ ] Create `ProjectContext` provider
- [ ] Create `ProjectSelector` dropdown component
- [ ] Fetch project list from API
- [ ] Store selected project in localStorage
- [ ] Add project switching logic
- [ ] Update route params when project changes
- [ ] Add "No project selected" empty state
- [ ] Write unit tests

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #1 (API service)
- ⚠️ **DEPENDS ON:** Issue #2 (routing)
- ⚠️ **DEPENDS ON:** Issue #4 (state management)

**Acceptance Criteria:**

- User can select a project from dropdown
- Selected project persists across page reloads
- All RAID/workflow views use selected project
- Empty state shows when no project exists
- Unit tests pass

---

### Category 2: RAID UI Implementation (Issues #7-13)

#### Issue #7: Create RAID data models and types

**Priority:** 🟡 High  
**Estimated:** 2-3 hours  
**Labels:** `step:1`, `client`, `raid`, `types`

**Description:**
Define TypeScript interfaces for RAID data matching backend API.

**Tasks:**

- [ ] Create `src/types/raid.ts` with RAIDEntry interface
- [ ] Add RAIDType enum (Risk/Assumption/Issue/Dependency)
- [ ] Add RAIDStatus enum (Open/In Progress/Resolved/Closed)
- [ ] Add RAIDPriority enum
- [ ] Add RAIDImpactLevel and RAIDLikelihood enums
- [ ] Add API request/response types

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #1 (API service)

**Acceptance Criteria:**

- Types match backend API exactly
- All enums are defined
- Types are exported and reusable

---

#### Issue #5: Implement RAID API service

**Priority:** 🟡 High  
**Estimated:** 3-4 hours  
**Labels:** `step:1`, `client`, `raid`, `api`

**Description:**
Create service for RAID CRUD operations.

**Tasks:**

- [ ] Create `src/services/raidService.ts`
- [ ] Implement `listRAID(projectKey, filters?)`
- [ ] Implement `getRAID(projectKey, raidId)`
- [ ] Implement `createRAID(projectKey, data)`
- [ ] Implement `updateRAID(projectKey, raidId, data)`
- [ ] Implement `deleteRAID(projectKey, raidId)`
- [ ] Add error handling for all methods
- [ ] Write unit tests with mocked API

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #1 (API service)
- ⚠️ **DEPENDS ON:** Issue #4 (RAID types)

**Acceptance Criteria:**

- All CRUD operations work
- Filtering works (type, status, owner, due date)
- Unit tests pass with mocked responses

---

#### Issue #6: Build RAID list view component

**Priority:** 🟡 High  
**Estimated:** 6-8 hours  
**Labels:** `step:1`, `client`, `raid`, `ui`

**Description:**
Create main RAID list view with table and filters.

**Tasks:**

- [ ] Create `src/components/raid/RAIDListView.tsx`
- [ ] Implement table with columns: type, title, status, owner, priority, due date
- [ ] Add sorting by any column
- [ ] Add "Create New" button
- [ ] Handle loading and error states
- [ ] Show empty state when no RAID items
- [ ] Implement pagination if needed
- [ ] Write unit tests for component

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #2 (routing)
- ⚠️ **DEPENDS ON:** Issue #3 (Table component)
- ⚠️ **DEPENDS ON:** Issue #5 (RAID service)

**Acceptance Criteria:**

- Table displays RAID items from API
- Sorting works on all columns
- Loading/error states display correctly
- Unit tests pass

---

#### Issue #7: Build RAID filter panel

**Priority:** 🟡 High  
**Estimated:** 4-5 hours  
**Labels:** `step:1`, `client`, `raid`, `ui`

**Description:**
Create filter controls for RAID list.

**Tasks:**

- [ ] Create `src/components/raid/RAIDFilters.tsx`
- [ ] Add filter by type (Risk/Assumption/Issue/Dependency)
- [ ] Add filter by status (Open/In Progress/Resolved/Closed)
- [ ] Add filter by owner (text input or select)
- [ ] Add filter by due date range (date picker)
- [ ] Implement "Clear Filters" button
- [ ] Update URL query params when filters change
- [ ] Write unit tests

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #3 (Form components)
- ⚠️ **DEPENDS ON:** Issue #6 (RAID list view)

**Acceptance Criteria:**

- All filter controls work
- Filters update the RAID list
- URL reflects current filters (shareable)
- Unit tests pass

---

#### Issue #8: Build RAID detail/edit view

**Priority:** 🟡 High  
**Estimated:** 5-6 hours  
**Labels:** `step:1`, `client`, `raid`, `ui`

**Description:**
Create detailed view for viewing/editing single RAID item.

**Tasks:**

- [ ] Create `src/components/raid/RAIDDetailView.tsx`
- [ ] Display all RAID fields (type, title, description, status, etc.)
- [ ] Add edit mode toggle
- [ ] Implement form validation
- [ ] Add save/cancel buttons
- [ ] Add delete button with confirmation
- [ ] Handle API errors
- [ ] Write unit tests

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #3 (Form components, Modal)
- ⚠️ **DEPENDS ON:** Issue #5 (RAID service)

**Acceptance Criteria:**

- Can view all RAID details
- Can edit and save changes
- Validation prevents invalid data
- Delete requires confirmation
- Unit tests pass

---

#### Issue #9: Build RAID create modal

**Priority:** 🟡 High  
**Estimated:** 4-5 hours  
**Labels:** `step:1`, `client`, `raid`, `ui`

**Description:**
Create modal for creating new RAID items.

**Tasks:**

- [ ] Create `src/components/raid/RAIDCreateModal.tsx`
- [ ] Add form fields: type, title, description, status, owner, priority, impact, likelihood, due date
- [ ] Implement form validation (required fields)
- [ ] Add create/cancel buttons
- [ ] Handle API errors
- [ ] Close modal on successful creation
- [ ] Write unit tests

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #3 (Modal, Form components)
- ⚠️ **DEPENDS ON:** Issue #5 (RAID service)

**Acceptance Criteria:**

- Modal opens/closes correctly
- Form validation works
- Can create new RAID items
- Unit tests pass

---

#### Issue #10: Build RAID status badge component

**Priority:** 🟢 Medium  
**Estimated:** 2-3 hours  
**Labels:** `step:1`, `client`, `raid`, `ui`

**Description:**
Create visual indicators for RAID types and statuses.

**Tasks:**

- [ ] Create `src/components/raid/RAIDStatusBadge.tsx`
- [ ] Add color coding for RAID types (Risk=red, Issue=orange, etc.)
- [ ] Add color coding for statuses (Open=blue, Resolved=green, etc.)
- [ ] Add color coding for priorities (Critical=red, High=orange, etc.)
- [ ] Add icons for each type/status (optional)
- [ ] Write unit tests

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #3 (Badge component)
- ⚠️ **DEPENDS ON:** Issue #4 (RAID types)

**Acceptance Criteria:**

- Badges display with correct colors
- All types/statuses have visual representation
- Component is reusable
- Unit tests pass

---

### Category 3: Workflow UI Implementation (Issues #11-16)

#### Issue #11: Create workflow data models and types

**Priority:** 🟡 High  
**Estimated:** 2-3 hours  
**Labels:** `step:1`, `client`, `workflow`, `types`

**Description:**
Define TypeScript interfaces for ISO 21500 project workflows.

**Tasks:**

- [ ] Create `src/types/workflow.ts` with ProjectWorkflow interface
- [ ] Add WorkflowState enum (Initiating/Planning/Executing/Monitoring/Closing/Closed)
- [ ] Add WorkflowTransition interface
- [ ] Add AuditEvent interface
- [ ] Add API request/response types
- [ ] Document difference from agent workflows

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #1 (API service)

**Acceptance Criteria:**

- Types match backend API exactly
- ISO 21500 states are defined
- Types are distinct from agent workflow types
- Documentation clarifies usage

---

#### Issue #12: Implement workflow API service

**Priority:** 🟡 High  
**Estimated:** 3-4 hours  
**Labels:** `step:1`, `client`, `workflow`, `api`

**Description:**
Create service for workflow state management.

**Tasks:**

- [ ] Create `src/services/workflowService.ts`
- [ ] Implement `getWorkflowState(projectKey)`
- [ ] Implement `getAvailableTransitions(projectKey)`
- [ ] Implement `transitionState(projectKey, toState, note?)`
- [ ] Implement `getAuditEvents(projectKey, filters?)`
- [ ] Add error handling
- [ ] Write unit tests with mocked API

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #1 (API service)
- ⚠️ **DEPENDS ON:** Issue #11 (Workflow types)

**Acceptance Criteria:**

- All workflow operations work
- State transitions are validated
- Audit events are retrievable
- Unit tests pass

---

#### Issue #13: Build workflow stage indicator component

**Priority:** 🟡 High  
**Estimated:** 5-6 hours  
**Labels:** `step:1`, `client`, `workflow`, `ui`

**Description:**
Create visual indicator for ISO 21500 project stages.

**Tasks:**

- [ ] Create `src/components/workflow/WorkflowStageIndicator.tsx`
- [ ] Display all 6 stages (Initiating → Planning → Executing → Monitoring → Closing → Closed)
- [ ] Highlight current stage
- [ ] Show completed stages with checkmarks
- [ ] Make stages clickable to show details
- [ ] Add horizontal progress bar visual
- [ ] Write unit tests

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #2 (routing)
- ⚠️ **DEPENDS ON:** Issue #12 (Workflow service)

**Acceptance Criteria:**

- All 6 ISO 21500 stages display
- Current stage is clearly highlighted
- Visual matches ISO 21500 workflow
- Unit tests pass

---

#### Issue #14: Build workflow transition UI

**Priority:** 🟡 High  
**Estimated:** 4-5 hours  
**Labels:** `step:1`, `client`, `workflow`, `ui`

**Description:**
Create UI for transitioning between workflow states.

**Tasks:**

- [ ] Create `src/components/workflow/WorkflowTransitions.tsx`
- [ ] Display available transitions as buttons
- [ ] Add confirmation modal before transition
- [ ] Add optional note field in confirmation
- [ ] Show which transitions are invalid (disabled)
- [ ] Handle transition errors
- [ ] Refresh state after successful transition
- [ ] Write unit tests

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #3 (Modal, Button components)
- ⚠️ **DEPENDS ON:** Issue #12 (Workflow service)
- ⚠️ **DEPENDS ON:** Issue #13 (Stage indicator)

**Acceptance Criteria:**

- Only valid transitions are enabled
- Confirmation required before transition
- Transitions update state correctly
- Unit tests pass

---

#### Issue #15: Build audit trail viewer

**Priority:** 🟡 High  
**Estimated:** 4-5 hours  
**Labels:** `step:1`, `client`, `workflow`, `ui`

**Description:**
Create read-only viewer for workflow audit events.

**Tasks:**

- [ ] Create `src/components/workflow/WorkflowAuditTrail.tsx`
- [ ] Display audit events in reverse chronological order
- [ ] Show: timestamp, actor, event type, from/to states, note
- [ ] Add filtering by event type
- [ ] Add date range filtering
- [ ] Format timestamps as relative ("2 hours ago")
- [ ] Implement pagination/infinite scroll
- [ ] Write unit tests

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #3 (Table component)
- ⚠️ **DEPENDS ON:** Issue #12 (Workflow service)

**Acceptance Criteria:**

- All audit events display
- Events are sorted newest first
- Filtering works
- Timestamps are human-readable
- Unit tests pass

---

#### Issue #16: Refactor existing WorkflowPanel for ISO 21500

**Priority:** 🟠 Medium-High  
**Estimated:** 3-4 hours  
**Labels:** `step:1`, `client`, `workflow`, `refactor`

**Description:**
Update or replace current WorkflowPanel.tsx to support ISO 21500 workflows.

**Tasks:**

- [ ] Rename `WorkflowPanel.tsx` to `AgentWorkflowPanel.tsx` (preserve chat functionality)
- [ ] Create new `ProjectWorkflowPanel.tsx` for ISO 21500
- [ ] Update routing to use correct panel based on context
- [ ] Update types to distinguish agent vs project workflows
- [ ] Add comments explaining the difference
- [ ] Write unit tests for new panel

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issue #13 (Stage indicator)
- ⚠️ **DEPENDS ON:** Issue #14 (Transitions UI)
- ⚠️ **DEPENDS ON:** Issue #15 (Audit trail)

**Acceptance Criteria:**

- Agent workflows still work (chat interface)
- Project workflows show ISO 21500 stages
- Both coexist without conflicts
- Unit tests pass for both

---

### Category 4: Testing (Issues #17-20)

#### Issue #17: Write RAID component unit tests

**Priority:** 🟢 Medium  
**Estimated:** 4-5 hours  
**Labels:** `step:1`, `client`, `raid`, `testing`

**Description:**
Add comprehensive unit tests for all RAID components.

**Tasks:**

- [ ] Test RAIDListView rendering and interactions
- [ ] Test RAIDFilters state management
- [ ] Test RAIDDetailView edit mode
- [ ] Test RAIDCreateModal validation
- [ ] Test RAIDStatusBadge rendering
- [ ] Mock API calls in all tests
- [ ] Achieve >80% coverage for RAID components

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issues #6-10 (all RAID components)

**Acceptance Criteria:**

- All RAID components have unit tests
- Tests cover happy path and error cases
- Coverage exceeds 80%
- Tests pass in CI

---

#### Issue #18: Write workflow component unit tests

**Priority:** 🟢 Medium  
**Estimated:** 4-5 hours  
**Labels:** `step:1`, `client`, `workflow`, `testing`

**Description:**
Add comprehensive unit tests for all workflow components.

**Tasks:**

- [ ] Test WorkflowStageIndicator state visualization
- [ ] Test WorkflowTransitions button states
- [ ] Test WorkflowAuditTrail filtering
- [ ] Test ProjectWorkflowPanel integration
- [ ] Mock API calls in all tests
- [ ] Achieve >80% coverage for workflow components

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issues #13-16 (all workflow components)

**Acceptance Criteria:**

- All workflow components have unit tests
- Tests cover happy path and error cases
- Coverage exceeds 80%
- Tests pass in CI

---

#### Issue #19: Write Playwright E2E tests for RAID

**Priority:** 🟢 Medium  
**Estimated:** 5-6 hours  
**Labels:** `step:1`, `client`, `raid`, `testing`, `e2e`

**Description:**
Create end-to-end tests for RAID workflows using Playwright.

**Tasks:**

- [ ] Set up Playwright test environment
- [ ] Test: Open RAID list view
- [ ] Test: Filter RAID entries by type and status
- [ ] Test: Create new Risk entry
- [ ] Test: Edit existing Issue entry
- [ ] Test: Delete Dependency entry
- [ ] Test: Navigate to detail view
- [ ] Ensure tests run in CI

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issues #6-10 (all RAID UI)
- ⚠️ **REQUIRES:** Backend running for E2E

**Acceptance Criteria:**

- All RAID user workflows are tested
- Tests run reliably without flakiness
- Tests pass in CI
- Tests documented in e2e/README.md

---

#### Issue #20: Write Playwright E2E tests for workflow

**Priority:** 🟢 Medium  
**Estimated:** 4-5 hours  
**Labels:** `step:1`, `client`, `workflow`, `testing`, `e2e`

**Description:**
Create end-to-end tests for workflow transitions using Playwright.

**Tasks:**

- [ ] Test: View project in Initiating state
- [ ] Test: Transition to Planning state
- [ ] Test: Transition to Executing state
- [ ] Test: Transition between Executing ⇄ Monitoring
- [ ] Test: Attempt invalid transition (should fail)
- [ ] Test: View audit trail after transitions
- [ ] Test: State persists after page reload
- [ ] Ensure tests run in CI

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issues #13-16 (all workflow UI)
- ⚠️ **REQUIRES:** Backend running for E2E

**Acceptance Criteria:**

- All workflow transitions are tested
- Invalid transitions are tested
- Audit trail verification works
- Tests pass in CI
- Tests documented in e2e/README.md

---

### Category 5: Documentation (Issues #21-23)

#### Issue #21: Update client README to reflect actual features

**Priority:** 🟡 High  
**Estimated:** 2-3 hours  
**Labels:** `step:1`, `client`, `documentation`

**Description:**
Correct client README.md to accurately describe current state.

**Tasks:**

- [ ] Remove claims about "project management capabilities" (until implemented)
- [ ] Document that client is currently a chat interface
- [ ] Add section explaining Step 1 implementation status
- [ ] Link to STEP-1-STATUS.md and STEP-1-COMPLETION-PLAN.md
- [ ] Update feature list to match reality
- [ ] Add "Coming Soon" section for RAID and workflow UIs

**Dependencies:**

- ⚠️ **CAN START IMMEDIATELY** (no dependencies)

**Acceptance Criteria:**

- README accurately describes current features
- No misleading claims about unimplemented features
- Clear roadmap section exists
- Links to planning documents work

---

#### Issue #22: Update PLAN.md to clarify Step 1 scope

**Priority:** 🟡 High  
**Estimated:** 2-3 hours  
**Labels:** `step:1`, `backend`, `documentation`

**Description:**
Align PLAN.md with actual step-1.yml requirements.

**Tasks:**

- [ ] Clarify Step 1 = RAID + Workflow only
- [ ] Move templates/blueprints description to Step 2 section
- [ ] Move proposals description to Step 2 section
- [ ] Move cross-artifact audits to Step 2 section
- [ ] Update "Step 1 Outcomes" section
- [ ] Add table comparing PLAN.md vs step-1.yml
- [ ] Sync changes to docs/project-plan.md

**Dependencies:**

- ⚠️ **CAN START IMMEDIATELY** (no dependencies)

**Acceptance Criteria:**

- PLAN.md clearly describes minimal Step 1
- No confusion about Step 1 vs Step 2 scope
- step-1.yml and PLAN.md are aligned
- docs/project-plan.md is updated

---

#### Issue #23: Write client test documentation

**Priority:** 🟢 Medium  
**Estimated:** 2-3 hours  
**Labels:** `step:1`, `client`, `documentation`, `testing`

**Description:**
Create/update testing documentation for client.

**Tasks:**

- [ ] Create/update `client/tests/README.md`
- [ ] Document how to run unit tests
- [ ] Document how to run E2E tests
- [ ] Document test file organization
- [ ] Add examples of writing tests
- [ ] Document CI integration
- [ ] Add troubleshooting section

**Dependencies:**

- ⚠️ **DEPENDS ON:** Issues #17-20 (all tests implemented)

**Acceptance Criteria:**

- Tests/README.md exists with comprehensive guide
- All test commands are documented
- Examples help developers write new tests
- CI integration is explained

---

## 📋 Implementation Order & Phases

### Phase 1: Foundation (Week 1)

**Critical Path - Must complete first**

1. Issue #1: API service layer (BLOCKER)
2. Issue #2: Routing (BLOCKER)
3. Issue #3: UI components (HIGH)
4. Issue #21: Update client README (HIGH)
5. Issue #22: Update PLAN.md (HIGH)

**Milestone:** Infrastructure ready for feature development

---

### Phase 2: RAID Implementation (Week 2)

**Parallel work possible after Phase 1**

6. Issue #4: RAID types (HIGH)
7. Issue #5: RAID API service (HIGH)
8. Issue #10: RAID badges (can start early)
9. Issue #6: RAID list view (HIGH)
10. Issue #7: RAID filters (HIGH)
11. Issue #8: RAID detail view (HIGH)
12. Issue #9: RAID create modal (HIGH)

**Milestone:** RAID management fully functional

---

### Phase 3: Workflow Implementation (Week 3)

**Can overlap with Phase 2 testing**

13. Issue #11: Workflow types (HIGH)
14. Issue #12: Workflow API service (HIGH)
15. Issue #13: Stage indicator (HIGH)
16. Issue #14: Transition UI (HIGH)
17. Issue #15: Audit trail viewer (HIGH)
18. Issue #16: Refactor WorkflowPanel (MEDIUM)

**Milestone:** Workflow management fully functional

---

### Phase 4: Testing & Documentation (Week 4)

**Final validation phase**

19. Issue #17: RAID unit tests (MEDIUM)
20. Issue #18: Workflow unit tests (MEDIUM)
21. Issue #19: RAID E2E tests (MEDIUM)
22. Issue #20: Workflow E2E tests (MEDIUM)
23. Issue #23: Test documentation (MEDIUM)

**Milestone:** Step 1 100% complete

---

## 🚀 Quick Start Guide for Contributors

### Before Starting Any Issue

1. **Read STEP-1-STATUS.md** - Understand what's missing
2. **Read STEP-1-COMPLETION-PLAN.md** - See the implementation roadmap
3. **Check dependencies** - Ensure prerequisite issues are complete
4. **Pull latest main** - Start with up-to-date code

### Recommended Work Order

**Solo Developer:**

- Follow Phase 1 → Phase 2 → Phase 3 → Phase 4 sequentially

**Team of 2:**

- Dev 1: Phase 1 → Phase 2 (RAID)
- Dev 2: Phase 1 (help) → Phase 3 (Workflow)
- Both: Phase 4 (Testing) together

**Team of 3+:**

- Dev 1: Phase 1 (lead) → Phase 2 (RAID)
- Dev 2: Phase 3 (Workflow) - wait for Phase 1 completion
- Dev 3: Documentation (Issues #21, #22) → Testing (Phase 4)

### Tips for AI Agent Collaboration

- **Small commits**: Each issue should be 1-2 commits
- **Test early**: Run tests after each component
- **Document as you go**: Add JSDoc comments
- **PR per issue**: One issue = one pull request
- **Reference issue**: Include "Fixes #XX" in PR description

### Avoiding Merge Conflicts

**High Risk Areas:**

- `App.tsx` (routing) - Issues #2, #16
- `src/types/` - Issues #4, #11
- `src/services/` - Issues #5, #12

**Mitigation:**

- Complete Issue #2 before starting any UI work
- Complete Issue #4 before Issue #5
- Complete Issue #11 before Issue #12
- Don't work on same file simultaneously

### CI/CD Requirements

Each PR must:

- ✅ Pass `npm run lint`
- ✅ Pass `npm run build`
- ✅ Pass `npm run test` (when tests exist)
- ✅ Include unit tests for new components
- ✅ Update relevant documentation

---

## 📊 Progress Tracking

**Current Status:** 0/23 issues complete (0%)

**When to Update STEP-1-STATUS.md:**

- After Phase 2: Update "Client Issue 4" status
- After Phase 3: Update "Client Issue 5" status
- After Phase 4: Update "Client Issue 6" status and overall conclusion

**Definition of Done:**

- All 23 issues closed
- All tests passing in CI
- Client README accurately describes features
- STEP-1-STATUS.md shows Step 1 = 100% complete

---

## 🔗 Related Documents

- [STEP-1-STATUS.md](STEP-1-STATUS.md) - Current status with TODO analysis
- [STEP-1-COMPLETION-PLAN.md](STEP-1-COMPLETION-PLAN.md) - Detailed implementation plan
- [planning/issues/step-1.yml](planning/issues/step-1.yml) - Original requirements
- [PLAN.md](PLAN.md) - Project master plan
- [Backend API Docs](docs/api/client-integration-guide.md) - API integration guide

---

## ❓ Questions or Issues?

If you encounter:

- **Unclear requirements** → Check STEP-1-STATUS.md TODO section
- **API questions** → See backend docs/api/client-integration-guide.md
- **Dependency conflicts** → Verify prerequisite issues are complete
- **Breaking changes needed** → Create issue for discussion first

**Contact:** Reference GitHub issues for discussion and clarification.
