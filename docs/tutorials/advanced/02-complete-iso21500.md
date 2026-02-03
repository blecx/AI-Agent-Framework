# Complete ISO 21500 Project Lifecycle

**Estimated Time:** 60 minutes  
**Difficulty:** Advanced  
**Prerequisites:** TUI Basics, GUI Basics, Hybrid Workflows tutorial

## Overview

This tutorial walks through a complete ISO 21500 project lifecycle for a real-world example: building a Todo Application MVP. You'll experience all five process groups (Initiating, Planning, Executing, Monitoring & Controlling, Closing) and learn how the framework supports each phase.

## Project: Todo Application MVP

**Business Context:**
- **Goal:** Launch a web-based todo application for small teams (5-10 users)
- **Timeline:** 9 weeks from project kickoff to production launch
- **Team:** 1 Project Manager, 2 Developers, 1 QA Engineer, 1 Designer
- **Budget:** $50,000 (estimated)
- **Success Criteria:** 
  - 90% of user stories completed
  - < 5 critical bugs in production
  - User satisfaction score > 4.0/5.0
  - Launch on time (Week 9)

## ISO 21500 Process Groups Overview

| Phase | Duration | Key Activities | Artifacts |
|-------|----------|---------------|-----------|
| **Initiating** | Week 1 | Charter, stakeholders, initial RAID | Charter, stakeholder list |
| **Planning** | Week 2-3 | WBS, schedule, budget, detailed RAID | WBS, schedule, risk register |
| **Executing** | Week 4-8 | Development, code artifacts, testing | Code, tests, builds |
| **Monitoring** | Continuous | Progress tracking, gap assessment, issue resolution | Status reports, gap analysis |
| **Closing** | Week 9 | Lessons learned, handover, archive | Closure report, retrospective |

## Timeline Diagram

```
Week:  1      2    3      4    5    6    7    8      9
      ┌─────┬────┬────┬────┬────┬────┬────┬────┬─────┐
Phase:│Init │ Planning │      Executing        │Close│
      │     │          │                       │     │
      └─────┴──────────┴───────────────────────┴─────┘
                         ↑
                  Monitoring (Continuous)
```

## Part 1: Initiating (Week 1)

### Step 1: Create Project

```bash
cd apps/tui
python main.py projects create \
  --key "TODO" \
  --name "Todo App MVP" \
  --description "Web-based task management application for small teams (5-10 users). Features: user auth, task CRUD, priority levels, due dates, team collaboration."
```

**Output:**
```
✓ Project created: TODO
  Name: Todo App MVP
  Workflow State: Initiating
  Path: projectDocs/TODO/
  Git repository initialized
```

**Verification:**
```bash
# Check project structure
ls -R projectDocs/TODO/
```

**Expected:**
```
projectDocs/TODO/:
artifacts/  raid/  workflow/

projectDocs/TODO/artifacts/:
(empty)

projectDocs/TODO/raid/:
register.json

projectDocs/TODO/workflow/:
state.json
```

### Step 2: Identify Stakeholders

Create stakeholder register:

```bash
python main.py artifacts create --project TODO \
  --type stakeholders \
  --title "Stakeholder Register" \
  --prompt "Create a stakeholder register for the Todo App MVP project. Include: Product Owner (Sarah Chen), Dev Team Lead (Mike Johnson), QA Lead (Priya Patel), UX Designer (Alex Kim), End Users (small team managers), and Executive Sponsor (CTO David Liu). For each, document: role, interest level (High/Medium/Low), influence level, communication preferences, and key concerns."
```

**Output:**
```
✓ Artifact created: artifacts/stakeholders.md
  Generated content: 2.1 KB
```

**Review in GUI:**
1. Open http://localhost:5173
2. Select project "TODO"
3. Navigate to "Artifacts" → "stakeholders.md"
4. Verify all stakeholders are listed with contact info

### Step 3: Create Project Charter

```bash
python main.py artifacts create --project TODO \
  --type charter \
  --title "Todo App Project Charter" \
  --prompt "Create a comprehensive project charter for the Todo App MVP. Include: Executive Summary, Project Purpose and Justification (address market gap for simple team task management), Project Objectives (quantifiable goals), High-Level Requirements (user auth, task CRUD, priority levels, due dates), Key Milestones (Alpha Week 4, Beta Week 6, Launch Week 9), Budget Summary ($50k), Assumptions (team available full-time, no scope creep), Constraints (9-week timeline, budget cap), Risks (high-level only), and Success Criteria (90% stories done, <5 critical bugs, 4.0+ user rating). Stakeholders: Sarah Chen (Product Owner), David Liu (Executive Sponsor)."
```

**Output:**
```
✓ Artifact created: artifacts/charter.md
  Generated content: 4.8 KB
```

**Verification:**
```bash
# View charter
cat projectDocs/TODO/artifacts/charter.md | head -30
```

### Step 4: Initial RAID Register

Add high-level risks and assumptions from charter:

```bash
# High-priority risks
python main.py raid add --project TODO --type risk --severity High \
  --description "Scope creep due to stakeholder feature requests during development" \
  --mitigation "Establish change control process, require Product Owner approval for new features, defer non-MVP items to Phase 2"

python main.py raid add --project TODO --type risk --severity High \
  --description "Third-party authentication API (Auth0) downtime or rate limiting" \
  --mitigation "Implement circuit breaker pattern, local fallback auth for testing, monitor API status dashboard"

# Medium-priority risks
python main.py raid add --project TODO --type risk --severity Medium \
  --description "Database performance degradation with > 1000 tasks per user" \
  --mitigation "Implement pagination (20 tasks/page), add database indexes on user_id and created_at, plan load testing in Week 6"

python main.py raid add --project TODO --type risk --severity Medium \
  --description "Team member unavailability (vacation, illness)" \
  --mitigation "Cross-train developers on frontend and backend, maintain up-to-date documentation, pair programming"

# Assumptions
python main.py raid add --project TODO --type assumption --severity Low \
  --description "All team members available full-time for 9-week duration" \
  --mitigation "Confirmed with team leads, backup developers identified"

python main.py raid add --project TODO --type assumption --severity Low \
  --description "Development environment (AWS, Docker) available and stable" \
  --mitigation "Environment provisioned in Week 1, infrastructure-as-code for reproducibility"

# Dependencies
python main.py raid add --project TODO --type dependency --severity Medium \
  --description "Auth0 API integration requires approval and setup (1 week lead time)" \
  --mitigation "Initiated setup in Week 1, use mock auth for parallel development"
```

**Output:**
```
✓ RAID entry added: RAID-001 (Risk)
✓ RAID entry added: RAID-002 (Risk)
✓ RAID entry added: RAID-003 (Risk)
✓ RAID entry added: RAID-004 (Risk)
✓ RAID entry added: RAID-005 (Assumption)
✓ RAID entry added: RAID-006 (Assumption)
✓ RAID entry added: RAID-007 (Dependency)
```

**Verification:**
```bash
python main.py raid list --project TODO
```

### Step 5: Initial Gap Assessment

Run gap assessment to identify missing artifacts for Initiating phase:

```bash
python main.py assess-gaps --project TODO
```

**Expected Output:**
```
=== Gap Assessment: TODO ===

Current State:
  Workflow Phase: Initiating
  Artifacts: 2 (stakeholders.md, charter.md)
  RAID Entries: 7

Recommended Artifacts (Initiating Phase):
  ✓ Project Charter (charter.md) - Present
  ✓ Stakeholder Register (stakeholders.md) - Present
  ⚠ Business Case - Missing
    Suggested: Create business case document with ROI analysis

Next Phase Preparation (Planning):
  ⊙ Work Breakdown Structure - Not yet required
  ⊙ Schedule - Not yet required
  ⊙ Budget Details - Not yet required

ISO 21500 Compliance: 67% (2/3 recommended artifacts)
```

**Decision:** Defer business case to Planning phase (Product Owner will provide ROI data).

### Step 6: Transition to Planning

```bash
python main.py workflow update --project TODO --state Planning
```

**Output:**
```
✓ Proposal created: proposals/workflow-update-20260203-140000.json
  Command: workflow update
  Changes: state (Initiating → Planning)
  
Apply with: python main.py proposals apply --id workflow-update-20260203-140000
Or review in GUI: http://localhost:5173/proposals
```

**Apply proposal:**
```bash
python main.py proposals apply --id workflow-update-20260203-140000
```

**Output:**
```
✓ Proposal applied successfully
  Workflow state: Planning
  Git commit: [TODO] Transition to Planning phase
```

**End of Week 1 - Initiating Phase Complete**

---

## Part 2: Planning (Week 2-3)

### Step 7: Create Work Breakdown Structure (WBS)

```bash
python main.py artifacts create --project TODO \
  --type wbs \
  --title "Work Breakdown Structure" \
  --prompt "Create a detailed WBS for the Todo App MVP. Structure: 1. Project Management (1.1 Planning, 1.2 Monitoring, 1.3 Closing); 2. Requirements (2.1 Gather requirements, 2.2 Create user stories, 2.3 Acceptance criteria); 3. Design (3.1 UI/UX mockups, 3.2 Database schema, 3.3 API design); 4. Development (4.1 Backend API [4.1.1 User auth, 4.1.2 Task CRUD, 4.1.3 Priority/due dates], 4.2 Frontend [4.2.1 Login page, 4.2.2 Task list view, 4.2.3 Task editor], 4.3 Integration); 5. Testing (5.1 Unit tests, 5.2 Integration tests, 5.3 User acceptance testing); 6. Deployment (6.1 CI/CD pipeline, 6.2 Production deployment, 6.3 Monitoring setup). Include work package IDs, descriptions, and estimated hours."
```

**Output:**
```
✓ Artifact created: artifacts/wbs.md
  Generated content: 5.2 KB
```

### Step 8: Create Project Schedule

```bash
python main.py artifacts create --project TODO \
  --type schedule \
  --title "Project Schedule - 9 Week Plan" \
  --prompt "Create a detailed project schedule for the Todo App MVP (9 weeks). Format as a Gantt-style table with columns: Work Package, Duration (days), Start Date, End Date, Dependencies, Assignee. Week 1: Project setup, requirements gathering (Done). Week 2-3: Design phase (UI mockups, database schema, API design). Week 4-5: Backend development (auth, CRUD APIs). Week 5-6: Frontend development (React components). Week 7: Integration and testing. Week 8: UAT and bug fixes. Week 9: Deployment and closure. Mark critical path items. Include milestones: Alpha (end of Week 4), Beta (end of Week 6), Launch (end of Week 9)."
```

**Output:**
```
✓ Artifact created: artifacts/schedule.md
  Generated content: 3.8 KB
```

### Step 9: Define Budget

```bash
python main.py artifacts create --project TODO \
  --type budget \
  --title "Project Budget Breakdown" \
  --prompt "Create a detailed budget for the Todo App MVP ($50,000 total). Breakdown: 1. Labor costs (Team salaries: PM 10%, Dev 50%, QA 20%, Design 15% of project time); 2. Infrastructure (AWS hosting, Auth0 subscription, monitoring tools: $2,000); 3. Software licenses (IDEs, design tools: $1,000); 4. Contingency reserve (10% for risks: $5,000); 5. Training and documentation ($1,000). Present as table with categories, estimated cost, actual cost (TBD), variance. Include cost control measures and approval process for budget changes."
```

**Output:**
```
✓ Artifact created: artifacts/budget.md
  Generated content: 2.9 KB
```

### Step 10: Detailed Risk Analysis

Expand RAID register with detailed analysis:

```bash
# Add specific technical risks
python main.py raid add --project TODO --type risk --severity High \
  --description "React state management complexity with large task lists (>500 items)" \
  --mitigation "Implement Redux with normalized state, use virtualized lists (react-window), add performance monitoring"

python main.py raid add --project TODO --type risk --severity Medium \
  --description "CORS issues when deploying frontend and backend to different domains" \
  --mitigation "Configure CORS headers in FastAPI, test with production-like setup in Week 7"

python main.py raid add --project TODO --type risk --severity Medium \
  --description "Database migration strategy for production data" \
  --mitigation "Use Alembic for migrations, test migration rollback, maintain backup before prod deploy"

# Add project management risks
python main.py raid add --project TODO --type risk --severity Medium \
  --description "Insufficient user feedback during UAT leading to post-launch issues" \
  --mitigation "Recruit 10 beta users in Week 6, structured feedback sessions, prioritize critical feedback"

# Add dependencies
python main.py raid add --project TODO --type dependency --severity High \
  --description "Frontend development blocked until backend APIs are stable (Week 5)" \
  --mitigation "Define API contract in Week 3, use mock server for parallel frontend dev"

python main.py raid add --project TODO --type dependency --severity Medium \
  --description "UAT requires production-like environment (Week 8)" \
  --mitigation "Provision staging environment in Week 6, ensure data parity with production"

# Add issues (planning concerns)
python main.py raid add --project TODO --type issue --severity Medium \
  --description "User story 'bulk task import from CSV' has unclear acceptance criteria" \
  --mitigation "Schedule refinement session with Product Owner in Week 2, defer to Phase 2 if complex"

python main.py raid add --project TODO --type issue --severity Low \
  --description "Team onboarding for new QA engineer (starts Week 4)" \
  --mitigation "Prepare onboarding checklist, assign buddy (Priya Patel), allocate 2 days for ramp-up"
```

**Output:**
```
✓ RAID entries added: RAID-008 through RAID-015
  Total RAID entries: 15
```

### Step 11: Create Detailed Requirements

```bash
python main.py artifacts create --project TODO \
  --type requirements \
  --title "Software Requirements Specification (SRS)" \
  --prompt "Create a comprehensive SRS for the Todo App MVP. Include: 1. Functional Requirements (FR-001: User registration and login with email/password, FR-002: Create task with title/description/priority/due date, FR-003: Edit and delete tasks, FR-004: Mark tasks as complete, FR-005: Filter tasks by status/priority, FR-006: Search tasks by keyword, FR-007: Team sharing - invite members to shared task lists, FR-008: Real-time sync when team members update tasks). 2. Non-Functional Requirements (NFR-001: Response time <500ms for API calls, NFR-002: Support 100 concurrent users, NFR-003: 99.5% uptime, NFR-004: WCAG 2.1 AA accessibility, NFR-005: GDPR compliance for user data). 3. User Interface Requirements (Mobile-responsive, modern design, intuitive navigation). 4. Data Requirements (Task data retention: 2 years, backups: daily). 5. Security Requirements (HTTPS only, password hashing, SQL injection prevention, XSS protection). Include requirement IDs, priority (Must/Should/Could), and acceptance criteria."
```

**Output:**
```
✓ Artifact created: artifacts/requirements.md
  Generated content: 6.7 KB
```

### Step 12: Gap Assessment (Planning Phase)

```bash
python main.py assess-gaps --project TODO
```

**Expected Output:**
```
=== Gap Assessment: TODO ===

Current State:
  Workflow Phase: Planning
  Artifacts: 6 (stakeholders, charter, wbs, schedule, budget, requirements)
  RAID Entries: 15

Recommended Artifacts (Planning Phase):
  ✓ WBS (wbs.md) - Present
  ✓ Schedule (schedule.md) - Present
  ✓ Budget (budget.md) - Present
  ✓ Requirements (requirements.md) - Present
  ⚠ Test Plan - Missing
    Suggested: Create test plan with test cases and coverage targets
  ⚠ Risk Management Plan - Missing (RAID register present but no formal plan)
    Suggested: Document risk response strategies and review cadence

ISO 21500 Compliance: 80% (4/5 core artifacts)

Next Phase Readiness (Executing):
  ⊙ Development environment setup - Required before Week 4
  ⊙ API design document - Recommended
```

**Action Items:**
```bash
# Create test plan
python main.py artifacts create --project TODO \
  --type test-plan \
  --title "Test Plan and Strategy" \
  --prompt "Create a test plan for the Todo App MVP. Include: 1. Test Strategy (unit tests for all business logic, integration tests for API endpoints, E2E tests for critical user flows, UAT with 10 beta users). 2. Test Cases (TC-001: User registration success, TC-002: User login with invalid credentials, TC-003: Create task with all fields, TC-004: Edit task and verify updates, TC-005: Delete task and verify removal, TC-006: Filter tasks by priority, TC-007: Team member can see shared tasks, TC-008: Real-time sync when task updated). 3. Coverage Targets (Unit: 80%, Integration: 70%, E2E: 90% of critical paths). 4. Test Environment (Staging environment, test data generation scripts). 5. Defect Management (JIRA for bug tracking, severity levels, fix prioritization). 6. UAT Plan (Week 8, 10 users, feedback forms, acceptance criteria sign-off)."
```

**Output:**
```
✓ Artifact created: artifacts/test-plan.md
  Generated content: 4.5 KB
```

### Step 13: Transition to Executing

```bash
python main.py workflow update --project TODO --state Executing
python main.py proposals list --project TODO | grep workflow-update | tail -1
# Get proposal ID from output
python main.py proposals apply --id <proposal-id>
```

**Output:**
```
✓ Workflow state: Executing
  Git commit: [TODO] Transition to Executing phase - development begins Week 4
```

**End of Week 3 - Planning Phase Complete**

---

## Part 3: Executing (Week 4-8)

### Step 14: Development Artifacts (Week 4-5)

Simulate development activity by creating code artifacts:

```bash
# Backend API design
python main.py artifacts create --project TODO \
  --type design \
  --title "Backend API Design Document" \
  --prompt "Create API design document for Todo App backend. Include: 1. Technology Stack (FastAPI, PostgreSQL, SQLAlchemy ORM, Auth0 for authentication). 2. API Endpoints (POST /api/auth/register, POST /api/auth/login, GET /api/tasks, POST /api/tasks, PUT /api/tasks/{id}, DELETE /api/tasks/{id}, GET /api/tasks/{id}, POST /api/teams/{id}/invite). 3. Data Models (User: id, email, hashed_password, created_at; Task: id, title, description, priority, due_date, status, user_id, team_id; Team: id, name, owner_id). 4. Request/Response Examples (JSON schemas). 5. Error Handling (4xx for client errors, 5xx for server errors, structured error responses). 6. Authentication Flow (JWT tokens, refresh tokens, token expiry 24h). 7. Database Schema (tables, indexes, foreign keys)."

# Frontend architecture
python main.py artifacts create --project TODO \
  --type design \
  --title "Frontend Architecture Design" \
  --prompt "Create frontend architecture document for Todo App. Include: 1. Technology Stack (React 18, Redux Toolkit for state management, React Router v6, Axios for API calls, Material-UI components). 2. Component Hierarchy (App > Router > Layout > [Dashboard, TaskList, TaskEditor, TeamManager, Settings], shared components: Header, Sidebar, TaskCard). 3. State Management (Redux slices: authSlice, tasksSlice, teamsSlice; async thunks for API calls; normalized state shape). 4. Routing (/login, /register, /dashboard, /tasks, /tasks/:id, /teams). 5. API Integration (axios instance with interceptors, token refresh logic, error handling). 6. Build and Deploy (Vite for bundling, env variables for API URL, production build optimization)."

# Database schema
python main.py artifacts create --project TODO \
  --type design \
  --title "Database Schema Design" \
  --prompt "Create database schema design for Todo App. Include: 1. ERD (Entity Relationship Diagram in ASCII or Mermaid syntax). 2. Tables (users, tasks, teams, team_members junction table). 3. Columns with data types (PostgreSQL types). 4. Indexes (user_id, team_id, created_at for performance). 5. Foreign Keys (tasks.user_id → users.id, tasks.team_id → teams.id). 6. Migration Strategy (Alembic, versioned migrations, rollback plan). 7. Sample Queries (fetch user's tasks, fetch team's tasks, filter by priority, search by keyword). 8. Data Retention (soft deletes with deleted_at timestamp, archival after 2 years)."
```

**Output:**
```
✓ Artifact created: artifacts/api-design.md (5.1 KB)
✓ Artifact created: artifacts/frontend-architecture.md (4.8 KB)
✓ Artifact created: artifacts/database-schema.md (3.9 KB)
```

### Step 15: Track Development Progress (Week 5-6)

Add issues encountered during development:

```bash
# Week 5 issues
python main.py raid add --project TODO --type issue --severity High \
  --description "Auth0 token refresh failing intermittently in frontend (10% of requests)" \
  --mitigation "Debugging in progress, added retry logic, escalated to Auth0 support"

python main.py raid add --project TODO --type issue --severity Medium \
  --description "Task list renders slowly with >200 tasks (500ms delay)" \
  --mitigation "Implementing virtualized list with react-window, target <100ms render time"

# Week 6 issues
python main.py raid add --project TODO --type issue --severity Medium \
  --description "Team invite email delivery delayed (2-5 minutes)" \
  --mitigation "Switched from SendGrid to AWS SES, monitoring delivery times"

python main.py raid add --project TODO --type issue --severity Low \
  --description "Unit test coverage at 72% (target 80%)" \
  --mitigation "Adding tests for edge cases, prioritizing critical paths"
```

### Step 16: Integration Testing (Week 7)

```bash
# Create integration test report
python main.py artifacts create --project TODO \
  --type test-results \
  --title "Integration Test Results - Week 7" \
  --prompt "Create integration test results report. Include: 1. Test Summary (Total tests: 45, Passed: 42, Failed: 3, Coverage: 78%). 2. Failing Tests (Test: 'Team member receives real-time task update', Reason: WebSocket connection drops after 5 minutes, Status: Investigating; Test: 'Bulk task import from CSV', Reason: Memory error with >1000 rows, Status: Deferred to Phase 2; Test: 'Search with special characters', Reason: SQL injection prevention too aggressive, Status: Fixed in commit abc123). 3. Performance Benchmarks (API response times: median 120ms, p95 380ms, p99 620ms; Frontend render: median 80ms, p95 250ms). 4. Recommendations (Fix WebSocket stability before UAT, optimize CSV import for Phase 2, retest search with fix)."
```

### Step 17: User Acceptance Testing (Week 8)

```bash
# Create UAT plan
python main.py artifacts create --project TODO \
  --type uat-plan \
  --title "User Acceptance Testing Plan - Week 8" \
  --prompt "Create UAT plan for Todo App MVP. Include: 1. Participants (10 beta users: 5 team managers, 5 individual users, mix of tech-savvy and non-technical). 2. Test Scenarios (Scenario 1: New user registration and first task creation, Scenario 2: Team collaboration - invite member, share tasks, real-time updates, Scenario 3: Task management - create, edit, delete, filter, search, Scenario 4: Mobile responsiveness - test on phone and tablet). 3. Success Criteria (90% of scenarios completed without assistance, user satisfaction >4.0/5.0, <5 critical bugs, <10 medium bugs). 4. Feedback Collection (Post-test survey, recorded sessions, bug reports in JIRA). 5. Schedule (Monday: Setup and onboarding, Tuesday-Thursday: Testing sessions, Friday: Analysis and prioritization). 6. Contingency (If >5 critical bugs, delay launch by 1 week for fixes)."

# Simulate UAT results
python main.py artifacts create --project TODO \
  --type uat-results \
  --title "UAT Results Summary - Week 8" \
  --prompt "Create UAT results summary. Include: 1. Participation (10/10 users completed testing, 8 hours total testing time). 2. Scenario Results (Scenario 1: 100% completion, Scenario 2: 90% completion [1 user couldn't invite team member due to email issue], Scenario 3: 95% completion, Scenario 4: 85% completion [some UI elements not responsive on small phones]). 3. User Satisfaction (Average rating: 4.2/5.0, Positive feedback: intuitive UI, fast performance, clean design; Negative feedback: mobile UI needs work, missing bulk operations, unclear error messages). 4. Bugs Found (3 critical: email invite fails for Gmail addresses with '+' symbol, task deletion doesn't prompt confirmation, logout doesn't clear cached data; 7 medium bugs; 12 low priority). 5. Recommendations (Fix 3 critical bugs before launch, defer medium/low bugs to Phase 2, improve mobile UI in next sprint)."
```

**Output:**
```
✓ Artifacts created for Week 7-8 testing
```

### Step 18: Bug Fixes and Refinement (Late Week 8)

```bash
# Track critical bug fixes
python main.py raid add --project TODO --type issue --severity Critical \
  --description "Email invite fails for Gmail addresses with '+' symbol (e.g., user+test@gmail.com)" \
  --mitigation "Fixed email validation regex, deployed hotfix, retested successfully"

python main.py raid update --project TODO --id RAID-<issue-id> --status Resolved

python main.py raid add --project TODO --type issue --severity Critical \
  --description "Task deletion doesn't prompt confirmation, users accidentally delete tasks" \
  --mitigation "Added confirmation dialog, added undo feature (30s window), deployed to staging"

python main.py raid update --project TODO --id <issue-id> --status Resolved

python main.py raid add --project TODO --type issue --severity Critical \
  --description "Logout doesn't clear cached data, next user sees previous user's tasks briefly" \
  --mitigation "Clear Redux store on logout, clear localStorage, added E2E test, deployed"

python main.py raid update --project TODO --id <issue-id> --status Resolved
```

**End of Week 8 - Executing Phase Complete**

---

## Part 4: Monitoring & Controlling (Continuous)

### Step 19: Weekly Gap Assessments

Run gap assessment weekly to identify missing work:

```bash
# Week 4 gap assessment
python main.py assess-gaps --project TODO
```

**Example Output (Week 4):**
```
=== Gap Assessment: TODO ===

Current State:
  Workflow Phase: Executing
  Artifacts: 9
  RAID Entries: 19 (3 critical issues open)

Gaps Identified:
  ⚠ No code artifacts yet (expected backend code by Week 5)
  ⚠ Test coverage report missing (required for quality gates)
  ⊙ Deployment plan not yet created (needed for Week 9)

Recommendations:
  → Create backend code structure artifact
  → Run test coverage analysis and document results
  → Begin drafting deployment runbook
```

### Step 20: Weekly Status Reports

Generate weekly status reports:

```bash
# Week 5 status report
python main.py artifacts create --project TODO \
  --type status-report \
  --title "Weekly Status Report - Week 5" \
  --prompt "Create weekly status report. Include: 1. Progress Summary (Backend API 80% complete, Frontend 60% complete, Testing 40% complete). 2. Completed This Week (User auth API, Task CRUD endpoints, Database schema finalized, Frontend login/register pages). 3. Planned Next Week (Team collaboration APIs, Task list frontend, Integration testing setup). 4. Blockers (Auth0 token refresh issue - escalated to support, ETA 2 days). 5. RAID Updates (1 new risk added, 2 issues resolved, 1 issue escalated to critical). 6. Budget Status (Spent: $28,000 / $50,000, On track). 7. Schedule Status (On schedule, Alpha milestone achieved end of Week 4). 8. Risks Requiring Attention (WebSocket stability issue may delay real-time features)."
```

Repeat for weeks 6, 7, 8.

### Step 21: Milestone Reviews

Document milestone achievements:

```bash
# Alpha milestone (Week 4)
python main.py artifacts create --project TODO \
  --type milestone-review \
  --title "Alpha Milestone Review - Week 4" \
  --prompt "Document Alpha milestone review. Include: 1. Milestone Criteria (Backend APIs functional, Database operational, Frontend can login and create tasks, Basic integration working). 2. Achievement Status (All criteria met, demo successful to stakeholders). 3. Stakeholder Feedback (Positive response to UI design, request for dark mode [deferred to Phase 2], concern about mobile UI [addressed in Beta]). 4. Lessons Learned (API contract definition upfront prevented integration issues, mock server enabled parallel frontend dev). 5. Next Milestone (Beta - Week 6): Full feature set, ready for UAT."

# Beta milestone (Week 6)
python main.py artifacts create --project TODO \
  --type milestone-review \
  --title "Beta Milestone Review - Week 6" \
  --prompt "Document Beta milestone review. Include: 1. Milestone Criteria (All MVP features implemented, Integration tests passing, Ready for UAT). 2. Achievement Status (Features complete, 3 known issues, UAT scheduled for Week 8). 3. Stakeholder Feedback (Impressed with performance, team collaboration works well, minor UI polish needed). 4. Lessons Learned (Early UAT user recruitment prevented last-minute scramble, staging environment critical for realistic testing). 5. Next Milestone (Launch - Week 9): Production deployment, all critical bugs fixed."
```

---

## Part 5: Closing (Week 9)

### Step 22: Deployment to Production

```bash
# Create deployment runbook
python main.py artifacts create --project TODO \
  --type deployment \
  --title "Production Deployment Runbook" \
  --prompt "Create production deployment runbook. Include: 1. Pre-Deployment Checklist (All tests passing, critical bugs fixed, UAT sign-off received, staging validated, database backup completed, rollback plan ready). 2. Deployment Steps (Step 1: Database migration [Alembic], Step 2: Backend deployment [Docker to AWS ECS], Step 3: Frontend deployment [S3 + CloudFront], Step 4: Verify health endpoints, Step 5: Smoke tests [login, create task, invite team member], Step 6: Monitor logs for 2 hours). 3. Rollback Plan (If critical issue, rollback database migration, redeploy previous backend version, revert frontend to previous S3 version, ETA 15 minutes). 4. Post-Deployment (Send launch announcement, update documentation, monitor user feedback). 5. On-Call Rotation (Week 9: dev team on-call 24/7, escalation to CTO if needed)."

# Document deployment execution
python main.py artifacts create --project TODO \
  --type deployment-log \
  --title "Production Deployment Log - Week 9" \
  --prompt "Document production deployment execution. Include: 1. Deployment Date/Time (Monday, Week 9, 6:00 AM EST). 2. Team Members Present (Mike Johnson [Dev Lead], Priya Patel [QA], Sarah Chen [Product Owner]). 3. Execution Log (06:00: Database backup completed [15 minutes], 06:15: Database migration applied [8 minutes], 06:23: Backend deployed [12 minutes], 06:35: Frontend deployed [5 minutes], 06:40: Health checks passed, 06:45: Smoke tests executed - all passed, 07:00: Monitoring established). 4. Issues Encountered (Minor: CloudFront cache invalidation took 10 minutes longer than expected [no user impact]). 5. Rollback Triggers (None triggered). 6. Status (Deployment successful, system operational, no critical issues). 7. Post-Deployment Monitoring (First 2 hours: 15 active users, 0 errors, avg response time 110ms)."
```

### Step 23: Lessons Learned

```bash
python main.py artifacts create --project TODO \
  --type lessons-learned \
  --title "Project Retrospective - Lessons Learned" \
  --prompt "Create comprehensive lessons learned document. Include: 1. What Went Well (API-first design enabled parallel dev, automated testing caught bugs early, weekly gap assessments kept project on track, stakeholder communication was clear and frequent, team collaboration excellent, on-time delivery with no scope creep). 2. What Didn't Go Well (Auth0 integration took longer than expected [1 week delay absorbed by contingency], mobile UI polish needed more time [some compromises made], test coverage target of 80% not fully achieved [reached 76%]). 3. What We Learned (Mock API server is critical for frontend independence, early UAT user recruitment prevents delays, virtualized lists are essential for performance with large datasets, JWT token refresh requires robust error handling, database indexes must be planned upfront not added later). 4. Recommendations for Future Projects (Allocate 2 weeks buffer for third-party integrations, include mobile-first design from start, aim for 85% test coverage target to have buffer, provision staging environment in Week 1 not Week 6, conduct mini-retrospectives every 2 weeks not just at end). 5. Quantitative Results (Delivered 92% of planned user stories, 3 critical bugs found in UAT [all fixed], user satisfaction 4.2/5.0 [exceeded 4.0 target], budget used $48,500 / $50,000 [97%], launched on schedule [Week 9])."
```

### Step 24: Final RAID Register Review

Review and close all RAID entries:

```bash
python main.py raid list --project TODO --filter status=Open
```

**Review each open item:**
- Risks: Have they been mitigated or did they not materialize?
- Issues: Have they been resolved or deferred to Phase 2?
- Assumptions: Were they validated?
- Dependencies: Were they fulfilled?

Update statuses:

```bash
# Example: Close mitigated risks
python main.py raid update --project TODO --id RAID-001 --status Mitigated \
  --notes "Change control process successfully prevented scope creep"

python main.py raid update --project TODO --id RAID-002 --status Mitigated \
  --notes "Circuit breaker pattern implemented, no Auth0 downtime encountered"

# Example: Close resolved issues
python main.py raid update --project TODO --id <issue-id> --status Resolved \
  --notes "All critical UAT bugs fixed and deployed to production"

# Example: Defer Phase 2 items
python main.py raid add --project TODO --type issue --severity Low \
  --description "Bulk task import from CSV deferred to Phase 2" \
  --mitigation "User feedback indicates nice-to-have, not critical for launch"
```

### Step 25: Archive Project Artifacts

```bash
# Create archive package
python main.py artifacts create --project TODO \
  --type archive-manifest \
  --title "Project Archive Manifest" \
  --prompt "Create project archive manifest. Include: 1. Archived Artifacts (List all 18 artifacts with descriptions: charter, requirements, wbs, schedule, budget, test plan, api design, frontend architecture, database schema, test results, uat plan, uat results, status reports [weeks 5-8], milestone reviews [alpha, beta], deployment runbook, deployment log, lessons learned). 2. Git Repository (Location: projectDocs/TODO/, Commits: 87, Branches: main [production], develop [archived]). 3. RAID Register Final State (Total entries: 24, Risks: 8 [6 mitigated, 2 did not materialize], Issues: 12 [11 resolved, 1 deferred], Assumptions: 2 [both validated], Dependencies: 2 [both fulfilled]). 4. Handover Documentation (Production credentials [in secure vault], monitoring dashboards [Grafana URLs], on-call rotation, support process). 5. Retention Policy (Archive retained for 2 years, then deleted per data policy). 6. Access (Product Owner [read/write], Dev Team [read-only], archived team members [no access])."

# Export artifacts for archival
cd projectDocs/TODO
git tag -a v1.0-launch -m "Todo App MVP Launch - Week 9"
git archive --format=zip --output=../../TODO-archive-v1.0.zip HEAD
```

### Step 26: Project Closure

```bash
python main.py workflow update --project TODO --state Closing
python main.py proposals apply --id <proposal-id>
```

**Output:**
```
✓ Workflow state: Closing
  Project successfully completed
  Git commit: [TODO] Project closed - MVP launched successfully
```

### Step 27: Final Project Summary

```bash
python main.py artifacts create --project TODO \
  --type project-summary \
  --title "Todo App MVP - Final Project Summary" \
  --prompt "Create final project summary. Include: 1. Executive Summary (Todo App MVP successfully launched on schedule in Week 9. All critical features delivered, exceeded user satisfaction target [4.2/5.0], within budget [$48,500 / $50,000]). 2. Objectives Achieved (✓ 90%+ user stories completed [92%], ✓ <5 critical bugs in production [3 found, all fixed], ✓ User satisfaction >4.0 [achieved 4.2], ✓ On-time launch [Week 9]). 3. Key Metrics (Timeline: 9 weeks planned, 9 weeks actual; Budget: $50k planned, $48.5k actual; Scope: 25 user stories planned, 23 delivered, 2 deferred to Phase 2; Quality: 76% test coverage, 3 critical bugs [all fixed], 19 total bugs). 4. Deliverables (Fully functional web application, comprehensive documentation [18 artifacts], trained support team, production infrastructure). 5. Stakeholder Satisfaction (Product Owner [Sarah Chen]: Very satisfied, CTO [David Liu]: Approved for Phase 2 funding, End Users: Positive feedback, requesting additional features). 6. Lessons Applied (API-first design, automated testing, continuous integration, weekly gap assessments). 7. Next Steps (Phase 2 planning begins Week 10, focus on mobile app and advanced features, maintain Phase 1 in production with support)."
```

**End of Week 9 - Closing Phase Complete**

---

## Part 6: Retrospective Analysis

### Step 28: ISO 21500 Compliance Review

Review how the framework supported the project:

```bash
python main.py assess-gaps --project TODO --detailed
```

**Expected Output:**
```
=== Detailed Gap Assessment: TODO ===

ISO 21500 Compliance by Process Group:

Initiating (100%):
  ✓ Project Charter
  ✓ Stakeholder Register
  ✓ Initial RAID

Planning (100%):
  ✓ WBS
  ✓ Schedule
  ✓ Budget
  ✓ Requirements
  ✓ Test Plan
  ✓ RAID expanded

Executing (95%):
  ✓ Design documents
  ✓ Development artifacts
  ✓ Test results
  ⚠ Code repository links (could be added)

Monitoring (100%):
  ✓ Weekly status reports
  ✓ Milestone reviews
  ✓ Gap assessments
  ✓ RAID updates

Closing (100%):
  ✓ Lessons learned
  ✓ Deployment documentation
  ✓ Archive manifest
  ✓ Project summary

Overall ISO 21500 Compliance: 98%
```

### Step 29: Workflow State History

Review all workflow transitions:

```bash
cd projectDocs/TODO
git log --all --grep="Workflow" --oneline
```

**Output:**
```
a1b2c3d [TODO] Project closed - MVP launched successfully
e4f5g6h [TODO] Transition to Closing phase
i7j8k9l [TODO] Transition to Executing phase - development begins Week 4
m0n1o2p [TODO] Transition to Planning phase
```

### Step 30: Final Verification

Verify all project artifacts are present and complete:

```bash
cd apps/tui
python main.py projects show --project TODO
```

**Output:**
```
Project: TODO (Todo App MVP)

Status:
  Workflow State: Closing
  Created: Week 1, Day 1
  Closed: Week 9, Day 5
  Duration: 9 weeks

Artifacts (19):
  ✓ charter.md
  ✓ stakeholders.md
  ✓ wbs.md
  ✓ schedule.md
  ✓ budget.md
  ✓ requirements.md
  ✓ test-plan.md
  ✓ api-design.md
  ✓ frontend-architecture.md
  ✓ database-schema.md
  ✓ test-results.md
  ✓ uat-plan.md
  ✓ uat-results.md
  ✓ status-report-week-5.md
  ✓ milestone-review-alpha.md
  ✓ milestone-review-beta.md
  ✓ deployment.md
  ✓ deployment-log.md
  ✓ lessons-learned.md
  ✓ project-summary.md

RAID Register (24 entries):
  Risks: 8 (6 mitigated, 2 did not materialize)
  Issues: 12 (11 resolved, 1 deferred)
  Assumptions: 2 (validated)
  Dependencies: 2 (fulfilled)

Git Commits: 87
Git Tags: v1.0-launch
```

---

## Key Takeaways

### ISO 21500 Process Groups in Practice

**1. Initiating:**
- Focus: Define project, identify stakeholders, establish charter
- Framework Support: Project creation, RAID register initialization, charter generation
- Duration: ~1 week for typical projects

**2. Planning:**
- Focus: Detailed WBS, schedule, budget, risk analysis
- Framework Support: WBS artifacts, gap assessment identifies missing plans
- Duration: ~2 weeks for comprehensive planning

**3. Executing:**
- Focus: Develop deliverables, manage team, create artifacts
- Framework Support: Artifact generation, code documentation, continuous RAID updates
- Duration: ~5 weeks for MVP development

**4. Monitoring & Controlling:**
- Focus: Track progress, assess gaps, resolve issues
- Framework Support: Gap assessments, RAID tracking, status reports
- Duration: Continuous throughout project

**5. Closing:**
- Focus: Lessons learned, archival, handover
- Framework Support: Retrospective generation, archive manifest, final summary
- Duration: ~1 week for formal closure

### Framework Features That Supported Success

1. **Gap Assessment:** Weekly `assess-gaps` runs kept project on track
2. **RAID Register:** Central repository for risks, issues, assumptions, dependencies
3. **Proposal System:** Change control mechanism prevented scope creep
4. **Git-based Versioning:** All artifacts versioned and auditable
5. **LLM Generation:** Accelerated artifact creation (charters, requirements, designs)
6. **Workflow States:** Clear phase transitions with automated validation

### Best Practices Demonstrated

1. **Comprehensive Planning:** Invest 2-3 weeks in planning for 9-week projects
2. **Continuous Monitoring:** Run gap assessments weekly, not just at milestones
3. **RAID Discipline:** Update RAID register daily, review weekly
4. **Artifact-Driven:** Document everything (18+ artifacts for this project)
5. **Iterative Refinement:** Use proposals for all state changes (change control)
6. **Lessons Learned:** Capture learnings immediately, not just at project end

### Metrics to Track

- **Timeline Adherence:** Planned vs. actual duration per phase
- **Scope Delivered:** User stories completed vs. planned
- **Quality:** Test coverage, bug counts, user satisfaction
- **Budget:** Actual vs. planned spend per phase
- **RAID Efficiency:** Time to resolve issues, risk mitigation success rate
- **ISO 21500 Compliance:** Percentage of recommended artifacts created

## Next Steps

- **Adapt for Your Project:** Adjust timeline and artifacts for your scope
- **Automate Reporting:** Use TUI scripting to generate weekly reports
- **Integrate Tools:** Connect JIRA, GitHub, CI/CD to framework
- **Phase 2:** Apply learnings to next project iteration

## Additional Resources

- [ISO 21500 Official Standard](https://www.iso.org/standard/50003.html)
- [TUI Automation Tutorial](../advanced/03-automation-scripting.md)
- [RAID Register Best Practices](../../raid_register.md)
- [Gap Assessment Guide](../../docs/api/gap-assessment.md)
