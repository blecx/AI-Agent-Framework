# Step 2: Complete Requirements Specification

## Executive Summary

**Step 2 Goal:** Deliver template-driven project artifact management with proposal-based change control and audit tracking.

**What Step 2 adds to Step 1:** Template system, artifact generation, visual artifact editor, proposal workflow (propose → review → apply/reject), and end-to-end validation.

**Success criteria:** Users can generate project artifacts (PMP, RAID, etc.) from templates, edit them through forms, propose changes, review diffs, and apply/reject proposals with full audit trail.

## Context: How Step 2 Relates to Master Plan

### Original Master Plan Structure

The master plan in `usedChats/master_plan_for_solution_merged.md` defined a "Step 1 thin slice" that included:

1. **Phase 1 (Core Platform):** Project creation, document storage (Git), basic commands
2. **Phase 2 (PMP/Templates):** Template system, artifact generation
3. **Phase 3 (Proposals):** Propose/apply pattern with diff visualization
4. **Phase 4 (RAID/Workflow/Audit):** RAID register, workflow engine, audit viewer

### What Was Actually Delivered

**Step 1 (completed):**

- ✅ Core platform (projects, Git storage, REST API, React WebUI)
- ✅ RAID register (full CRUD, filtering, status updates)
- ✅ Workflow engine (state machine, transitions, validation)
- ✅ Audit system (event logging, impact tracking, viewer UI)
- ✅ Domain-Driven Design architecture established

**Step 2 (planned = 18 issues):**

- All remaining "thin slice" capabilities
- Template system (domain models + service + API)
- Blueprint management
- Artifact generation from templates
- Visual artifact editor (WebUI)
- Proposal workflow (create → review → apply/reject)
- End-to-end tests

### Why Step 2 Exists

Step 1 delivered RAID/workflow/audit but **did not include templates or artifact editing**. Users could create projects and log RAID items, but couldn't:

- Generate PMP/SRS/other documents from templates
- Edit artifacts through structured forms
- Propose changes with diff visualization

Step 2 closes this gap, completing the original "thin slice" vision.

---

## Complete Step 2 Requirements (7 Core + 2 Testing)

### R1: Template Management System

**Description:** Backend domain for managing project templates (PMP, SRS, RAID, etc.) with metadata, validation rules, and artifact generation logic.

**Why it matters:** Templates are the **blueprint** for generating project artifacts. Without templates, users must manually create all documents from scratch.

**Must deliver:**

- ✅ Template domain models (`apps/api/domain/templates/`)
- ✅ Template validation (required fields, schema compliance)
- ✅ Template service (CRUD operations, query by type/category)
- ✅ Template REST API (GET, POST, PUT, DELETE endpoints)
- ✅ Support for Jinja2 template rendering

**Acceptance criteria:**

- [ ] Template models defined with Pydantic schemas
- [ ] Templates stored in `projectDocs/templates/` (Git-backed)
- [ ] API supports creating templates via POST /templates
- [ ] API supports listing templates: GET /templates?type=pmp
- [ ] Template validation rejects invalid schemas

**Mapped to issues:**

- BE-01: Template domain models (#69)
- BE-02: Template service (#70)
- BE-03: Template REST API (#71)

**Validation:**

```bash
# Create template
curl -X POST http://localhost:8000/templates \
  -H "Content-Type: application/json" \
  -d '{"name":"ISO21500-PMP","type":"pmp","schema":{...}}'

# List templates
curl http://localhost:8000/templates?type=pmp

# Verify Git commit
cd projectDocs && git log --oneline | grep "Template"
```

---

### R2: Blueprint Management

**Description:** Blueprints are **project-specific instances** of templates with user customizations (e.g., "Acme Corp PMP based on ISO21500-PMP").

**Why it matters:** Templates are generic; blueprints are customized for each project. This separation allows teams to standardize templates while customizing content.

**Must deliver:**

- ✅ Blueprint domain models (extends templates with project context)
- ✅ Blueprint service (create from template, customize fields)
- ✅ Blueprint REST API (GET, POST /blueprints)
- ✅ Link blueprints to projects

**Acceptance criteria:**

- [ ] Blueprint model includes `projectKey`, `templateId`, `customFields`
- [ ] Blueprints stored in `projectDocs/{projectKey}/blueprints/`
- [ ] API supports: POST /projects/{key}/blueprints
- [ ] Blueprints can override template defaults

**Mapped to issues:**

- BE-04: Blueprint domain (complete: models + service + API) (#72)

**Validation:**

```bash
# Create blueprint from template
curl -X POST http://localhost:8000/projects/ACME/blueprints \
  -d '{"templateId":"ISO21500-PMP","customFields":{"projectName":"Acme Corp"}}'

# List blueprints
curl http://localhost:8000/projects/ACME/blueprints
```

---

### R3: Artifact Generation from Templates

**Description:** Generate concrete project artifacts (PMP document, RAID register, etc.) from blueprints by applying template logic and filling in data.

**Why it matters:** This is the **core value** of the template system. Users define templates once, then auto-generate artifacts for every project.

**Must deliver:**

- ✅ Artifact service with `generate_from_template(blueprint_id)` method
- ✅ Jinja2 rendering engine integration
- ✅ Support for multiple output formats (Markdown, JSON)
- ✅ Artifact REST API (POST /artifacts/generate)
- ✅ Artifacts stored in `projectDocs/{projectKey}/artifacts/`

**Acceptance criteria:**

- [ ] Artifact generation uses Jinja2 templates
- [ ] Generated artifacts include metadata (templateId, version, timestamp)
- [ ] API endpoint: POST /projects/{key}/artifacts/generate
- [ ] Artifacts versioned in Git (one commit per generation)

**Mapped to issues:**

- BE-05: Artifact service (#73)
- BE-06: Artifact REST API (#74)

**Validation:**

```bash
# Generate artifact
curl -X POST http://localhost:8000/projects/ACME/artifacts/generate \
  -d '{"blueprintId":"acme-pmp-v1","outputFormat":"markdown"}'

# Verify artifact file created
ls -lh projectDocs/ACME/artifacts/pmp-001.md

# Check Git history
cd projectDocs/ACME && git log --oneline | grep "Generated artifact"
```

---

### R4: Proposal Workflow System

**Description:** Proposal-based change control for artifacts. Users **propose** changes (edit artifact), system generates **diff**, then changes are **applied** (committed to Git) or **rejected**.

**Why it matters:** Prevents direct editing of artifacts. All changes go through review process, ensuring traceability and approval gates.

**Must deliver:**

- ✅ Proposal domain models (status: pending/approved/rejected/applied)
- ✅ Diff generation (Git-based or text-based diff)
- ✅ Proposal service (create, review, apply, reject)
- ✅ Proposal REST API (POST, GET, PATCH endpoints)
- ✅ Integration with audit system (log all proposal actions)

**Acceptance criteria:**

- [ ] Proposal model includes: `title`, `artifactId`, `diff`, `status`, `author`, `reviewedBy`
- [ ] Proposals stored in `projectDocs/{projectKey}/proposals/`
- [ ] API supports full CRUD: POST, GET, PATCH /proposals
- [ ] Applying proposal commits changes to artifact + logs audit event
- [ ] Rejecting proposal updates status without changing artifact

**Mapped to issues:**

- BE-07: Proposal domain models (#75)
- BE-08: Proposal service (#76)
- BE-09: Proposal REST API (#77)

**Validation:**

```bash
# Create proposal
curl -X POST http://localhost:8000/projects/ACME/proposals \
  -d '{"title":"Update PMP scope","artifactId":"pmp-001","diff":"..."}'

# List proposals
curl http://localhost:8000/projects/ACME/proposals

# Apply proposal
curl -X PATCH http://localhost:8000/proposals/123 \
  -d '{"action":"apply"}'

# Verify artifact changed
cat projectDocs/ACME/artifacts/pmp-001.md | grep "Updated scope"

# Check audit log
curl http://localhost:8000/projects/ACME/audit | grep "Proposal applied"
```

---

### R5: Visual Artifact Editor (WebUI)

**Description:** React component for **editing artifacts** through template-driven forms. Shows structured fields (not raw Markdown), validates input, submits as proposal.

**Why it matters:** Users expect modern web forms, not raw file editing. Editor provides **structure** and **validation** based on template schema.

**Must deliver:**

- ✅ ArtifactEditor React component
- ✅ ArtifactsList component (browse artifacts by type)
- ✅ Dynamic form generation from template schema
- ✅ Field validation (required fields, data types, regex patterns)
- ✅ Integration with proposal API (submit changes as proposal)

**Acceptance criteria:**

- [ ] Editor component renders artifact fields as form inputs
- [ ] Save button creates proposal (not direct edit)
- [ ] List component shows all artifacts with type filtering
- [ ] Navigation: List → Editor → Proposal created
- [ ] Form validation shows errors inline

**Mapped to issues:**

- UX-01: ArtifactEditor component (#102)
- UX-02: ArtifactsList component (#103)

**Validation:**

```bash
# Manual test (browser)
1. Navigate to http://localhost:5173/projects/ACME/artifacts
2. Click "Edit" on PMP artifact
3. Change field "Project Purpose" → Save
4. Verify proposal created (not direct artifact edit)
5. Check proposals list shows new proposal
```

---

### R6: Proposal Review UI (WebUI)

**Description:** React components for **reviewing proposals** with diff visualization, approval/rejection actions.

**Why it matters:** Review workflow is **mandatory gate** for artifact changes. UI must show what changed, who proposed it, and allow approve/reject.

**Must deliver:**

- ✅ ProposalCreator component (manual proposal creation)
- ✅ ProposalList component (browse all proposals, filter by status)
- ✅ ProposalReviewModal component (show diff, apply/reject buttons)
- ✅ Diff visualization (side-by-side or unified diff)
- ✅ Integration with proposal API

**Acceptance criteria:**

- [ ] ProposalList shows: title, status, author, date
- [ ] Clicking proposal opens ReviewModal with diff
- [ ] Apply button: calls PATCH /proposals/{id} action=apply
- [ ] Reject button: calls PATCH /proposals/{id} action=reject
- [ ] Diff shows before/after or unified diff format

**Mapped to issues:**

- UX-03: ProposalCreator component (#104)
- UX-04: ProposalList component (#105)
- UX-05: ProposalReviewModal component (#106)

**Validation:**

```bash
# Manual test (browser)
1. Navigate to http://localhost:5173/projects/ACME/proposals
2. Click proposal "Update PMP scope"
3. Verify diff shows changes
4. Click "Apply" → Verify success message
5. Navigate to artifacts → Verify artifact updated
```

---

### R7: Audit Viewer Integration

**Description:** Audit UI must show **proposal events** (created, applied, rejected) with filtering and navigation to artifacts.

**Why it matters:** Full traceability requires audit log to show **who changed what and when** for all proposals.

**Must deliver:**

- ✅ AuditViewer component extended with proposal event support
- ✅ AuditBadges component (show severity/impact icons)
- ✅ Filter by event type (proposals only)
- ✅ Click audit event → Navigate to artifact or proposal

**Acceptance criteria:**

- [ ] Audit log shows proposal events: "Proposal #123 applied by user@example.com"
- [ ] Filter dropdown includes "Proposals" option
- [ ] Clicking event navigates to relevant artifact or proposal
- [ ] Badge shows proposal status (pending=yellow, applied=green, rejected=red)

**Mapped to issues:**

- UX-06: AuditViewer enhancements (#107)
- UX-07: AuditBadges component (#108)

**Validation:**

```bash
# Manual test (browser)
1. Navigate to http://localhost:5173/projects/ACME/audit
2. Filter by "Proposals"
3. Verify proposal events shown
4. Click event → Verify navigates to artifact editor
```

---

### R8: Backend End-to-End Tests

**Description:** pytest-based E2E test suite validating **complete Step 2 workflow** from template creation to proposal application.

**Why it matters:** Unit tests validate individual components, but E2E tests ensure the **entire system works together**. This is the final gate for Step 2.

**Must deliver:**

- ✅ E2E test suite (`tests/e2e/test_step2_workflow.py`)
- ✅ 7+ test scenarios covering full workflow
- ✅ Test fixtures (templates, blueprints, artifacts)
- ✅ Assertions on both API responses AND Git commits
- ✅ Tests run in CI (automated)

**Acceptance criteria:**

- [ ] Test 1: Template CRUD (create, list, update, delete)
- [ ] Test 2: Blueprint creation from template
- [ ] Test 3: Artifact generation from blueprint
- [ ] Test 4: Proposal creation for artifact edit
- [ ] Test 5: Proposal apply (changes artifact + Git commit)
- [ ] Test 6: Proposal reject (no artifact change)
- [ ] Test 7: Audit events logged for all actions
- [ ] All tests pass in CI (`pytest tests/e2e/`)
- [ ] Test execution time < 60 seconds

**Mapped to issues:**

- BE-10: Backend E2E tests (#78)

**Validation:**

```bash
# Run E2E tests
pytest tests/e2e/test_step2_workflow.py -v

# Expected output:
# test_template_crud PASSED
# test_blueprint_creation PASSED
# test_artifact_generation PASSED
# test_proposal_workflow PASSED
# test_audit_logging PASSED
# ==================== 7 passed in 45.2s ====================
```

---

### R9: Client End-to-End Tests

**Description:** Playwright-based E2E test suite validating **complete Step 2 UI workflow** with real browser automation.

**Why it matters:** Backend tests validate APIs, but client tests ensure **UI components integrate correctly** and users can actually complete workflows.

**Must deliver:**

- ✅ E2E test suite (`client/e2e/step2-workflow.spec.ts`)
- ✅ 7+ test scenarios using Playwright
- ✅ Page object models for all Step 2 components
- ✅ Tests validate UI state AND backend state (via API)
- ✅ Tests run in CI (headless Chrome)

**Acceptance criteria:**

- [ ] Test 1: Artifact editor workflow (navigate → edit → save → verify)
- [ ] Test 2: Artifact list filtering
- [ ] Test 3: Proposal creation via UI
- [ ] Test 4: Proposal apply workflow (list → review → apply → verify artifact)
- [ ] Test 5: Proposal reject workflow
- [ ] Test 6: Audit viewer with proposal events
- [ ] Test 7: Full end-to-end workflow (all steps integrated)
- [ ] All tests pass in CI (`npm run test:e2e`)
- [ ] Test execution time < 90 seconds
- [ ] No flaky tests (deterministic)

**Mapped to issues:**

- UX-08: Client E2E tests (#109)

**Validation:**

```bash
# Run client E2E tests
cd _external/AI-Agent-Framework-Client
npm run test:e2e

# Expected output:
# ✓ Step 2 Full Workflow > complete artifact → proposal → apply workflow (12.3s)
# ✓ Step 2 Full Workflow > artifact list filtering (3.1s)
# ✓ Step 2 Full Workflow > proposal reject workflow (4.2s)
# ...
# 7 passed (89.2s)
```

---

## Requirements Traceability Matrix

| Requirement              | Issues           | Backend Files                                                                  | Frontend Files                                                                                | Tests                                                                          |
| ------------------------ | ---------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| R1: Template Management  | #69, #70, #71    | `domain/templates/`, `services/template_service.py`, `routers/templates.py`    | N/A                                                                                           | `tests/unit/test_template_models.py`, `tests/integration/test_template_api.py` |
| R2: Blueprint Management | #72              | `domain/blueprints/`, `services/blueprint_service.py`, `routers/blueprints.py` | N/A                                                                                           | `tests/integration/test_blueprint_api.py`                                      |
| R3: Artifact Generation  | #73, #74         | `services/artifact_service.py`, `routers/artifacts.py`                         | N/A                                                                                           | `tests/integration/test_artifact_generation.py`                                |
| R4: Proposal Workflow    | #75, #76, #77    | `domain/proposals/`, `services/proposal_service.py`, `routers/proposals.py`    | N/A                                                                                           | `tests/integration/test_proposal_workflow.py`                                  |
| R5: Artifact Editor UI   | #102, #103       | N/A                                                                            | `src/components/artifacts/ArtifactEditor.tsx`, `ArtifactsList.tsx`                            | `client/src/tests/artifacts/*.test.tsx`                                        |
| R6: Proposal Review UI   | #104, #105, #106 | N/A                                                                            | `src/components/proposals/ProposalCreator.tsx`, `ProposalList.tsx`, `ProposalReviewModal.tsx` | `client/src/tests/proposals/*.test.tsx`                                        |
| R7: Audit Viewer         | #107, #108       | N/A                                                                            | `src/components/audit/AuditViewer.tsx`, `AuditBadges.tsx`                                     | `client/src/tests/audit/*.test.tsx`                                            |
| R8: Backend E2E Tests    | #78              | N/A                                                                            | N/A                                                                                           | `tests/e2e/test_step2_workflow.py`                                             |
| R9: Client E2E Tests     | #109             | N/A                                                                            | N/A                                                                                           | `client/e2e/step2-workflow.spec.ts`                                            |

---

## Implementation Order & Dependencies

### Phase 1: Backend Foundation (Concurrent)

**Duration:** 3 weeks (3 devs working in parallel)

- **Week 1:**
  - Dev A: Templates (#69, #70, #71) - S + M + S = 4 days
  - Dev B: Blueprints (#72) - M = 2 days, then start Artifacts (#73)
  - Dev C: Proposals (#75, #76) - S + M = 3 days

- **Week 2:**
  - Dev A: Review blueprints, start Artifact API (#74)
  - Dev B: Finish Artifacts (#73, #74)
  - Dev C: Finish Proposals (#77) + integration testing

- **Week 3:**
  - All devs: Backend E2E tests (#78) - M = 2 days
  - Code review + bug fixes

**Deliverable:** Fully functional backend APIs for templates, artifacts, proposals.

### Phase 2: Frontend (After Phase 1 APIs complete)

**Duration:** 3 weeks (2 devs)

- **Week 1:**
  - Dev D: ArtifactEditor + ArtifactsList (#102, #103)
  - Dev E: ProposalCreator + ProposalList (#104, #105)

- **Week 2:**
  - Dev D: ProposalReviewModal (#106)
  - Dev E: AuditViewer enhancements (#107, #108)

- **Week 3:**
  - Both devs: Client E2E tests (#109) + bug fixes

**Deliverable:** Complete WebUI for Step 2 workflow.

### Phase 3: Integration & Final Validation

**Duration:** 1 week (all devs)

- E2E test execution (backend + client)
- Cross-browser testing
- Performance validation
- User acceptance testing (UAT)
- Documentation finalization

**Deliverable:** Production-ready Step 2 release.

---

## Success Criteria (Definition of Done)

Step 2 is **COMPLETE** when:

### Functional Criteria

- [ ] All 18 issues closed (#69-#77, #102-#108, #78, #109)
- [ ] All acceptance criteria met (see individual issues)
- [ ] All E2E tests pass (backend + client)
- [ ] No critical bugs in issue tracker

### Quality Criteria

- [ ] Unit test coverage ≥ 80% (backend services + domain models)
- [ ] Integration test coverage ≥ 70% (API endpoints)
- [ ] E2E test coverage: 100% of critical workflows
- [ ] Linting passes (black + flake8 for Python, ESLint for TypeScript)
- [ ] No security vulnerabilities (npm audit, safety check)

### Documentation Criteria

- [ ] API documentation complete (OpenAPI/Swagger)
- [ ] User guide updated (how to use artifact editor, proposals)
- [ ] Developer guide updated (how to add new templates)
- [ ] Architecture diagrams updated (template system, proposal workflow)

### Deployment Criteria

- [ ] Docker compose builds successfully
- [ ] Production deployment scripts tested
- [ ] Environment variables documented
- [ ] Rollback plan documented

---

## Out of Scope for Step 2

These are **NOT required** for Step 2 completion (deferred to Step 3 or later):

### AI/LLM Integration

- **Deferred:** AI-generated artifact content (hook exists in artifact service)
- **Rationale:** Step 2 focuses on template system; AI is enhancement

### Advanced Features

- **Deferred:** Blueprint version management (complex, low priority)
- **Deferred:** Template marketplace (future feature)
- **Deferred:** Multi-user collaboration (concurrent editing)
- **Deferred:** Advanced diff algorithms (Git diff is sufficient)

### TUI Support

- **Deferred:** TUI commands for template management
- **Rationale:** WebUI is primary interface; TUI is convenience feature

### Cross-Artifact Validation

- **Deferred:** Rule-based audit validation (e.g., "PMP must reference all RAID risks")
- **Rationale:** Step 2 delivers event-based audit; rule engine is Step 3/4

### Performance Optimization

- **Deferred:** Artifact caching, lazy loading, pagination
- **Rationale:** Optimize after validating functionality

---

## Questions & Clarifications

### Q1: What is the difference between templates and blueprints?

**A:**

- **Template** = Generic, reusable (e.g., "ISO21500 PMP template")
- **Blueprint** = Project-specific customization (e.g., "Acme Corp PMP based on ISO21500")

Analogy: Template is the cookie cutter, blueprint is the cookie with your toppings.

### Q2: Why proposal workflow instead of direct editing?

**A:** Traceability and approval gates. All artifact changes are:

1. Proposed (with diff)
2. Reviewed (by team/lead)
3. Applied (committed to Git with audit event)

This prevents unauthorized changes and provides full change history.

### Q3: Can users edit artifacts directly without proposals?

**A:** No. In Step 2, ALL artifact edits go through proposal workflow. Direct editing will be added as admin-only feature in Step 3.

### Q4: What happens if proposal is rejected?

**A:** Proposal status changes to "rejected", artifact remains unchanged. Rejection is logged in audit.

### Q5: Do E2E tests replace unit/integration tests?

**A:** No. Testing pyramid applies:

- **Unit tests** (many): Test individual functions/classes
- **Integration tests** (some): Test API endpoints + service interactions
- **E2E tests** (few): Test complete workflows end-to-end

All three are required.

### Q6: Can Step 2 be deployed without Step 1?

**A:** No. Step 2 requires Step 1 infrastructure (project management, Git storage, audit system, workflow engine).

---

## Appendix A: File Structure (After Step 2)

```
AI-Agent-Framework/
├── apps/api/
│   ├── domain/
│   │   ├── templates/         # NEW in Step 2
│   │   │   ├── models.py      # Template entity, schema
│   │   │   └── validators.py  # Template validation rules
│   │   ├── blueprints/        # NEW in Step 2
│   │   │   └── models.py
│   │   ├── proposals/         # NEW in Step 2
│   │   │   └── models.py      # Proposal entity (status, diff)
│   │   ├── projects/          # Step 1
│   │   ├── raid/              # Step 1
│   │   ├── workflow/          # Step 1
│   │   └── audit/             # Step 1
│   ├── services/
│   │   ├── template_service.py   # NEW
│   │   ├── blueprint_service.py  # NEW
│   │   ├── artifact_service.py   # NEW
│   │   ├── proposal_service.py   # NEW
│   │   ├── command_service.py    # Step 1
│   │   ├── git_manager.py        # Step 1
│   │   └── llm_service.py        # Step 1
│   └── routers/
│       ├── templates.py          # NEW
│       ├── blueprints.py         # NEW
│       ├── artifacts.py          # NEW (enhanced)
│       ├── proposals.py          # NEW
│       ├── projects.py           # Step 1
│       ├── raid.py               # Step 1
│       └── audit.py              # Step 1
├── tests/
│   ├── unit/
│   │   ├── test_template_models.py   # NEW
│   │   ├── test_proposal_models.py   # NEW
│   │   └── ...
│   ├── integration/
│   │   ├── test_template_api.py      # NEW
│   │   ├── test_proposal_workflow.py # NEW
│   │   └── ...
│   └── e2e/
│       └── test_step2_workflow.py    # NEW (#78)
├── projectDocs/
│   └── {PROJECT_KEY}/
│       ├── templates/          # NEW
│       ├── blueprints/         # NEW
│       ├── artifacts/          # NEW (generated)
│       ├── proposals/          # NEW
│       ├── raid/               # Step 1
│       └── audit/              # Step 1

AI-Agent-Framework-Client/
├── client/
│   ├── e2e/
│   │   ├── step2-workflow.spec.ts    # NEW (#109)
│   │   ├── pages/
│   │   │   ├── ArtifactEditorPage.ts # NEW
│   │   │   ├── ProposalListPage.ts   # NEW
│   │   │   └── ProposalReviewPage.ts # NEW
│   │   └── fixtures/
│   │       └── test-templates.ts     # NEW
│   └── ...
├── src/
│   ├── components/
│   │   ├── artifacts/        # NEW in Step 2
│   │   │   ├── ArtifactEditor.tsx      (#102)
│   │   │   └── ArtifactsList.tsx       (#103)
│   │   ├── proposals/        # NEW in Step 2
│   │   │   ├── ProposalCreator.tsx     (#104)
│   │   │   ├── ProposalList.tsx        (#105)
│   │   │   └── ProposalReviewModal.tsx (#106)
│   │   ├── audit/            # Step 1 (enhanced in Step 2)
│   │   │   ├── AuditViewer.tsx         (#107 - enhanced)
│   │   │   └── AuditBadges.tsx         (#108 - NEW)
│   │   ├── raid/             # Step 1
│   │   └── workflow/         # Step 1
│   └── domain/
│       ├── TemplateApiClient.ts   # NEW
│       ├── ProposalApiClient.ts   # NEW
│       ├── ProjectApiClient.ts    # Step 1
│       ├── RAIDApiClient.ts       # Step 1
│       └── WorkflowApiClient.ts   # Step 1
```

---

## Appendix B: API Endpoints (Step 2 Additions)

### Templates

- `GET /templates` - List all templates (filter by type, category)
- `GET /templates/{id}` - Get template by ID
- `POST /templates` - Create new template
- `PUT /templates/{id}` - Update template
- `DELETE /templates/{id}` - Delete template

### Blueprints

- `GET /projects/{key}/blueprints` - List blueprints for project
- `GET /blueprints/{id}` - Get blueprint by ID
- `POST /projects/{key}/blueprints` - Create blueprint from template
- `PUT /blueprints/{id}` - Update blueprint
- `DELETE /blueprints/{id}` - Delete blueprint

### Artifacts (Enhanced)

- `GET /projects/{key}/artifacts` - List artifacts (filter by type)
- `GET /artifacts/{id}` - Get artifact by ID
- `POST /projects/{key}/artifacts/generate` - Generate artifact from blueprint
- `PUT /artifacts/{id}` - Update artifact (creates proposal)
- `DELETE /artifacts/{id}` - Delete artifact

### Proposals (NEW)

- `GET /projects/{key}/proposals` - List proposals (filter by status)
- `GET /proposals/{id}` - Get proposal by ID
- `POST /projects/{key}/proposals` - Create manual proposal
- `PATCH /proposals/{id}` - Apply or reject proposal
  - Body: `{"action": "apply"}` or `{"action": "reject"}`
- `DELETE /proposals/{id}` - Delete proposal (if pending)

---

## Appendix C: Validation Commands Summary

**Backend validation:**

```bash
# Setup
./setup.sh && source .venv/bin/activate && mkdir -p projectDocs

# Run API
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Test health
curl http://localhost:8000/health

# Run tests
pytest tests/unit/         # Unit tests
pytest tests/integration/  # Integration tests
pytest tests/e2e/         # E2E tests (Step 2)

# Lint
python -m black apps/api/
python -m flake8 apps/api/
```

**Frontend validation:**

```bash
# Setup
cd _external/AI-Agent-Framework-Client && npm install

# Run dev server
npm run dev  # http://localhost:5173

# Test
npm run lint
npm run test -- --run
npm run test:e2e

# Build
npm run build  # Should complete in ~120ms
```

**Docker validation:**

```bash
mkdir -p projectDocs
docker compose up --build

# Verify
curl http://localhost:8080  # WebUI
curl http://localhost:8000/health  # API
```

---

## Appendix D: Key Decisions & Rationale

### Decision 1: Why proposal workflow instead of direct editing?

**Rationale:** ISO 21500 requires change control and traceability. Proposal workflow ensures:

- All changes are reviewed before application
- Diffs are visible (what changed, who changed it)
- Audit trail is complete (proposal created → reviewed → applied/rejected)

### Decision 2: Why separate templates and blueprints?

**Rationale:** Separation of concerns:

- **Templates** are generic, reusable, organization-wide (managed by PMO)
- **Blueprints** are project-specific, customized by project teams
- This allows template updates without affecting existing projects

### Decision 3: Why Git storage for artifacts?

**Rationale:** Full version history, branching, merging capabilities. Git provides:

- Complete audit trail (every change is a commit)
- Conflict resolution (if needed)
- Backup and disaster recovery (Git remotes)

### Decision 4: Why E2E tests as separate issues?

**Rationale:** E2E tests are the final gate for Step 2. They:

- Validate all components work together
- Catch integration bugs unit tests miss
- Serve as executable documentation of Step 2 workflow

### Decision 5: Why 18 issues instead of 6?

**Rationale:** Small, focused issues enable:

- **Concurrency:** Multiple devs work in parallel
- **Early feedback:** PRs are small and reviewable
- **Incremental progress:** Each issue delivers value independently

---

**Last Updated:** 2026-02-01  
**Document Owner:** AI Agent  
**Status:** Approved for implementation  
**Related Documents:** `planning/issues/step-2-revised.yml`, `planning/step-2-requirements-coverage.md`
