# Step 2 Planning - Complete ISO Workflow Spine

**Date:** 2026-01-17
**Step:** 2 - Templates, Blueprints, Proposals, and Cross-Artifact Audits
**Prerequisite:** Step 1 (COMPLETE ✅)

---

## Table of Contents

1. [Overview](#overview)
2. [Step 2 Goals](#step-2-goals)
3. [Issue Breakdown](#issue-breakdown)
4. [Dependencies](#dependencies)
5. [Implementation Sequence](#implementation-sequence)
6. [Cross-Repo Coordination](#cross-repo-coordination)
7. [Testing Strategy](#testing-strategy)
8. [Success Criteria](#success-criteria)

---

## Overview

Step 2 extends Step 1's PMP+RAID backbone with the **full artifact lifecycle**, including:

- **Templates**: Structured schemas for artifacts with validation
- **Blueprints**: Collections of templates defining methodologies
- **Proposals**: Structured, auditable change workflow with diffs
- **Cross-Artifact Audits**: Automated validation and consistency checks

This step transforms the system from basic artifact storage to a **complete artifact management workflow** with AI assistance and quality gates.

---

## Step 2 Goals

### From step-2.yml

By the end of Step 2, the system must support:

1. **Template & Blueprint System**
   - Define artifact schemas with required fields and validation rules
   - Create blueprints that specify required artifact collections
   - Generate artifacts from templates with default values
   - Drive UI navigation based on blueprint requirements

2. **Proposal Workflow**
   - Create proposals (manual or AI-assisted) with diffs
   - Review proposals with clear diff visualization
   - Apply accepted proposals atomically with audit events
   - Reject proposals with rationale
   - Maintain proposal history for governance

3. **Cross-Artifact Audit**
   - Validate required fields per template schema
   - Check cross-artifact references (RAID ↔ PMP)
   - Detect consistency issues (dates, owners, statuses)
   - Generate actionable results (error/warning/info)
   - Link results back to specific artifact fields
   - Support re-running audits after fixes

---

## Issue Breakdown

### Backend Issues (AI-Agent-Framework)

#### Issue 1: Implement Artifact Templates + Blueprint System

**Goal:** Provide template and blueprint system that drives artifact generation and validation

**Scope:**

1. **Templates:**
   - Structured schema (required fields, field types, validation rules)
   - Markdown templates for rendering
   - PMP minimum sections: purpose, scope, deliverables, milestones, roles, communications, change control
   - RAID minimum columns: type, description, owner, status, impact, due date
   - JSON Schema validation support

2. **Blueprints:**
   - Specify collections of required templates
   - Define artifact relationships and dependencies
   - Drive UI navigation and workflow requirements
   - Support multiple methodologies (ISO 21500 baseline)

3. **Artifact Generation:**
   - Generate artifacts from templates with default values
   - Populate based on project metadata
   - Support AI-assisted generation (hook for LLM service)

**API Endpoints:**

- `GET /api/v1/templates` - List available templates
- `GET /api/v1/templates/{id}` - Get template details
- `POST /api/v1/templates` - Create template (admin)
- `PUT /api/v1/templates/{id}` - Update template (admin)
- `GET /api/v1/blueprints` - List available blueprints
- `GET /api/v1/blueprints/{id}` - Get blueprint details
- `POST /api/v1/blueprints` - Create blueprint (admin)
- `PUT /api/v1/blueprints/{id}` - Update blueprint (admin)
- `POST /api/v1/artifacts/generate` - Generate artifact from template

**Data Models:**

```python
class Template(BaseModel):
    id: str
    name: str
    description: str
    artifact_type: str  # "pmp", "raid", etc.
    schema: Dict[str, Any]  # JSON Schema
    markdown_template: str
    required_fields: List[str]
    field_types: Dict[str, str]
    validation_rules: Dict[str, Any]

class Blueprint(BaseModel):
    id: str
    name: str
    description: str
    methodology: str  # "ISO21500", "Agile", etc.
    required_templates: List[str]  # Template IDs
    artifact_relationships: Dict[str, List[str]]
    workflow_stages: List[str]
```

**Storage:**

- Templates: `templates/{id}.json`
- Blueprints: `blueprints/{id}.json`
- Generated artifacts: `{project}/artifacts/{type}/{id}.md` (or `.json`)

**Tests Required:**

- Unit tests: Template validation, blueprint resolution, artifact generation logic
- Integration tests: API CRUD for templates/blueprints, generation endpoint
- Coverage: Field validation, schema validation, default value population

**Estimated Effort:** 3-4 days

---

#### Issue 2: Implement Proposal System for Artifact Changes

**Goal:** Enable structured, auditable changes to artifacts via proposal workflow

**Scope:**

1. **Proposal Model:**
   - Target artifact reference
   - Change type: create, update, delete
   - Diff/patch content (unified diff or structured)
   - Rationale/description
   - Status: pending, accepted, rejected
   - Author, timestamp, correlation_id
   - AI-assisted flag

2. **Proposal Lifecycle:**
   - **Create**: Manual edit or AI-assisted suggestion
   - **Review**: Display diff with context
   - **Apply**: Merge changes atomically, create audit event
   - **Reject**: Record decision with reason
   - History tracking for governance

3. **Diff Generation:**
   - Unified diff format for text artifacts
   - Structured diff for JSON artifacts
   - Context lines (3-5 lines before/after)
   - Highlight additions/deletions

4. **AI Integration Hook:**
   - Interface for LLM-based proposal generation
   - Prompt templates for different artifact types
   - Fallback to manual proposals if AI unavailable

**API Endpoints:**

- `GET /api/v1/projects/{project_key}/proposals` - List proposals
- `GET /api/v1/projects/{project_key}/proposals/{id}` - Get proposal details
- `POST /api/v1/projects/{project_key}/proposals` - Create proposal
- `PUT /api/v1/projects/{project_key}/proposals/{id}` - Update proposal
- `POST /api/v1/projects/{project_key}/proposals/{id}/apply` - Apply proposal
- `POST /api/v1/projects/{project_key}/proposals/{id}/reject` - Reject proposal

**Data Models:**

```python
class ProposalChangeType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class ProposalStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Proposal(BaseModel):
    id: str
    project_key: str
    artifact_id: str
    artifact_type: str
    change_type: ProposalChangeType
    diff: str  # Unified diff or structured JSON
    rationale: str
    status: ProposalStatus
    author: str
    created_at: str
    updated_at: str
    applied_at: Optional[str]
    rejected_at: Optional[str]
    rejection_reason: Optional[str]
    ai_assisted: bool = False
    correlation_id: Optional[str]
```

**Storage:**

- Proposals: `{project}/proposals/{id}.json`
- Applied proposals: Tracked in artifact history + audit events

**Tests Required:**

- Unit tests: Proposal validation, diff generation, apply/reject logic
- Integration tests: Proposal CRUD, apply/reject operations
- E2E tests: Create artifact → propose change → apply → verify update
- Coverage: Concurrent proposals, conflict detection, audit event creation

**Estimated Effort:** 4-5 days

---

#### Issue 3: Implement Cross-Artifact Audit System

**Goal:** Automated validation and consistency checks across artifacts

**Scope:**

1. **Audit Framework:**
   - Configurable rule system
   - Rule types: required fields, cross-references, consistency checks
   - Severity levels: error, warning, info
   - Location tracking (artifact, section, field)

2. **Audit Rules:**
   - **Required Fields**: Check template-defined required fields
   - **Cross-References**: RAID items reference PMP deliverables/milestones
   - **Consistency**: Date ranges, owner validation, status alignment
   - **Completeness**: Percentage of required fields filled

3. **Audit Results:**
   - Structured result format with location and severity
   - Actionable suggestions for fixes
   - Link to artifact editor with pre-populated field
   - History tracking (audit runs over time)

4. **Execution:**
   - On-demand audit runs
   - Scheduled audits (hook for future automation)
   - Incremental audits (changed artifacts only)

**API Endpoints:**

- `POST /api/v1/projects/{project_key}/audit/run` - Trigger audit
- `GET /api/v1/projects/{project_key}/audit/results` - Get latest results
- `GET /api/v1/projects/{project_key}/audit/history` - Get audit run history
- `GET /api/v1/audit/rules` - List available audit rules

**Data Models:**

```python
class AuditSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class AuditResult(BaseModel):
    id: str
    severity: AuditSeverity
    rule_id: str
    rule_name: str
    message: str
    artifact_id: str
    artifact_type: str
    section: Optional[str]
    field: Optional[str]
    suggestion: Optional[str]
    location: str  # Human-readable location string

class AuditRun(BaseModel):
    id: str
    project_key: str
    started_at: str
    completed_at: str
    status: str  # "running", "completed", "failed"
    results: List[AuditResult]
    summary: Dict[str, int]  # error_count, warning_count, info_count
    artifacts_checked: int
    rules_executed: int
```

**Storage:**

- Audit runs: `{project}/audit/runs/{id}.json`
- Latest results: `{project}/audit/latest.json` (symlink)

**Tests Required:**

- Unit tests: Individual audit rules, result generation
- Integration tests: Full audit run, result retrieval
- E2E tests: Create incomplete artifact → run audit → verify errors
- Coverage: All rule types, cross-reference validation, suggestion generation

**Estimated Effort:** 4-5 days

---

### Client Issues (AI-Agent-Framework-Client)

#### Issue 4: Web UI - Artifact Editor with Template-Driven Forms

**Goal:** Structured, template-driven artifact editor for PMP and RAID

**Scope:**

1. **Artifact Editor Components:**
   - Dynamic form generation from template JSON schemas
   - Field types: text, textarea, markdown, date, select, multi-select
   - Inline validation with error messages
   - Save/draft/publish workflow
   - Version tracking display

2. **PMP Editor:**
   - Sections: Purpose, Scope, Deliverables, Milestones, Roles, Communications, Change Control
   - Markdown support for long-form content
   - Table editing for deliverables/milestones
   - Required field indicators

3. **RAID Table Editor:**
   - Grid/table view with inline editing
   - Columns: Type, Description, Owner, Status, Impact, Likelihood, Due Date
   - Row-level actions: edit, delete, duplicate
   - Bulk actions: filter, sort, export

4. **Navigation:**
   - Project selector → Blueprint view → Artifact list → Artifact editor
   - Breadcrumb navigation
   - Unsaved changes warning

**Components:**

```typescript
// Core editor components
<ArtifactEditor artifact={artifact} template={template} onSave={handleSave} />
<TemplateForm schema={template.schema} values={values} onChange={handleChange} />
<MarkdownEditor content={content} onChange={handleChange} />
<RAIDTableEditor items={items} onUpdate={handleUpdate} />

// Navigation
<ProjectSelector projects={projects} onSelect={handleSelect} />
<BlueprintView blueprint={blueprint} artifacts={artifacts} />
<ArtifactList artifacts={artifacts} onSelect={handleSelect} />
<Breadcrumbs path={currentPath} />
```

**API Integration:**

- Fetch templates: `GET /api/v1/templates`
- Fetch artifact: `GET /api/v1/projects/{key}/artifacts/{id}`
- Save artifact: `PUT /api/v1/projects/{key}/artifacts/{id}`
- Create artifact: `POST /api/v1/artifacts/generate`

**Tests Required:**

- Unit tests: Form rendering, field validation, markdown editor
- Integration tests: API client for artifacts/templates, save/load operations
- E2E tests: Create PMP → fill fields → save → reload → verify
- Coverage: All field types, validation, error handling

**Estimated Effort:** 5-6 days

---

#### Issue 5: Web UI - Proposal Creation, Review, and Apply Workflow

**Goal:** Full proposal workflow with diff visualization

**Scope:**

1. **Proposal Creation UI:**
   - **Manual**: Edit artifact → "Propose Changes" → generates diff
   - **AI-Assisted**: "Suggest Improvements" → AI generates proposal → review
   - Rationale input (required)
   - Preview diff before saving

2. **Proposal List View:**
   - Filter by status (pending/accepted/rejected)
   - Sort by date, author, artifact
   - Status badges and indicators
   - Quick actions: review, accept, reject

3. **Proposal Detail/Review:**
   - Side-by-side diff view (original vs. proposed)
   - Unified diff view (GitHub-style)
   - Toggle between views
   - Inline comments (future enhancement)
   - Rationale display
   - Author and timestamp

4. **Proposal Actions:**
   - **Accept**: Confirm → apply changes → show success + audit event
   - **Reject**: Provide reason → confirm → record rejection
   - **Edit**: Modify proposal before applying (creates new proposal)

**Components:**

```typescript
// Proposal workflow
<ProposalCreate artifact={artifact} onSave={handleSave} />
<ProposalList proposals={proposals} filters={filters} onSelect={handleSelect} />
<ProposalDetail proposal={proposal} onAccept={handleAccept} onReject={handleReject} />
<DiffViewer original={original} proposed={proposed} mode="side-by-side" />
<UnifiedDiff diff={unifiedDiff} />
<ProposalActions proposal={proposal} onAccept={handleAccept} onReject={handleReject} />
```

**API Integration:**

- List proposals: `GET /api/v1/projects/{key}/proposals`
- Get proposal: `GET /api/v1/projects/{key}/proposals/{id}`
- Create proposal: `POST /api/v1/projects/{key}/proposals`
- Apply proposal: `POST /api/v1/projects/{key}/proposals/{id}/apply`
- Reject proposal: `POST /api/v1/projects/{key}/proposals/{id}/reject`

**Tests Required:**

- Unit tests: Proposal components, diff rendering, action handlers
- Integration tests: Proposal API client, apply/reject operations
- E2E tests: Full workflow (create → review → apply → verify artifact updated)
- Coverage: Manual proposals, AI proposals, accept/reject flows

**Estimated Effort:** 5-6 days

---

#### Issue 6: Web UI - Audit Results Viewer with Actionable Links

**Goal:** Display audit results with navigation to fix issues

**Scope:**

1. **Audit Page:**
   - **Trigger Audit**: Button to run audit on demand
   - **Results Display**:
     - Grouped by severity (errors → warnings → info)
     - Expandable sections
     - Color-coded severity indicators
     - Count badges (5 errors, 12 warnings)
   - **Result Details**:
     - Artifact name and type
     - Section and field location
     - Error message
     - Suggestion (if available)
     - Link to artifact editor

2. **Status Indicators:**
   - **Project-level**: Audit status badge in header
     - Green: No errors
     - Yellow: Warnings only
     - Red: Errors present
   - **Artifact-level**: Completeness percentage
     - Progress bar (e.g., "75% complete")
     - Required fields filled count
   - **Last audit run**: Timestamp + status

3. **Navigation:**
   - Click result → opens artifact editor
   - Pre-populate/focus on relevant field
   - Highlight missing/invalid field
   - "Fix All" button (future: auto-apply suggestions)

4. **Filtering & Sorting:**
   - Filter by severity, artifact type, section
   - Sort by severity, artifact, timestamp
   - Search results

**Components:**

```typescript
// Audit viewer
<AuditPage project={project} />
<AuditTrigger onRun={handleRunAudit} />
<AuditResults results={results} onNavigate={handleNavigate} />
<AuditResultGroup severity="error" results={errorResults} />
<AuditResultItem result={result} onClick={() => navigateToArtifact(result)} />
<AuditStatusBadge status={auditStatus} />
<ArtifactCompletenessIndicator artifact={artifact} />
```

**API Integration:**

- Run audit: `POST /api/v1/projects/{key}/audit/run`
- Get results: `GET /api/v1/projects/{key}/audit/results`
- Get history: `GET /api/v1/projects/{key}/audit/history`

**Tests Required:**

- Unit tests: Audit result components, filtering, sorting
- Integration tests: Audit API client, navigation
- E2E tests: Trigger audit → view results → navigate to artifact → fix issue → re-audit
- Coverage: All severity levels, navigation, status indicators

**Estimated Effort:** 4-5 days

---

## Dependencies

### Issue Dependencies

```
Backend:
  Issue 1 (Templates/Blueprints)
    ↓
  Issue 2 (Proposals) ← depends on Issue 1 (needs artifact schemas)
    ↓
  Issue 3 (Audits) ← depends on Issue 1 (needs template schemas)

Client:
  Issue 4 (Artifact Editor) ← depends on Backend Issue 1 (needs templates API)
    ↓
  Issue 5 (Proposal UI) ← depends on Backend Issue 2 (needs proposals API)
  Issue 6 (Audit UI) ← depends on Backend Issue 3 (needs audit API)
```

### Critical Path

1. **Backend Issue 1** (Templates/Blueprints) - MUST be first
   - Blocks all other backend issues
   - Blocks client Issue 4

2. **Backend Issue 2** (Proposals) - After Issue 1
   - Needs artifact schemas from Issue 1
   - Blocks client Issue 5

3. **Backend Issue 3** (Audits) - After Issue 1, parallel to Issue 2
   - Needs template schemas from Issue 1
   - Can be developed in parallel with Issue 2
   - Blocks client Issue 6

4. **Client Issue 4** (Artifact Editor) - After Backend Issue 1
   - Needs templates API from backend
   - Should be done before Issues 5 & 6

5. **Client Issue 5** (Proposal UI) - After Backend Issue 2
   - Needs proposals API from backend
   - Parallel to Issue 6

6. **Client Issue 6** (Audit UI) - After Backend Issue 3
   - Needs audit API from backend
   - Parallel to Issue 5

---

## Implementation Sequence

### Recommended Order

#### Phase 1: Foundation (Week 1-2)

**Backend Issue 1: Templates & Blueprints**

- Days 1-2: Data models, storage layer
- Days 3-4: API endpoints, validation
- Days 5-6: Artifact generation, tests
- Days 7: Integration tests, documentation

**Outcome:** Template and blueprint system operational, artifact generation working

#### Phase 2: Backend Core Workflows (Week 2-4)

**Backend Issue 2: Proposals** (Parallel with Issue 3)

- Days 1-2: Proposal model, diff generation
- Days 3-4: API endpoints, apply/reject logic
- Days 5-6: AI integration hook, tests
- Day 7: E2E tests, documentation

**Backend Issue 3: Audits** (Parallel with Issue 2)

- Days 1-2: Audit framework, rule system
- Days 3-4: Core audit rules implementation
- Days 5-6: API endpoints, result generation
- Day 7: Integration tests, documentation

**Outcome:** Full backend workflow operational

#### Phase 3: Client UI (Week 4-6)

**Client Issue 4: Artifact Editor**

- Days 1-2: Template-driven form components
- Days 3-4: PMP editor, RAID table editor
- Days 5-6: Validation, save/load integration
- Day 7: Tests, documentation

**Outcome:** Users can create and edit artifacts

#### Phase 4: Client Advanced Features (Week 6-8)

**Client Issue 5: Proposal UI** (Parallel with Issue 6)

- Days 1-2: Proposal creation UI
- Days 3-4: Diff viewer components
- Days 5-6: Review and apply workflow
- Day 7: E2E tests

**Client Issue 6: Audit UI** (Parallel with Issue 5)

- Days 1-2: Audit results viewer
- Days 3-4: Navigation and filtering
- Days 5: Status indicators
- Days 6-7: E2E tests, documentation

**Outcome:** Full client workflow operational

### Total Estimated Time: 6-8 weeks

---

## Cross-Repo Coordination

### API Contract Coordination

**Required for each backend issue:**

1. Define API contract **before** implementation
2. Document in `docs/api/api-contract-matrix.md`
3. Create matching client types/interfaces
4. Coordinate breaking changes via linked issues

### Issue Linking Pattern

Backend issues should reference client issues:

```
Backend Issue 1 (Templates/Blueprints)
→ Requires: None
→ Blocks: Client Issue 4 (Artifact Editor)
→ Link: "Implements API for blecx/AI-Agent-Framework-Client#XX"
```

Client issues should reference backend issues:

```
Client Issue 4 (Artifact Editor)
→ Requires: Backend Issue 1 (Templates/Blueprints)
→ Link: "Consumes API from blecx/AI-Agent-Framework#YY"
```

### Testing Coordination

1. **Backend completes integration tests first**
2. **Client implements unit tests with mocked API**
3. **Cross-repo E2E tests last**

Use `tests/e2e/backend_e2e_runner.py` for coordinated E2E testing.

---

## Testing Strategy

### Backend Testing Requirements

Each backend issue must include:

1. **Unit Tests:**
   - Model validation
   - Service logic
   - Rule/validation functions
   - Target: 90%+ coverage for new code

2. **Integration Tests:**
   - API endpoints (CRUD operations)
   - Error handling
   - Authentication/authorization (if applicable)
   - Target: All endpoints covered

3. **E2E Tests:**
   - Complete workflow scenarios
   - Cross-service integration
   - Audit event verification
   - Target: Happy path + major error cases

### Client Testing Requirements

Each client issue must include:

1. **Unit Tests:**
   - Component rendering
   - State management
   - Validation logic
   - Target: 80%+ coverage for components

2. **Integration Tests:**
   - API client mocking
   - Data flow through components
   - Error handling
   - Target: All API integrations covered

3. **E2E Tests:**
   - Full user workflows
   - Cross-component navigation
   - Backend integration
   - Target: Critical user paths

### Test Documentation

Update `tests/README.md` for each issue:

- New test files
- How to run tests
- Coverage requirements
- Known limitations

---

## Success Criteria

### Step 2 Complete When:

#### Backend:

- ✅ All 3 backend issues implemented and merged
- ✅ Templates and blueprints operational
- ✅ Proposal workflow functional with diffs
- ✅ Cross-artifact audit system working
- ✅ All API endpoints documented
- ✅ Test coverage >90% for new code
- ✅ All tests passing in CI
- ✅ `tests/README.md` updated

#### Client:

- ✅ All 3 client issues implemented and merged
- ✅ Artifact editor with template-driven forms
- ✅ Proposal creation, review, and apply UI
- ✅ Audit results viewer with navigation
- ✅ All components tested
- ✅ E2E tests covering full workflows
- ✅ Client `tests/README.md` updated

#### Integration:

- ✅ Cross-repo E2E tests passing
- ✅ API contracts documented and validated
- ✅ No breaking changes without coordination
- ✅ Both repos deployable independently

#### Documentation:

- ✅ Step 2 implementation summary created
- ✅ API documentation complete
- ✅ User workflows documented
- ✅ Architecture decision records (ADRs) for major design choices

---

## Next Steps

### Immediate Actions:

1. **Review this plan** with stakeholders
2. **Create GitHub issues** from this plan
   - Use templates from `.github/prompts/`
   - Link issues across repositories
3. **Set up project board** to track progress
4. **Begin Backend Issue 1** (Templates & Blueprints)

### Before Starting Each Issue:

1. ✅ Confirm prerequisites complete
2. ✅ Review API contract with client team
3. ✅ Create issue with acceptance criteria
4. ✅ Set up feature branch
5. ✅ Write tests first (TDD approach)

### After Completing Each Issue:

1. ✅ Run all tests locally
2. ✅ Update `tests/README.md`
3. ✅ Create PR with detailed description
4. ✅ Request review from relevant team members
5. ✅ Merge after approval
6. ✅ Update project board

---

## Risks & Mitigations

### Risk 1: Template Schema Complexity

**Impact:** High - Affects all issues
**Mitigation:**

- Start with simple schemas (string, number, boolean)
- Iterate to complex types (nested objects, arrays)
- Use JSON Schema standard
- Test with real PMP/RAID examples

### Risk 2: Diff Generation Accuracy

**Impact:** High - Critical for proposal workflow
**Mitigation:**

- Use proven diff library (difflib, diff-match-patch)
- Test with various content types (markdown, JSON)
- Handle edge cases (whitespace, line endings)
- Provide both unified and side-by-side views

### Risk 3: Cross-Artifact Reference Resolution

**Impact:** Medium - Affects audit quality
**Mitigation:**

- Define clear reference syntax (e.g., `RAID-001`, `PMP:deliverable:3`)
- Build reference index during artifact save
- Cache references for fast lookup
- Handle circular references

### Risk 4: Client-Backend API Coupling

**Impact:** Medium - Slows development
**Mitigation:**

- Define API contracts upfront
- Version APIs (`/api/v1/`, `/api/v2/`)
- Use contract testing
- Coordinate breaking changes via linked issues

### Risk 5: Test Flakiness

**Impact:** Low - Slows CI
**Mitigation:**

- Avoid sleep-based timing
- Use proper awaits and retries
- Isolate tests (unique temp directories)
- Monitor test execution times

---

## Appendix

### Useful Commands

```bash
# Backend development
cd AI-Agent-Framework
source .venv/bin/activate
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Run specific test file
pytest tests/unit/test_template_service.py -v

# Run integration tests for templates
pytest tests/integration/test_template_api.py -v

# Client development
cd AI-Agent-Framework-Client
npm install
npm run dev

# Run client tests
npm test -- ArtifactEditor

# Cross-repo E2E
cd AI-Agent-Framework
python tests/e2e/backend_e2e_runner.py --mode server &
cd ../AI-Agent-Framework-Client
npm run test:e2e
```

### Related Documents

- `PLAN.md` - Canonical project plan
- `STEP-1-STATUS.md` - Step 1 completion summary
- `planning/issues/step-2.yml` - Detailed issue definitions
- `tests/README.md` - Testing guide
- `E2E_TESTING.md` - Cross-repo E2E coordination
- `docs/api/api-contract-matrix.md` - API contracts
- `docs/architecture/` - System architecture

---

## Conclusion

Step 2 builds on Step 1's solid foundation to deliver the **complete ISO workflow spine** with:

- 📋 **Templates & Blueprints** - Structured artifact schemas
- 📝 **Proposal Workflow** - Auditable change management
- ✅ **Cross-Artifact Audits** - Automated quality gates
- 🎨 **Rich UI** - Template-driven editors, diff viewers, audit navigation

Estimated timeline: **6-8 weeks** with proper coordination and testing.

The system will be **production-ready** for managing ISO 21500/21502 compliant projects with full artifact lifecycle support.
