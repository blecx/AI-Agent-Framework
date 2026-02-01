# Multi-Step Planning Procedure

**Purpose:** Create comprehensive planning documentation for major feature steps (like Step 2 and Step 3) that delivers production-quality requirements specifications, coverage analysis, implementation roadmaps, and GitHub issues.

**When to use:** For complex, multi-issue feature work that requires 2+ weeks, cross-repo coordination, or systematic requirements analysis. For smaller features, use the Quick Feature Planning template at the end of this document.

**Proven track record:** This procedure was used successfully for:
- Step 2 planning (PR #84): 18 issues, 2234 lines of documentation, 100% coverage
- Step 3 planning (PR #87): 6 issues, 2234 lines of documentation, 100% coverage

---

## Overview

This planning procedure produces 3 comprehensive planning documents plus GitHub issues:

1. **STEP-N-REQUIREMENTS.md** (800-900 lines) - Complete requirements specification
2. **step-N-requirements-coverage.md** (550-700 lines) - 100% coverage validation
3. **step-N-complete-status.md** (600-700 lines) - Implementation roadmap
4. **6-9 GitHub issues** - Comprehensive issue templates in correct repositories

**Total planning time:** 6-10 hours (can be split across multiple sessions)

---

## Phase 1: Requirements Analysis (60-90 min)

### Step 1.1: Read Step Definition

```bash
# Read the high-level step definition
cat planning/issues/step-N.yml

# Review related planning docs
cat planning/STEP-{N-1}-REQUIREMENTS.md | head -100
cat usedChats/master_plan_for_solution_merged.md | grep -A 20 "Step N"
```

### Step 1.2: Analyze Architecture Compliance

Review existing DDD architecture:

```bash
# Backend structure
tree apps/api/domain/
tree apps/api/services/
tree apps/api/routers/

# Client structure (if exists)
tree _external/AI-Agent-Framework-Client/client/src/domain/
tree _external/AI-Agent-Framework-Client/client/src/components/
```

### Step 1.3: Identify Core Requirements

Goal: Identify 6-9 high-level capabilities (not issues yet).

**Questions to answer:**
- What problem does Step N solve?
- What are the 6-9 major capabilities required?
- How does this relate to previous steps?
- What's in scope vs. out of scope?

**Output:** List of 6-9 requirement names (R1-R9)

---

## Phase 2: Requirements Specification (120-180 min)

Create `planning/STEP-N-REQUIREMENTS.md` with exactly these sections:

### Section 1: Executive Summary

```markdown
## Executive Summary

**Step N Goal:** [1 sentence describing what this step delivers]

**What Step N adds to Step {N-1}:** [2-3 bullet points of new capabilities]

**Success criteria:** [1-2 sentences on how we know it's done]
```

### Section 2: Context

```markdown
## Context: How Step N Relates to Previous Steps

### Step 1 Delivered (Completed)
- ✅ [Capability 1]
- ✅ [Capability 2]
- ✅ [Capability 3-7]

### Step 2 Delivered (18 Issues) [if applicable]
- ✅ [Capability 1]
- ✅ [Capability 2]
- ✅ [Capability 3-7]

### Step N Focus: [Primary Focus Name]

Step {N-1} delivered **[functional capability / quality hardening]**. Step N delivers **[quality / new features]** through:

1. **[Capability 1]:** [1 sentence]
2. **[Capability 2]:** [1 sentence]
3. **[Capability 3-5]:** [1 sentence each]

**Why Step N exists:** [2-3 sentences explaining business/technical need]
```

### Section 3: Complete Requirements (R1-R9)

For EACH requirement, use this exact template:

```markdown
### R[N]: [Requirement Name]

**Description:** [1-2 sentences explaining what this is]

**Why it matters:** [2-3 sentences on business/technical value - explain the "why"]

**Must deliver:**
- ✅ [Specific deliverable 1]
- ✅ [Specific deliverable 2]
- ✅ [Specific deliverable 3]
- ✅ [Specific deliverable 4]
- ✅ [Specific deliverable 5+]

**Acceptance criteria:**
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]
- [ ] [Testable criterion 4]
- [ ] [Testable criterion 5]
- [ ] [Testable criterion 6+]

**API/interfaces involved:**
- [List endpoints, services, or interfaces]
- [Example: POST /api/v1/templates, TemplateService.create()]

**Mapped to issues:**
- [Issue ID]: [Issue title] (#[number])
- [Example: BE-01: Template domain models (#69)]

**Validation:**
\```bash
# [Actual commands to verify this requirement]
curl http://localhost:8000/api/v1/[endpoint] | jq
pytest tests/[path]/test_[module].py -v
cd apps/web && npm run test -- [component].test.tsx
\```
```

**Requirement count:** Aim for 6-9 requirements total. More than 9 suggests the step should be split.

### Section 4: Requirements Traceability Matrix

Create comprehensive traceability table:

```markdown
## Requirements Traceability Matrix

| Requirement | Issues | Backend Files | Client Files | Tests | Status |
|-------------|--------|---------------|--------------|-------|--------|
| R1: Template Management | BE-01, BE-02, BE-03 | `apps/api/domain/templates/models.py`, `apps/api/services/template_service.py`, `apps/api/routers/templates.py` | - | `tests/unit/test_templates.py`, `tests/integration/test_template_api.py` | ✅ 100% |
| R2: Blueprint Management | BE-04 | `apps/api/domain/blueprints/models.py`, `apps/api/services/blueprint_service.py` | - | `tests/unit/test_blueprints.py` | ✅ 100% |
| [Add all requirements] | | | | | |
```

### Section 5: Implementation Order

Document 3-4 phases with clear dependencies:

```markdown
## Implementation Order

**Phase 1 (Week 1-2): [Phase Name]**

```
Backend:
BE-01 → BE-02 → BE-03 (sequential: models → service → API)

Client (concurrent):
UX-01 (can start after BE-03 merged)
```

**Dependencies:** BE-03 must be merged before UX-01 can start

**Phase 2 (Week 3-4): [Phase Name]**

```
Backend:
BE-04 → BE-05 (sequential)

Client (concurrent):
UX-02 → UX-03 (sequential)
```

**Dependencies:** No blocking dependencies - backend and client work in parallel
```

### Section 6: Validation Commands

List exact commands for each requirement:

```markdown
## Validation Commands

### R1: Template Management

\```bash
# Unit tests
pytest tests/unit/test_templates.py -v

# Integration tests
pytest tests/integration/test_template_api.py -v

# API validation
curl -X POST http://localhost:8000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{"name":"ISO21500-PMP","type":"pmp","schema":{...}}'

curl http://localhost:8000/api/v1/templates?type=pmp | jq

# Git verification
cd projectDocs && git log --oneline | grep "Template"
\```

[Repeat for R2-R9]
```

### Section 7: Out of Scope

```markdown
## Out of Scope

Explicitly deferred or not applicable to Step N:

- [Capability 1] - Deferred to Step {N+1}
- [Capability 2] - Not required for MVP
- [Capability 3] - Already handled by Step {N-1}
- [Capability 4-5]
```

### Section 8: FAQs

```markdown
## FAQs

### Q1: Why not [alternative approach]?

[2-3 sentence answer explaining decision]

### Q2: How does [feature X] work with [feature Y]?

[2-3 sentence answer explaining integration]

[Add 6-10 FAQs total addressing common questions]
```

### Section 9: Appendices

```markdown
## Appendix A: Key Decisions

**Decision 1: [Decision name]**
- **Context:** [What problem]
- **Decision:** [What we chose]
- **Rationale:** [Why]
- **Consequences:** [Trade-offs]

[Document 3-5 key decisions]

## Appendix B: DDD Architecture for Step N

**Domain Layer:**
- `apps/api/domain/[domain]/models.py` - Entities, value objects, aggregates
- Pure business logic, no infrastructure dependencies
- Pydantic models for validation

**Service Layer:**
- `apps/api/services/[domain]_service.py` - Application services
- Orchestrates domain logic, Git operations
- Thin service methods (< 50 lines per method)

**Infrastructure Layer:**
- `apps/api/routers/[domain].py` - HTTP endpoints
- Thin controllers, delegate to services
- FastAPI dependency injection

**Client Layer:**
- `client/src/domain/[Domain]ApiClient.ts` - API integration
- `client/src/components/[feature]/[Component].tsx` - UI components
- Type-safe interfaces, proper error handling

**File Size Targets:**
- Domain models: < 100 lines per file
- Service classes: < 250 lines per file
- Router files: < 150 lines per file
- API clients: < 150 lines per file
- React components: < 100 lines per component
```

**Target length:** 800-900 lines total

---

## Phase 3: Coverage Analysis (60-90 min)

Create `planning/step-N-requirements-coverage.md`:

### Section 1: Requirements Coverage Matrix

```markdown
# Step N: Requirements Coverage Analysis

**Status:** ✅ **COMPLETE** - All Step N requirements fully covered by X issues  
**Date:** YYYY-MM-DD  
**Coverage:** 100% (X/X requirements mapped to issues)

---

## Requirements Coverage Matrix

| Requirement | Step N Scope | Issues | Coverage | Notes |
|-------------|--------------|--------|----------|-------|
| **R1:** [Name] | [1 sentence scope] | BE-XX | ✅ 100% | [Evidence] |
| **R2:** [Name] | [1 sentence scope] | BE-YY, BE-ZZ | ✅ 100% | [Evidence] |
| [R3-R9] | | | | |

**Total:** X requirements mapped to Y issues
```

### Section 2: Coverage Validation (for each R1-R9)

```markdown
### R1: [Requirement Name] (Issue BE-XX) ✅

**What's covered:**
- ✅ [Specific capability 1]
- ✅ [Specific capability 2]
- ✅ [Specific capability 3]
- ✅ [Specific capability 4]
- ✅ [Specific capability 5+]

**Evidence of completeness:**
- Issue BE-XX acceptance criteria list all 8 mandatory capabilities
- Framework requirements include [specific items]
- Test stability requirement (5 consecutive CI passes)
- Performance target (< X min execution)
- Documentation in `[path]/README.md`

**Gap analysis:** ✅ No gaps - [1 sentence explaining completeness]
```

### Section 3: Issue Size Analysis

```markdown
## Issue Size Analysis

| Issue | Size | Lines Changed | Days | Rationale |
|-------|------|---------------|------|-----------|
| BE-17 | L | 400-600 | 8-10 | New E2E framework setup + comprehensive test scenarios + CI integration |
| BE-18 | M | 150-250 | 3-4 | Enhanced audit rules + diff stability (shared domain) |
| UX-17 | L | 500-700 | 8-10 | Playwright setup + page objects + visual regression + multiple test suites |
| [All issues] | | | | |

**Size Guidelines:**
- **S (Small):** < 50 lines, < 1 day (prefer for new simple features)
- **M (Medium):** 50-200 lines, 1-2 days (typical feature)
- **L (Large):** 200-500 lines, 3-10 days (frameworks, complex features)
- **XL (Avoid):** > 500 lines (split into smaller issues)

**Distribution:**
- S: X issues (Y%)
- M: X issues (Y%)
- L: X issues (Y%)
- Total: X issues

**Target distribution:** 70% M, 20% S, 10% L
```

### Section 4: Dependency Analysis

```markdown
## Dependency Analysis

### Visualization

\```
Backend (blecx/AI-Agent-Framework):
Phase 1:
  BE-17 (E2E framework) ──┐
                           ├─> Phase 2
  BE-18 (Audit + Diff) ───┘

Phase 2:
  BE-19 (CI gates) [depends on BE-17 + BE-18]

Client (blecx/AI-Agent-Framework-Client):
Phase 1:
  UX-17 (E2E framework) ──┐
                           ├─> Phase 2
  UX-18 (Validation) ─────┘

Phase 2:
  UX-19 (CI gates) [depends on UX-17 + UX-18]

Cross-repo: No blocking dependencies (backend and client work in parallel)
\```

### Dependency Details

**Sequential dependencies (must complete in order):**
- BE-17 → BE-19 (CI gates need E2E tests to exist)
- UX-17 → UX-19 (CI gates need E2E tests to exist)

**Concurrent work (can happen in parallel):**
- BE-17 + UX-17 (both are E2E framework setup)
- BE-18 + UX-18 (backend audit vs client validation - independent)

**Critical path:** BE-17 → BE-19 (or UX-17 → UX-19) - 10-12 days
```

### Section 5: Test Coverage Analysis

```markdown
## Test Coverage Analysis

### Current State (After Step {N-1})

| Test Type | Coverage | Count | Notes |
|-----------|----------|-------|-------|
| Backend Unit | 75% | ~150 tests | Good domain coverage |
| Backend Integration | 65% | ~80 tests | API contract tests |
| Backend E2E | 0% | 0 tests | **GAP** - no workflow tests |
| Client Unit | 60% | ~100 tests | Component tests |
| Client Integration | 50% | ~40 tests | API client tests |
| Client E2E | 0% | 0 tests | **GAP** - no user journey tests |

### Target State (After Step N)

| Test Type | Coverage | Count | Change | Notes |
|-----------|----------|-------|--------|-------|
| Backend Unit | 85% | ~200 tests | +50 tests | Domain + service coverage |
| Backend Integration | 75% | ~110 tests | +30 tests | All API endpoints |
| Backend E2E | 90% | ~15 tests | +15 tests | **NEW** - TUI workflows |
| Client Unit | 75% | ~140 tests | +40 tests | Component + hook coverage |
| Client Integration | 65% | ~55 tests | +15 tests | API client coverage |
| Client E2E | 85% | ~20 tests | +20 tests | **NEW** - User journeys |

**Key improvements:**
- ✅ Backend E2E: 0% → 90% (+90pp)
- ✅ Client E2E: 0% → 85% (+85pp)
- ✅ Backend Unit: 75% → 85% (+10pp)
- ✅ Client Unit: 60% → 75% (+15pp)
```

### Section 6: Risk Analysis

```markdown
## Risk Analysis

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **R1:** Flaky E2E tests cause CI instability | High | Medium | - Require 5 consecutive passes before merge<br>- Use deterministic test data<br>- Avoid sleep() - use proper awaits<br>- Retry logic for network operations |
| **R2:** CI gates too strict - block legitimate PRs | Medium | Medium | - Make gates configurable<br>- Clear error messages with fix suggestions<br>- Grace period for existing code |
| [R3-R8] | | | |

**Risk prioritization:**
1. **Critical (High Impact + High Probability):** [List]
2. **Important (High Impact + Medium Probability):** [List]
3. **Monitor (Lower priority):** [List]
```

### Section 7: Cross-Repo Coordination

```markdown
## Cross-Repo Coordination Plan

### Repositories Involved

- **blecx/AI-Agent-Framework** (Backend): X issues
- **blecx/AI-Agent-Framework-Client** (Client): Y issues

### Blocking Dependencies

**None** - All work can proceed in parallel because:
- Backend E2E tests use existing APIs
- Client E2E tests use existing components
- Audit rules don't require new endpoints
- CI gates are repo-specific

### API Contract Changes

**No breaking changes** - Step N hardens existing capabilities:
- No new endpoints added
- No existing endpoint modifications
- Client can work with current API

### Coordination Strategy

**Weekly sync meetings:**
- Review progress on both repos
- Identify integration issues early
- Coordinate PR merge timing (if needed)

**GitHub issue linking:**
- Backend issues reference related client issues
- Client issues reference backend APIs used
- Cross-reference in PR descriptions

**Validation:**
- Test backend + client integration locally before merging
- Run full E2E suite across both repos
- Verify no regressions in existing features
```

### Section 8: Documentation Requirements

```markdown
## Documentation Requirements

### Files to Create

- [ ] `tests/e2e/tui/README.md` - TUI E2E testing guide (new)
- [ ] `tests/e2e/web/README.md` - Web E2E testing guide (new)
- [ ] `docs/architecture/testing.md` - Testing architecture (new)
- [ ] `docs/ci-cd/quality-gates.md` - CI quality gates reference (new)

### Files to Update

- [ ] `tests/README.md` - Add E2E testing section
- [ ] `docs/architecture/overview.md` - Add testing patterns section
- [ ] `README.md` - Update testing commands
- [ ] `CONTRIBUTING.md` - Add testing guidelines
- [ ] `.github/workflows/ci.yml` - Add quality gate comments
- [ ] `docs/development.md` - Add E2E setup instructions

**Total:** X new files + Y updates = Z documentation tasks
```

### Section 9: Quality Checklist

```markdown
## Quality Checklist

### Requirements Completeness ✅

- [x] All X requirements have acceptance criteria (100% coverage)
- [x] All requirements mapped to specific issues
- [x] All requirements have validation commands
- [x] All requirements explain "why it matters"
- [x] Traceability matrix complete (requirements → issues → files → tests)

### Issue Quality ✅

- [x] All X issues sized S/M/L with effort estimates
- [x] All issues use comprehensive 10-section template
- [x] All issues have testable acceptance criteria (≥ 6 checkboxes)
- [x] All issues have exact validation commands
- [x] All issues document dependencies (blocks/blocked by)
- [x] All issues in correct repositories

### Planning Quality ✅

- [x] Dependencies documented and visualized
- [x] Test coverage targets specified (≥ 80% unit, ≥ 85% E2E)
- [x] Risk analysis complete (≥ 5 risks with mitigation)
- [x] Cross-repo coordination plan documented
- [x] Architecture docs update planned
- [x] Implementation roadmap created (week-by-week)

### DDD Architecture ✅

- [x] All new code follows DDD layering
- [x] File size targets specified (< 250 lines)
- [x] Domain boundaries maintained
- [x] No circular dependencies
- [x] Single Responsibility Principle maintained
```

**Target length:** 550-700 lines total

---

## Phase 4: Implementation Roadmap (60-90 min)

Create `planning/step-N-complete-status.md`:

### Section 1: Planning Complete Declaration

```markdown
# Step N: Planning Complete - Ready for Implementation

**Status:** ✅ **PLANNING COMPLETE** - All X issues created, requirements clarified, ready to start development

**Date:** YYYY-MM-DD  
**Planning Duration:** X sessions (Y hours total)  
**Issues Created:** X (Y backend + Z client)  
**Requirements Coverage:** 100% (N/N requirements fully scoped)

---

## Summary

Step N planning is **complete and ready for implementation**. All requirements have been:

1. ✅ Broken down into small, reviewable issues (S/M/L size)
2. ✅ Organized for concurrent development (2 developers)
3. ✅ Documented with comprehensive acceptance criteria
4. ✅ Created as GitHub issues in correct repositories
5. ✅ Validated against requirements (100% coverage)
```

### Section 2: All Issues Created

```markdown
## All Issues Created

### Backend (blecx/AI-Agent-Framework)

- [x] #XX - Step N.01 — [Issue title]
- [x] #YY - Step N.02 — [Issue title]
- [x] [List all backend issues]

### Client (blecx/AI-Agent-Framework-Client)

- [x] #ZZ - Step N.10 — [Issue title]
- [x] [List all client issues]

**Total:** X issues = Y backend + Z client
```

### Section 3: Requirements Coverage 100%

```markdown
## Requirements Coverage: 100%

| # | Requirement | Issues | Status |
|---|-------------|--------|--------|
| R1 | [Name] | #XX, #YY | ✅ 100% |
| R2 | [Name] | #ZZ | ✅ 100% |
| [R3-R9] | | | |

**All requirements mapped to issues - no gaps.**
```

### Section 4: Detailed Implementation Plan

```markdown
## Detailed Implementation Plan (X weeks)

### Week 1: [Phase Name]

**Backend Developer:**

- **Days 1-3:** Issue BE-17 ([Title]) [Size: L]
  - Day 1: Set up `tests/e2e/tui/` infrastructure
  - Day 2: Create test fixtures and factories
  - Day 3: Implement workflow spine test
  - Expected output: Basic TUI E2E framework working

- **Days 4-5:** Issue BE-18 part 1 ([Title]) [Size: M]
  - Day 4: Cross-reference validation rules
  - Day 5: Date consistency checks
  - Expected output: 5 new audit rules implemented

**Client Developer (concurrent):**

- **Days 1-4:** Issue UX-17 ([Title]) [Size: L]
  - Day 1: Playwright setup and configuration
  - Day 2: Create page objects for main views
  - Day 3: Implement smoke tests (auth, navigation)
  - Day 4: Add visual regression baseline
  - Expected output: Web E2E framework operational

- **Day 5:** Start UX-18 ([Title]) [Size: M]
  - Client-side validation rules setup
  - Expected output: Validation framework scaffolded

**Dependencies:** None - can work in parallel

**Week end review:**
- [ ] BE-17 merged (TUI E2E framework)
- [ ] BE-18 in progress (audit rules)
- [ ] UX-17 merged (Web E2E framework)
- [ ] UX-18 in progress (validation)

---

### Week 2: [Continue for all weeks]

[Same detailed structure for weeks 2-5]
```

### Section 5: Success Metrics

```markdown
## Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Backend unit test coverage | ≥ 85% | `pytest --cov=apps/api --cov-report=term` |
| Backend E2E test coverage | ≥ 90% | Manual verification of workflow coverage |
| Client unit test coverage | ≥ 75% | `npm run test:coverage` |
| Client E2E test coverage | ≥ 85% | Playwright coverage report |
| Test execution time (all) | < 8 min | CI logs total time |
| E2E test execution time | < 5 min | CI logs E2E job time |
| CI first-pass rate | ≥ 80% | GitHub Actions success rate |
| PR merge time | < 3 days | Time from PR creation to merge |
| Documentation completeness | 100% | All required docs updated |
| Zero critical bugs | 0 bugs | GitHub issues tagged "bug, critical" |

### Qualitative Metrics

- [ ] All workflows covered by deterministic E2E tests
- [ ] CI gates prevent incomplete PRs from merging
- [ ] Audit system catches cross-artifact inconsistencies
- [ ] Proposal diffs are stable (100 iterations = identical output)
- [ ] Client handles all error scenarios gracefully
- [ ] No flaky tests (≥ 95% reliability)
```

### Section 6: Comparison to Previous Steps

```markdown
## Step Comparison

| Aspect | Step 1 | Step 2 | Step N |
|--------|--------|--------|--------|
| **Focus** | Core platform | Feature delivery | Quality hardening |
| **Requirements** | 8 core | 9 core | 6 core |
| **Issue count** | 12 | 18 | 6 |
| **Duration** | 4 weeks | 5 weeks | 5 weeks |
| **Team size** | 2 devs | 2 devs | 2 devs |
| **Backend issues** | 8 | 9 | 3 |
| **Client issues** | 4 | 7 | 3 |
| **Test issues** | 0 | 2 | 0 (embedded) |
| **Lines changed** | ~2500 | ~3200 | ~2000 |
| **Key deliverable** | RAID + Workflow | Templates + Proposals | E2E tests + CI gates |

**Evolution:**
- Step 1: Establish foundation (platform, domains, basic features)
- Step 2: Add capabilities (templates, artifact editing, proposals)
- Step N: Harden quality (testing, validation, CI enforcement)
```

### Section 7: Readiness Assessment

```markdown
## Readiness Assessment

### Planning Artifacts ✅

- ✅ STEP-N-REQUIREMENTS.md (XXX lines) - Complete requirements specification
- ✅ step-N-requirements-coverage.md (YYY lines) - 100% coverage validation
- ✅ step-N-complete-status.md (ZZZ lines) - Implementation roadmap
- ✅ docs/architecture/overview.md updated (+145 lines)

**Total planning documentation:** 2XXX lines across 4 files

### Quality Validation ✅

- ✅ 100% requirements coverage (N/N requirements mapped)
- ✅ All X issues have comprehensive templates (10 sections each)
- ✅ Dependency analysis complete (visual diagram + sequencing)
- ✅ Test coverage targets set (unit ≥ 80%, E2E ≥ 85%)
- ✅ Risk analysis complete (5+ risks with mitigation)
- ✅ Cross-repo coordination planned (weekly syncs)
- ✅ Documentation updates identified (X files)

### Issues Created ✅

- ✅ All X issues created in correct repositories
- ✅ Backend: Y issues in blecx/AI-Agent-Framework
- ✅ Client: Z issues in blecx/AI-Agent-Framework-Client
- ✅ All issues use comprehensive templates
- ✅ All issues linked to requirements (traceability)
- ✅ All issues have validation steps (exact commands)

### Architecture Validation ✅

- ✅ DDD principles maintained throughout
- ✅ File size targets specified (< 250 lines)
- ✅ Domain boundaries clear (no violations)
- ✅ No circular dependencies
- ✅ Single Responsibility Principle maintained
- ✅ Cross-repo coordination does not introduce coupling

### Implementation Readiness ✅

- ✅ Week-by-week plan created (X weeks detailed)
- ✅ Success metrics defined (10+ quantitative metrics)
- ✅ Dependencies sequenced (critical path identified)
- ✅ Concurrent work identified (2 developers in parallel)
- ✅ Validation commands documented (exact bash commands)

**Overall Assessment:** ✅ **READY TO START IMPLEMENTATION**

Step N planning meets all quality standards from Step 2 planning. No blockers identified. First issue (BE-XX) can be started immediately.
```

**Target length:** 600-700 lines total

---

## Phase 5: Architecture Documentation (30-45 min)

Update `docs/architecture/overview.md`:

### Add New Section (if major architectural change)

```markdown
## Step N: [Capabilities]

[2-3 paragraphs explaining new architectural elements]

**New components:**
- `tests/e2e/tui/` - TUI-driven E2E test infrastructure
- `tests/e2e/web/` - Web UI E2E test infrastructure
- `.github/workflows/quality-gates.yml` - CI enforcement

**Architecture diagram:**

\```
[ASCII diagram showing new components and their relationships]
\```

**Key patterns:**
- [Pattern 1]: [Description]
- [Pattern 2]: [Description]
```

### Update Revision History

```markdown
## Revision History

- **v1.2.0** (YYYY-MM-DD): Added Step N architecture (E2E testing, CI gates)
- **v1.1.0** (YYYY-MM-DD): Added Step 2 architecture (Templates, Proposals)
- **v1.0.0** (YYYY-MM-DD): Initial architecture documentation
```

**Target addition:** 100-150 lines

---

## Phase 6: Issue Creation (30-60 min)

### Create Issue Template Files

For EACH issue (6-9 total), create `.tmp/issue-be-XX.md` or `.tmp/issue-ux-XX.md`:

```markdown
## Goal

[1-2 sentences: what this issue delivers]

Example: "Implement comprehensive TUI-driven E2E test suite covering project creation, artifact generation, proposal workflow, and audit cycles. Provides automated validation of critical workflows in CI."

## Scope

**In scope:**
- [Capability 1]
- [Capability 2]
- [Capability 3]
- [Capability 4]
- [Capability 5]

**Out of scope (deferred or not applicable):**
- [Excluded item 1] - Deferred to Step {N+1}
- [Excluded item 2] - Not required for MVP
- [Excluded item 3] - Handled by different issue

## Acceptance Criteria

**Functional:**
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]
- [ ] [Testable criterion 4]
- [ ] [Testable criterion 5]
- [ ] [Testable criterion 6+]

**Technical:**
- [ ] Code follows DDD architecture (domain/service/infrastructure layers)
- [ ] Unit tests cover ≥ 80% of new code
- [ ] Integration tests cover all API endpoints (if applicable)
- [ ] E2E tests run reliably in CI (5 consecutive passes)
- [ ] Linting passes (black, flake8 for backend / ESLint for client)
- [ ] No security vulnerabilities introduced
- [ ] Performance acceptable (< X ms response time / < Y min test execution)

**Documentation:**
- [ ] API documentation updated (if backend endpoints added/changed)
- [ ] Component documentation updated (if client components added)
- [ ] Architecture docs updated (if architectural pattern introduced)
- [ ] `tests/README.md` updated with new test setup/commands
- [ ] Code comments explain complex logic

## API Contract (Backend only)

**New endpoints:**

\```http
POST /api/v1/[resource]
GET /api/v1/[resource]/{id}
PUT /api/v1/[resource]/{id}
DELETE /api/v1/[resource]/{id}
\```

**Request schema:**

\```json
{
  "field1": "string",
  "field2": 123,
  "field3": {
    "nested": "value"
  }
}
\```

**Response schema:**

\```json
{
  "id": "uuid",
  "field1": "string",
  "created_at": "2026-02-01T12:00:00Z"
}
\```

**Error responses:**

- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `500 Internal Server Error` - Server error

## Technical Approach

**Domain layer:**

- Create `apps/api/domain/[domain]/models.py` with Pydantic models
- Define entities, value objects, aggregates following DDD
- Pure business logic, no infrastructure dependencies
- File size target: < 100 lines

**Service layer:**

- Implement `apps/api/services/[domain]_service.py`
- Business logic, orchestration, Git operations
- Use GitManager for document storage
- Thin service methods (< 50 lines per method)
- File size target: < 250 lines

**Infrastructure layer:**

- Add routes in `apps/api/routers/[domain].py`
- Thin controllers, delegate to services
- FastAPI dependency injection for services
- File size target: < 150 lines

**Client layer (if UX issue):**

- Create `client/src/domain/[Domain]ApiClient.ts`
- Implement API calls with type safety (no `any` types)
- Proper error handling and retry logic
- Create `client/src/components/[feature]/[Component].tsx`
- React component with hooks, proper state management
- File size targets: < 150 lines (client), < 100 lines (component)

**Testing infrastructure (if test issue):**

- Set up `tests/e2e/[tui|web]/` directory structure
- Create test fixtures and factories
- Implement helper utilities for common operations
- Configure CI integration (.github/workflows/)

## Testing Requirements

**Unit tests:**

- [ ] Domain model validation (valid/invalid inputs)
- [ ] Service business logic (happy path + edge cases)
- [ ] Utility functions (pure functions)
- [ ] Error handling (exceptions raised correctly)
- Target: ≥ 80% coverage of new code

**Integration tests:**

- [ ] API endpoint contracts (request/response schemas)
- [ ] Database operations (CRUD if applicable)
- [ ] Cross-service interactions (service A calls service B)
- [ ] Git operations (commit, push, branch if applicable)
- Target: ≥ 70% coverage of API endpoints

**E2E tests:**

- [ ] Happy path workflow (typical user journey)
- [ ] Error recovery scenarios (network failures, invalid data)
- [ ] Edge cases (empty state, maximum limits)
- [ ] Concurrent operations (if applicable)
- Target: ≥ 85% coverage of critical workflows

## Documentation Updates

- [ ] Update `tests/README.md` with new test setup instructions
- [ ] Update `docs/architecture/overview.md` (if architectural change)
- [ ] Add code examples to `docs/howto/[feature]-guide.md`
- [ ] Update API reference in `docs/api/[domain]-api.md`
- [ ] Add troubleshooting section to docs (if complex setup)

## Dependencies

**Blocks:** [List issue numbers that depend on this]
- Example: #YY (needs this API to exist)

**Blocked by:** [List issue numbers this depends on]
- Example: #XX (needs domain models first)

**Concurrent with:** [List issues that can be worked in parallel]
- Example: #ZZ (independent client work)

## Estimated Effort

**Size:** S / M / L  
**Days:** X-Y (range)  
**Lines changed:** ~XXX (estimate)

**Breakdown:**
- Implementation: X days
- Testing: Y days
- Documentation: Z days
- Code review: W days

## Validation Steps

**Backend:**

\```bash
# Setup environment
cd /path/to/AI-Agent-Framework
source .venv/bin/activate

# Unit tests
pytest tests/unit/test_[module].py -v

# Integration tests
pytest tests/integration/test_[module]_api.py -v

# E2E tests (if applicable)
pytest tests/e2e/tui/test_[workflow].py -v

# Linting
python -m black apps/api/
python -m flake8 apps/api/

# API manual test
curl -X POST http://localhost:8000/api/v1/[endpoint] \
  -H "Content-Type: application/json" \
  -d '{"field":"value"}' | jq

# Verify Git commit (if Git operations)
cd projectDocs && git log --oneline | grep "[commit message]"
\```

**Client:**

\```bash
# Setup environment
cd /path/to/AI-Agent-Framework-Client

# Unit tests
npm test -- [component].test.tsx --run

# Linting
npm run lint

# Type checking
npm run type-check

# Build
npm run build

# E2E tests (if applicable)
npm run test:e2e -- [workflow].spec.ts

# Manual test
npm run dev
# Then navigate to http://localhost:5173/[feature]
\```

**Evidence required:**
- Screenshot of all tests passing
- Screenshot of linting output (no errors)
- API response example (if backend)
- Component render screenshot (if client)
```

### Create GitHub Issues

```bash
# Backend issues
for i in 01 02 03; do
  gh issue create --repo blecx/AI-Agent-Framework \
    --title "Step N.$i — [Issue title]" \
    --body-file .tmp/issue-be-$i.md
done

# Client issues
for i in 10 11 12; do
  gh issue create --repo blecx/AI-Agent-Framework-Client \
    --title "Step N.$i — [Issue title]" \
    --body-file .tmp/issue-ux-$i.md
done

# Capture issue numbers
gh issue list --repo blecx/AI-Agent-Framework --search "Step N" > .tmp/step-N-issues-backend.txt
gh issue list --repo blecx/AI-Agent-Framework-Client --search "Step N" > .tmp/step-N-issues-client.txt
```

---

## Phase 7: Planning PR (30-45 min)

### Step 7.1: Create Planning Tracking Issue

```bash
gh issue create --repo blecx/AI-Agent-Framework \
  --title "docs: Step N Planning Documentation — Complete requirements specification and roadmap" \
  --body "Planning artifacts for Step N.

This tracking issue covers the creation of comprehensive planning documentation:
- STEP-N-REQUIREMENTS.md (requirements specification)
- step-N-requirements-coverage.md (coverage validation)
- step-N-complete-status.md (implementation roadmap)
- docs/architecture/overview.md updates

See planning/STEP-N-REQUIREMENTS.md for detailed requirements.

**Acceptance criteria:**
- [ ] All 3 planning documents created (2000+ lines total)
- [ ] Architecture docs updated
- [ ] All X issues created in correct repositories
- [ ] 100% requirements coverage validated
- [ ] Planning PR merged

**Related issues:**
- Backend: #XX, #YY, #ZZ
- Client: #AA, #BB, #CC"
```

Save the issue number (e.g., #88).

### Step 7.2: Create Feature Branch

```bash
cd /path/to/AI-Agent-Framework
git switch main
git pull
git switch -c docs/step-N-planning-complete
```

### Step 7.3: Stage Planning Files

```bash
git add planning/STEP-N-REQUIREMENTS.md
git add planning/step-N-requirements-coverage.md
git add planning/step-N-complete-status.md
git add docs/architecture/overview.md
git status  # Verify only planning files staged
```

### Step 7.4: Commit with Comprehensive Message

```bash
git commit -m "docs: Add Step N planning documentation

Complete planning documentation for Step N: [Step name/description]

Planning artifacts:
- STEP-N-REQUIREMENTS.md (XXX lines): Complete requirements specification
  - Executive summary and context
  - N core requirements with acceptance criteria
  - Requirements traceability matrix
  - Implementation order (X phases)
  - Validation commands for all requirements
  - Out of scope documentation
  - 8 FAQs addressing common questions
  - Appendix: DDD architecture patterns

- step-N-requirements-coverage.md (YYY lines): 100% coverage validation
  - Requirements coverage matrix (N/N requirements)
  - Coverage validation for each requirement
  - Issue size analysis (S/M/L estimates)
  - Dependency analysis with visual diagram
  - Test coverage analysis (current → target)
  - Risk analysis (5 risks with mitigation)
  - Cross-repo coordination plan
  - Documentation requirements (X files)
  - Quality checklist (all ✅)

- step-N-complete-status.md (ZZZ lines): Implementation roadmap
  - Planning completion summary
  - All X issues listed (Y backend + Z client)
  - Requirements coverage 100% table
  - Detailed implementation plan (week-by-week for X weeks)
  - Success metrics (10+ quantitative targets)
  - Comparison to previous steps
  - Readiness assessment (all ✅)

- docs/architecture/overview.md (+145 lines): Architecture updates
  - New Step N architecture section
  - Testing patterns documentation
  - Component diagrams updated
  - Revision history updated to v1.X.0

Covers N core requirements:
- R1: [Requirement name]
- R2: [Requirement name]
- R3: [Requirement name]
- [R4-R9]

Breaks down into X issues:
- Y backend issues (BE-XX through BE-YY)
- Z client issues (UX-XX through UX-ZZ)

Issues created:
- Backend (blecx/AI-Agent-Framework): #XX, #YY, #ZZ
- Client (blecx/AI-Agent-Framework-Client): #AA, #BB, #CC

All issues use comprehensive 10-section template:
- Goal, Scope, Acceptance Criteria, API Contract
- Technical Approach, Testing Requirements, Documentation Updates
- Dependencies, Estimated Effort, Validation Steps

Quality validation:
- 100% requirements coverage (N/N requirements mapped)
- All X issues sized S/M/L with effort estimates
- Dependency analysis complete (no circular deps)
- Test coverage targets set (unit ≥ 80%, E2E ≥ 85%)
- Architecture docs updated with testing patterns
- DDD principles maintained throughout

Ready for implementation. First issue (BE-XX) can start immediately.

Fixes #[PLANNING-ISSUE-NUMBER]"
```

### Step 7.5: Push Branch

```bash
git push -u origin docs/step-N-planning-complete
```

### Step 7.6: Create PR Description

Create `.tmp/pr-body-step-N-planning.md`:

```markdown
## Goal / Context

Complete planning documentation for Step N: [Step name/description].

This PR delivers comprehensive planning documentation following the proven Step 2 planning methodology:

- **STEP-N-REQUIREMENTS.md** (XXX lines): Complete requirements specification
- **step-N-requirements-coverage.md** (YYY lines): 100% coverage validation
- **step-N-complete-status.md** (ZZZ lines): Implementation roadmap (X weeks)
- **docs/architecture/overview.md** (+145 lines): Architecture updates

**What Step N delivers:**

Step N adds [2-3 bullet points of key capabilities] to the platform.

**Planning quality:**

- ✅ 2XXX lines of planning documentation across 4 files
- ✅ N core requirements fully specified with acceptance criteria
- ✅ X issues created (Y backend + Z client) using comprehensive templates
- ✅ 100% requirements coverage validated (no gaps)
- ✅ Week-by-week implementation plan (X weeks, 2 developers)
- ✅ Dependency analysis complete (visual diagram + sequencing)
- ✅ Test coverage targets set (unit ≥ 80%, E2E ≥ 85%)
- ✅ Risk analysis complete (5+ risks with mitigation)
- ✅ DDD architecture principles maintained

## Acceptance Criteria (required)

### Planning Documentation ✅

- [x] STEP-N-REQUIREMENTS.md created (XXX lines)
  - [x] Executive summary (goal, scope, success criteria)
  - [x] Context section (how Step N relates to previous steps)
  - [x] N requirements with acceptance criteria (6-10 checkboxes each)
  - [x] Requirements traceability matrix (requirements → issues → files → tests)
  - [x] Implementation order (3-4 phases with dependencies)
  - [x] Validation commands (exact bash commands for each requirement)
  - [x] Out of scope documentation (3-5 bullet points)
  - [x] FAQs (6-10 questions addressing common concerns)
  - [x] Appendix A: Key decisions (3-5 architectural decisions)
  - [x] Appendix B: DDD architecture patterns for Step N

- [x] step-N-requirements-coverage.md created (YYY lines)
  - [x] Requirements coverage matrix (100% coverage table)
  - [x] Coverage validation for each requirement (evidence of completeness)
  - [x] Issue size analysis (S/M/L estimates with rationale)
  - [x] Dependency analysis with visual diagram
  - [x] Test coverage analysis (current → target state)
  - [x] Risk analysis (5+ risks with impact/probability/mitigation)
  - [x] Cross-repo coordination plan (blocking dependencies, API changes, sync strategy)
  - [x] Documentation requirements (files to create/update)
  - [x] Quality checklist (all checkboxes ✅)

- [x] step-N-complete-status.md created (ZZZ lines)
  - [x] Planning completion summary (date, duration, issue count, coverage)
  - [x] All issues listed (Y backend + Z client with GitHub links)
  - [x] Requirements coverage 100% table (all requirements mapped to issues)
  - [x] Detailed implementation plan (week-by-week for X weeks, 2 developers)
  - [x] Success metrics (10+ quantitative targets with measurement methods)
  - [x] Comparison to previous steps (evolution table)
  - [x] Readiness assessment (all planning artifacts ✅, quality validation ✅, issues created ✅, architecture validation ✅, implementation readiness ✅)

- [x] docs/architecture/overview.md updated (+145 lines)
  - [x] New Step N architecture section (if major architectural change)
  - [x] Component diagrams updated (ASCII diagrams)
  - [x] Testing patterns documented (DDD testing architecture)
  - [x] Revision history updated (v1.X.0 - YYYY-MM-DD)

### Issues Created ✅

**Backend (blecx/AI-Agent-Framework):**

- [x] Issue #XX: Step N.01 — [Issue title] (Size: S/M/L, X-Y days)
- [x] Issue #YY: Step N.02 — [Issue title] (Size: S/M/L, X-Y days)
- [x] [List all Y backend issues with links]

**Client (blecx/AI-Agent-Framework-Client):**

- [x] Issue #AA: Step N.10 — [Issue title] (Size: S/M/L, X-Y days)
- [x] Issue #BB: Step N.11 — [Issue title] (Size: S/M/L, X-Y days)
- [x] [List all Z client issues with links]

**Total:** X issues (Y backend + Z client)

**Issue quality:**

- [x] All issues use comprehensive 10-section template
- [x] All sections present: Goal, Scope, Acceptance Criteria, API Contract, Technical Approach, Testing Requirements, Documentation Updates, Dependencies, Estimated Effort, Validation Steps
- [x] All issues have 6-10 functional acceptance criteria (testable checkboxes)
- [x] All issues have 3-4 technical acceptance criteria (DDD, coverage, linting, docs)
- [x] All issues have exact validation commands (bash commands with expected output)
- [x] All issues document dependencies (blocks/blocked by/concurrent with)
- [x] All issues in correct repositories (backend in AI-Agent-Framework, client in AI-Agent-Framework-Client)

### Quality Validation ✅

**Coverage analysis:**

- [x] 100% requirements coverage (N/N requirements mapped to X issues)
- [x] Traceability matrix complete (requirements → issues → files → tests)
- [x] All requirements have validation commands (exact bash commands)
- [x] All requirements explain "why it matters" (business/technical value)
- [x] No gaps identified in coverage validation sections

**Issue quality:**

- [x] All X issues sized S/M/L with effort estimates (days + lines changed)
- [x] Issue size distribution reasonable (target: 70% M, 20% S, 10% L)
- [x] All issues have testable acceptance criteria (≥ 6 checkboxes)
- [x] All issues have validation steps (exact commands, not "test it")
- [x] Dependencies documented and sequenced correctly

**Architecture validation:**

- [x] DDD principles maintained throughout
- [x] File size targets specified (domain < 100, service < 250, router < 150)
- [x] Domain boundaries clear (no cross-domain coupling)
- [x] No circular dependencies
- [x] Single Responsibility Principle followed
- [x] Cross-repo coordination does not introduce tight coupling

**Testing validation:**

- [x] Test coverage targets specified (unit ≥ 80%, E2E ≥ 85%)
- [x] Test organization documented (tests/unit, tests/integration, tests/e2e)
- [x] CI integration planned (.github/workflows updates)
- [x] Test data factories planned (for E2E tests)
- [x] Deterministic test execution ensured (no sleep, proper awaits)

**Cross-repo coordination:**

- [x] Both repositories assessed (backend + client)
- [x] Blocking dependencies documented (or stated "None")
- [x] API contract changes documented (or stated "No breaking changes")
- [x] Coordination strategy specified (weekly syncs, GitHub issue linking)
- [x] Client issues reference backend APIs used

## Validation Evidence (required)

### Planning Artifacts Created

\```bash
$ ls -lh planning/STEP-N-*.md planning/step-N-*.md docs/architecture/overview.md
-rw-r--r-- 1 user user XXXk Feb  1 12:00 planning/STEP-N-REQUIREMENTS.md
-rw-r--r-- 1 user user YYYk Feb  1 12:00 planning/step-N-requirements-coverage.md
-rw-r--r-- 1 user user ZZZk Feb  1 12:00 planning/step-N-complete-status.md
-rw-r--r-- 1 user user   45k Feb  1 12:00 docs/architecture/overview.md

$ wc -l planning/STEP-N-*.md planning/step-N-*.md
  XXX planning/STEP-N-REQUIREMENTS.md
  YYY planning/step-N-requirements-coverage.md
  ZZZ planning/step-N-complete-status.md
 2XXX total

$ git diff main --stat
 planning/STEP-N-REQUIREMENTS.md          | XXX ++++++++++++++++
 planning/step-N-requirements-coverage.md | YYY +++++++++++++++
 planning/step-N-complete-status.md       | ZZZ ++++++++++++++++
 docs/architecture/overview.md            | 145 +++++++++-----
 4 files changed, 2XXX insertions(+), 3 deletions(-)
\```

### Issues Created (Backend)

\```bash
$ gh issue list --repo blecx/AI-Agent-Framework --search "Step N" --json number,title,state
[
  {
    "number": XX,
    "title": "Step N.01 — [Issue title]",
    "state": "OPEN"
  },
  {
    "number": YY,
    "title": "Step N.02 — [Issue title]",
    "state": "OPEN"
  }
]

# Total: Y backend issues
\```

### Issues Created (Client)

\```bash
$ gh issue list --repo blecx/AI-Agent-Framework-Client --search "Step N" --json number,title,state
[
  {
    "number": AA,
    "title": "Step N.10 — [Issue title]",
    "state": "OPEN"
  },
  {
    "number": BB,
    "title": "Step N.11 — [Issue title]",
    "state": "OPEN"
  }
]

# Total: Z client issues
\```

### Architecture Documentation Updated

\```bash
$ git diff main docs/architecture/overview.md | head -30
+## Step N: [Capabilities]
+
+Step N adds [description] to the platform.
+
+**New components:**
+- `[path]` - [Description]
+
+**Architecture diagram:**
+
+\```
+[ASCII diagram]
+\```
+
+**Testing architecture:**
+- Backend: TUI-driven E2E tests in `tests/e2e/tui/`
+- Client: Playwright E2E tests in `tests/e2e/web/`
+
+[... more content]

$ git log --oneline -1
xxxxxxx docs: Add Step N planning documentation
\```

### Requirements Coverage Validation

From `planning/step-N-requirements-coverage.md`:

\```markdown
## Requirements Coverage Matrix

| Requirement | Step N Scope | Issues | Coverage | Notes |
|-------------|--------------|--------|----------|-------|
| R1: [Name] | [Scope] | BE-XX | ✅ 100% | [Evidence] |
| R2: [Name] | [Scope] | BE-YY, BE-ZZ | ✅ 100% | [Evidence] |
| [R3-R9] | ... | ... | ✅ 100% | [Evidence] |

**Total:** N requirements mapped to X issues - 100% coverage
\```

### Automated Checks

**Backend linting:**

- [x] No backend code changes - documentation only (pytest/black/flake8 not required for this PR)

**Frontend linting:**

- [x] No client code changes - documentation only (npm lint/test/build not required for this PR)

### Manual Test Evidence (required)

**Validation performed:**

1. ✅ Read all 3 planning documents end-to-end (completeness check)
   - Each document follows proven Step 2/Step 3 methodology
   - All required sections present with substantial content
   - No placeholder text or TODOs

2. ✅ Verified 100% requirements coverage
   - Created traceability matrix in STEP-N-REQUIREMENTS.md
   - Validated coverage in step-N-requirements-coverage.md
   - All N requirements explicitly mapped to X issues
   - No gaps identified

3. ✅ Validated issue breakdown quality
   - All X issues created in correct repositories
   - All issues use comprehensive 10-section template
   - All sections filled with specific, actionable content
   - Validation steps have exact bash commands (not vague "test it")

4. ✅ Checked issue templates completeness
   - Randomly sampled 3 issues (#XX, #YY, #AA)
   - All have Goal, Scope, Acceptance Criteria, API Contract, Technical Approach
   - All have Testing Requirements, Documentation Updates, Dependencies
   - All have Estimated Effort, Validation Steps
   - All checkboxes are specific and testable

5. ✅ Reviewed dependency analysis
   - Created visual dependency diagram in coverage doc
   - Identified sequential dependencies (X → Y → Z)
   - Identified concurrent work (A + B can run in parallel)
   - No circular dependencies found
   - Critical path documented (X days)

6. ✅ Verified architecture docs updated
   - docs/architecture/overview.md has new Step N section (+145 lines)
   - Testing patterns documented (DDD testing architecture)
   - Component diagrams updated
   - Revision history updated to v1.X.0

7. ✅ Cross-repo coordination assessed
   - Backend issues in blecx/AI-Agent-Framework (Y issues)
   - Client issues in blecx/AI-Agent-Framework-Client (Z issues)
   - Blocking dependencies documented (or confirmed "None")
   - API contracts documented in backend issues
   - Client issues reference backend APIs

**Evidence:**

- Planning documents total 2XXX lines (exceeds 2000 line target)
- All N requirements have 6-10 acceptance criteria (avg X per requirement)
- All X issues sized S/M/L with realistic estimates
- Dependency diagram shows X phases with Y concurrent work streams
- Test coverage targets specified (unit ≥ 80%, E2E ≥ 85%)
- Implementation plan details X weeks of work for 2 developers
- Success metrics define 10+ quantitative targets
- DDD architecture principles maintained (file size targets < 250 lines)

**Quality comparison to Step 2 planning:**

| Metric | Step 2 | Step N | Status |
|--------|--------|--------|--------|
| Total planning lines | 2234 | 2XXX | ✅ Similar |
| Requirements count | 9 | N | ✅ Appropriate |
| Issues created | 18 | X | ✅ Appropriate |
| Coverage | 100% | 100% | ✅ Same |
| Issue template sections | 10 | 10 | ✅ Same |
| Documentation files | 3 | 3 | ✅ Same |
| Architecture updates | Yes | Yes | ✅ Same |

Step N planning follows identical methodology to successful Step 2 planning.

## How to Review

1. **Start with executive summaries (5 min):**
   - Read [planning/STEP-N-REQUIREMENTS.md](planning/STEP-N-REQUIREMENTS.md) Executive Summary
   - Read [planning/step-N-complete-status.md](planning/step-N-complete-status.md) Summary section
   - Understand: What does Step N deliver? Why does it matter?

2. **Validate completeness (10 min):**
   - Check requirements coverage matrix in [step-N-requirements-coverage.md](planning/step-N-requirements-coverage.md)
   - Verify all N requirements mapped to X issues (100% coverage table)
   - Review coverage validation sections (evidence of completeness for each R1-R9)
   - Confirm no gaps identified

3. **Review issue quality (15 min):**
   - Pick 3 random issues and review GitHub issue descriptions:
     - Backend: #XX, #YY
     - Client: #AA
   - Verify all 10 sections present:
     - Goal, Scope, Acceptance Criteria, API Contract, Technical Approach
     - Testing Requirements, Documentation Updates, Dependencies
     - Estimated Effort, Validation Steps
   - Check acceptance criteria are testable (specific, measurable)
   - Check validation steps have exact bash commands

4. **Check implementation plan (10 min):**
   - Review week-by-week roadmap in [step-N-complete-status.md](planning/step-N-complete-status.md)
   - Validate dependency analysis (no circular deps)
   - Check if concurrent work identified (2 developers working in parallel)
   - Confirm realistic effort estimates (X weeks, Y days per issue)
   - Review success metrics (10+ quantitative targets)

5. **Validate architecture alignment (10 min):**
   - Review DDD architecture appendix in [STEP-N-REQUIREMENTS.md](planning/STEP-N-REQUIREMENTS.md)
   - Check [docs/architecture/overview.md](docs/architecture/overview.md) updates
   - Verify no architectural violations
   - Confirm file size targets specified (< 250 lines)
   - Check domain boundaries maintained

6. **Verify cross-repo coordination (5 min):**
   - Check cross-repo section in [step-N-requirements-coverage.md](planning/step-N-requirements-coverage.md)
   - Confirm Y backend issues in blecx/AI-Agent-Framework
   - Confirm Z client issues in blecx/AI-Agent-Framework-Client
   - Validate API contracts documented in backend issues
   - Check coordination strategy (weekly syncs, issue linking)

**Total review time:** ~50-60 minutes

**Key questions:**
- ✅ Is 100% coverage claim backed by evidence?
- ✅ Are issues comprehensive enough to implement without ambiguity?
- ✅ Is the implementation plan realistic (effort + dependencies)?
- ✅ Does architecture maintain DDD principles?
- ✅ Are both repos coordinated properly?

## Cross-repo / Downstream Impact (always include)

### Repositories Affected

- **blecx/AI-Agent-Framework (Backend):**
  - Planning documentation added (3 files, 2XXX lines)
  - Y backend issues created (#XX, #YY, #ZZ)
  - Architecture docs updated (+145 lines)
  
- **blecx/AI-Agent-Framework-Client (Client):**
  - Z client issues created (#AA, #BB, #CC)
  - No documentation changes in this PR (client repo issues only)

### Downstream Changes Required

**After this PR merges:**
- None for this planning PR (documentation only)
- Implementation PRs will follow for each issue

**During Step N implementation:**
- Backend PRs in blecx/AI-Agent-Framework for issues #XX, #YY, #ZZ
- Client PRs in blecx/AI-Agent-Framework-Client for issues #AA, #BB, #CC

### API Changes

**This PR:** None (planning documentation only)

**During Step N implementation:**
- [List any new/changed endpoints from requirements doc]
- Example: No new endpoints - Step N hardens existing capabilities
- OR: New endpoints: POST /api/v1/[endpoint], GET /api/v1/[endpoint]/{id}

### Coordination Notes

**Cross-repo dependencies:**
- [State blocking dependencies or "None"]
- Example: "No blocking dependencies - backend and client work can proceed in parallel"
- See [step-N-requirements-coverage.md](planning/step-N-requirements-coverage.md) Section 7 for detailed coordination plan

**Implementation sequencing:**
- Phase 1 (Week 1-2): [Backend issue #XX] + [Client issue #AA] (concurrent)
- Phase 2 (Week 3-4): [Backend issue #YY] + [Client issue #BB] (concurrent)
- Phase 3 (Week 5): [Backend issue #ZZ] + [Client issue #CC] (concurrent)

**Validation:**
- Each issue has repo-specific validation steps (exact bash commands)
- Integration testing: Test backend + client together before final merge
- E2E testing: Run full workflow tests across both repos

## Issue / Tracking Link (required)

Fixes: #[PLANNING-ISSUE-NUMBER]

**Related issues:**

Backend (blecx/AI-Agent-Framework):
- #XX - Step N.01 — [Issue title]
- #YY - Step N.02 — [Issue title]
- #ZZ - Step N.03 — [Issue title]

Client (blecx/AI-Agent-Framework-Client):
- #AA - Step N.10 — [Issue title]
- #BB - Step N.11 — [Issue title]
- #CC - Step N.12 — [Issue title]
```

### Step 7.7: Create PR

```bash
gh pr create \
  --repo blecx/AI-Agent-Framework \
  --base main \
  --head docs/step-N-planning-complete \
  --title "docs: Step N Planning Documentation — Complete requirements specification and roadmap" \
  --body-file .tmp/pr-body-step-N-planning.md
```

### Step 7.8: Monitor CI and Fix if Needed

```bash
# Wait for CI to start
sleep 30

# Check CI status
gh pr checks [PR-NUMBER]

# If CI fails, investigate
gh run view [RUN-ID] --log-failed

# Common fix: Update PR body for CI template compliance
gh api -X PATCH repos/blecx/AI-Agent-Framework/pulls/[PR-NUMBER] \
  --field body=@.tmp/pr-body-updated.md

# Trigger CI re-run with empty commit
git commit --allow-empty -m "chore: trigger CI with updated PR description"
git push

# Wait and verify
sleep 30
gh pr checks [PR-NUMBER]
```

### Step 7.9: Merge PR

```bash
# After CI passes
gh pr merge [PR-NUMBER] --squash --delete-branch
```

### Step 7.10: Clean Up

```bash
# Remove temporary files
rm -f .tmp/pr-body-step-N-planning.md
rm -f .tmp/pr-body-updated.md
rm -f .tmp/issue-be-*.md
rm -f .tmp/issue-ux-*.md
rm -f .tmp/step-N-issues-*.txt

# Switch back to main and pull
git switch main
git pull

# Verify planning docs are on main
ls -lh planning/STEP-N-*.md planning/step-N-*.md
```

---

## Expected Outputs Checklist

After completing this procedure, you will have:

### Planning Documentation ✅

- [ ] `planning/STEP-N-REQUIREMENTS.md` (800-900 lines)
  - [ ] Executive summary (goal, scope, success criteria)
  - [ ] Context section (how Step N relates to previous steps)
  - [ ] N requirements (R1-R9) with comprehensive details
  - [ ] Requirements traceability matrix
  - [ ] Implementation order (3-4 phases)
  - [ ] Validation commands (exact bash commands)
  - [ ] Out of scope documentation
  - [ ] 8+ FAQs
  - [ ] Appendix A: Key decisions
  - [ ] Appendix B: DDD architecture

- [ ] `planning/step-N-requirements-coverage.md` (550-700 lines)
  - [ ] Requirements coverage matrix (100% table)
  - [ ] Coverage validation (R1-R9 each validated)
  - [ ] Issue size analysis (S/M/L distribution)
  - [ ] Dependency analysis (visual diagram)
  - [ ] Test coverage analysis (current → target)
  - [ ] Risk analysis (5+ risks with mitigation)
  - [ ] Cross-repo coordination plan
  - [ ] Documentation requirements (files to update)
  - [ ] Quality checklist (all ✅)

- [ ] `planning/step-N-complete-status.md` (600-700 lines)
  - [ ] Planning complete declaration
  - [ ] All issues listed (backend + client with links)
  - [ ] Requirements coverage 100% table
  - [ ] Detailed implementation plan (week-by-week)
  - [ ] Success metrics (10+ quantitative)
  - [ ] Comparison to previous steps
  - [ ] Readiness assessment (all ✅)

- [ ] `docs/architecture/overview.md` (+100-150 lines)
  - [ ] New Step N architecture section
  - [ ] Component diagrams updated
  - [ ] Testing patterns documented
  - [ ] Revision history updated

### GitHub Issues Created ✅

- [ ] Y backend issues in `blecx/AI-Agent-Framework`
  - [ ] All use comprehensive 10-section template
  - [ ] All have 6-10 functional acceptance criteria
  - [ ] All have exact validation commands
  - [ ] All sized S/M/L with effort estimates

- [ ] Z client issues in `blecx/AI-Agent-Framework-Client`
  - [ ] All use comprehensive 10-section template
  - [ ] All have 6-10 functional acceptance criteria
  - [ ] All have exact validation commands
  - [ ] All sized S/M/L with effort estimates

### Planning PR Merged ✅

- [ ] Planning issue created (#XX)
- [ ] Feature branch created (`docs/step-N-planning-complete`)
- [ ] Comprehensive commit message
- [ ] PR created with comprehensive description
- [ ] CI passed (all checks ✅)
- [ ] PR merged (squash merge)
- [ ] Planning issue auto-closed
- [ ] Branch deleted
- [ ] Temporary files cleaned up

### Quality Validation ✅

- [ ] 100% requirements coverage validated
- [ ] All N requirements mapped to X issues (no gaps)
- [ ] All issues in correct repositories
- [ ] Dependency analysis complete (no circular deps)
- [ ] DDD architecture principles maintained
- [ ] File size targets specified (< 250 lines)
- [ ] Test coverage targets set (≥ 80% unit, ≥ 85% E2E)
- [ ] Cross-repo coordination planned
- [ ] Implementation readiness confirmed

---

## Quality Standards Summary

### Planning Document Length Targets

- STEP-N-REQUIREMENTS.md: **800-900 lines**
- step-N-requirements-coverage.md: **550-700 lines**
- step-N-complete-status.md: **600-700 lines**
- **Total:** 2000-2300 lines of planning documentation

### Requirements Count

- **Minimum:** 6 core requirements
- **Maximum:** 9 core requirements
- **Sweet spot:** 7-8 requirements
- Each requirement: 50-100 lines (description, why, must deliver, acceptance criteria, validation)

### Issue Count and Size

- **Total issues:** 6-18 (depends on step complexity)
- **Distribution:** 70% M (Medium), 20% S (Small), 10% L (Large)
- **S (Small):** < 50 lines, < 1 day
- **M (Medium):** 50-200 lines, 1-2 days
- **L (Large):** 200-500 lines, 3-10 days
- **Avoid XL:** > 500 lines (split instead)

### Issue Template Sections (All 10 Required)

1. Goal (1-2 sentences)
2. Scope (In/Out of scope)
3. Acceptance Criteria (Functional + Technical + Documentation)
4. API Contract (Backend only)
5. Technical Approach (Domain/Service/Infrastructure layers)
6. Testing Requirements (Unit/Integration/E2E)
7. Documentation Updates (files to create/update)
8. Dependencies (Blocks/Blocked by/Concurrent)
9. Estimated Effort (Size, Days, Lines)
10. Validation Steps (Exact bash commands)

### DDD Architecture Standards

**File size targets:**
- Domain models: < 100 lines per file
- Service classes: < 250 lines per file
- Router files: < 150 lines per file
- API clients: < 150 lines per file
- React components: < 100 lines per component
- Test helpers: < 150 lines per file

**When to split:**
- File > 250 lines → extract helper classes
- Class has multiple responsibilities → refactor to SRP
- Service orchestrates > 3 domains → consider facade pattern

### Testing Standards

**Coverage targets:**
- Backend unit tests: ≥ 80%
- Backend integration tests: ≥ 70%
- Backend E2E tests: ≥ 90% of critical workflows
- Client unit tests: ≥ 75%
- Client E2E tests: ≥ 85% of user journeys

**Test reliability:**
- E2E tests: ≥ 95% pass rate (5 consecutive passes required)
- Execution time: < 5 min for E2E suite, < 8 min total
- Deterministic: No sleep(), use proper awaits
- Data isolation: Use factories, clean state between tests

### Documentation Standards

**Required updates:**
- `tests/README.md` - Testing setup and commands
- `docs/architecture/overview.md` - System architecture
- `docs/api/[domain]-api.md` - API documentation (if new endpoints)
- `docs/howto/[feature]-guide.md` - User guide (if user-facing)
- `README.md` - Top-level updates (if major capabilities)

### Cross-Repo Coordination Standards

**For backend issues:**
- Document API endpoints added/changed
- Specify request/response schemas (JSON examples)
- Note if client changes required
- Link to client issues (if exists)

**For client issues:**
- Reference backend API issue number
- Document API client changes
- Specify component dependencies
- Note if backend changes required

**Coordination workflow:**
1. Create backend issue first (if new API)
2. Create client issue with backend reference
3. Implement backend PR (if backward compatible)
4. Implement client PR (depends on backend)
5. Merge backend, then client

### CI/PR Standards

**PR description must include:**
- All section headers from template (Goal, Acceptance Criteria, Validation Evidence, How to Review, Cross-repo Impact, Issue Link)
- All checkboxes checked (don't create PR until work complete)
- `Fixes: #<issue-number>` format (not "Closes")
- Validation section has exact commands run
- Evidence includes actual output (test counts, build times)
- "How to review" has 4+ meaningful steps (not just "review code")
- Cross-repo impact assessed (even if "None")

**CI requirements:**
- All automated checks pass (lint, test, build)
- PR description validates against template
- All required sections present
- All checkboxes checked
- Evidence provided for test execution (or explicit "No code changes")

---

## Success Metrics

### Planning Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Requirements coverage | 100% | All requirements mapped to issues |
| Issue template completeness | 100% | All 10 sections in each issue |
| Planning document length | 2000-2300 lines | Sum of 3 planning docs |
| Issue size distribution | 70% M, 20% S, 10% L | Count by size label |
| Planning duration | 6-10 hours | Time from start to PR merge |
| CI first-pass rate | ≥ 80% | PRs passing CI without fixes |
| Requirements per step | 6-9 | Count of R1-R9 |
| Issues per step | 6-18 | Total backend + client |
| Average issue quality score | ≥ 9/10 sections | Completeness audit |
| DDD compliance | 100% | All code follows patterns |

### Implementation Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Issue completion rate | 100% | All issues closed |
| PR merge time | < 3 days avg | Time from creation to merge |
| Test coverage (backend) | ≥ 80% | `pytest --cov` |
| Test coverage (client) | ≥ 75% | Vitest coverage report |
| E2E coverage | ≥ 85% | Manual workflow verification |
| E2E test reliability | ≥ 95% | 5 consecutive passes |
| Documentation completeness | 100% | All required docs updated |
| Zero critical bugs | 0 | No "bug, critical" issues |
| Code review cycles | ≤ 2 avg | Rounds before approval |
| Build/test time | < 8 min | Total CI execution time |

---

## Lessons Learned (From Step 2 and Step 3)

### What Worked Exceptionally Well ✅

1. **Comprehensive requirements specification (800+ lines)**
   - Single source of truth prevents confusion
   - Traceability matrix ensures no gaps
   - Validation commands provide clear acceptance criteria
   - FAQs address common questions proactively

2. **100% coverage validation methodology**
   - Explicit gap analysis catches missing work
   - Evidence-based completeness verification
   - Risk analysis with mitigation strategies
   - Quality checklist ensures nothing forgotten

3. **Detailed implementation roadmap (week-by-week)**
   - Day-by-day breakdown for 2 developers
   - Dependency analysis enables parallel work
   - Success metrics provide clear targets
   - Comparison to previous steps shows evolution

4. **Comprehensive 10-section issue templates**
   - Nothing gets forgotten (Goal → Validation Steps)
   - Validation steps make testing explicit
   - DDD architecture guidance maintains consistency
   - Dependencies prevent blocked work

5. **CI-enforced PR template compliance**
   - Prevents incomplete PRs from merging
   - Forces explicit test evidence
   - Maintains documentation quality
   - Catches missing checkboxes early

6. **Cross-repo coordination planning**
   - Identifies blocking dependencies upfront
   - Documents API contracts in backend issues
   - Enables concurrent backend + client work
   - Weekly sync meetings keep teams aligned

### Common Pitfalls to Avoid ❌

1. **Incomplete issue templates**
   - ❌ Missing validation steps → reviewers don't know how to test
   - ✅ Include exact bash commands in every issue
   - ❌ Vague acceptance criteria → "E2E tests work"
   - ✅ Specific criteria → "Workflow spine test runs reliably (5 consecutive passes)"

2. **Underestimating issue size**
   - ❌ "Add E2E tests" as S issue → actually L (400+ lines + framework)
   - ✅ Analyze: framework setup + test scenarios + CI integration + docs
   - ❌ "Implement proposal system" as single issue → 1500+ lines
   - ✅ Split: domain models (S) → service (M) → API (S) → UI (M)

3. **Missing cross-repo coordination**
   - ❌ Create client issue without backend API ready
   - ✅ Document API contract in backend issue first
   - ❌ Assume API is "obvious" from frontend needs
   - ✅ Explicit request/response schemas with JSON examples

4. **Skipping dependency analysis**
   - ❌ Create issues without sequencing → blocked work
   - ✅ Create visual dependency diagram (ASCII art OK)
   - ❌ Assume "everything can be parallel"
   - ✅ Identify critical path and sequential dependencies

5. **Vague acceptance criteria**
   - ❌ "System works correctly"
   - ✅ "Workflow spine test: create project → generate artifacts → propose → apply → audit → verify clean"
   - ❌ "Tests pass"
   - ✅ "Unit test coverage ≥ 80%, integration ≥ 70%, E2E ≥ 90%"

6. **Forgetting documentation updates**
   - ❌ Merge code without updating architecture docs
   - ✅ Include documentation checkboxes in every issue
   - ❌ "Docs can be done later"
   - ✅ Docs are acceptance criteria (block merge if missing)

7. **Not validating 100% coverage**
   - ❌ Assume all requirements covered → find gaps during implementation
   - ✅ Create coverage matrix and validate each requirement
   - ❌ "We'll catch it in code review"
   - ✅ Explicit "evidence of completeness" for each requirement

8. **Creating too many XL issues**
   - ❌ "Implement entire proposal system" (1500+ lines, 10+ days)
   - ✅ Split into: models (S, 1d) → service (M, 2d) → API (S, 1d) → UI (M, 2d)
   - ❌ "Add all CI gates" (12 gates, 800+ lines)
   - ✅ Split by concern: backend gates (M) + client gates (M)

9. **Ignoring DDD architecture**
   - ❌ Put everything in one 500-line service file
   - ✅ Separate: domain (models < 100) + service (< 250) + router (< 150)
   - ❌ Mix infrastructure concerns in domain logic
   - ✅ Keep domain pure, delegate to infrastructure layer

10. **PR description doesn't match template**
    - ❌ Create PR, CI fails on missing sections
    - ✅ Research recent successful PR first: `gh pr view <recent-pr> --json body`
    - ❌ Guess section names: "## Validation" vs "## Validation Evidence (required)"
    - ✅ Copy exact section headers (including "(required)" suffix)

### Process Improvements for Next Time

1. **Start with architecture review**
   - Review existing DDD structure before planning
   - Identify domain boundaries early
   - Check for architectural debt

2. **Use planning time estimates**
   - Phase 1 (Requirements): 60-90 min
   - Phase 2 (Specification): 120-180 min
   - Phase 3 (Coverage): 60-90 min
   - Phase 4 (Roadmap): 60-90 min
   - Phase 5 (Architecture): 30-45 min
   - Phase 6 (Issues): 30-60 min
   - Phase 7 (PR): 30-45 min
   - **Total:** 6-10 hours

3. **Validate incrementally**
   - After each phase, do quick validation
   - Check line counts match targets
   - Verify all sections present
   - Catches issues early

4. **Reference previous planning**
   - Keep Step 2 and Step 3 planning open
   - Copy proven patterns
   - Maintain consistency

5. **Plan for 2 developers concurrently**
   - Forces good dependency analysis
   - Maximizes throughput
   - Realistic for teams

---

## Reference Examples

**Best practices demonstrated in:**

- **Step 2 planning (PR #84):** Feature delivery planning
  - 18 issues (9 backend + 7 client + 2 E2E)
  - Templates, Blueprints, Artifacts, Proposals
  - 2234 lines of documentation
  - 100% coverage validation

- **Step 3 planning (PR #87):** Quality hardening planning
  - 6 issues (3 backend + 3 client)
  - E2E tests, CI gates, audit rules, diff stability
  - 2234 lines of documentation
  - 100% coverage validation

**Example issues:**

- **Issue #85:** TUI E2E test suite (comprehensive template)
- **Issue #69-#77:** Backend feature issues (Templates, Blueprints, Proposals)
- **Issue #102-#109:** Client feature issues (Artifact Editor, Proposal UI)

**Key documents to reference:**

- `planning/STEP-2-REQUIREMENTS.md` - Feature requirements template
- `planning/STEP-3-REQUIREMENTS.md` - Quality requirements template
- `planning/step-2-complete-status.md` - Implementation roadmap template
- `.github/copilot-instructions.md` - DDD architecture standards
- `.github/ISSUE_TEMPLATE/feature_request.yml` - Issue template schema

---

## Quick Feature Planning (For Small Features < 1 Week)

For features that can be completed in < 1 week or < 5 issues, use this simplified approach:

**When to use:**
- Single-domain features (one backend service + one client component)
- Bug fixes requiring multiple changes
- Refactoring work
- Documentation improvements
- Small enhancements to existing features

**When NOT to use (use Multi-Step Planning instead):**
- New major capabilities (templates, proposals, E2E testing)
- Cross-domain features (affects 3+ services)
- Features requiring ≥ 2 weeks of work
- Quality hardening initiatives
- Architectural changes

**Simplified process:**

1. **Feature Spec (30 min):**
   - Goal (1-2 sentences)
   - Scope (In: 3-5 bullets, Out: 2-3 bullets)
   - Acceptance Criteria (5-8 checkboxes)
   - Constraints (technical limitations)
   - Dependencies (related components)

2. **Issue Breakdown (30 min):**
   - 2-5 focused issues
   - Each < 200 lines changed
   - Clear acceptance criteria
   - Logical implementation order

3. **Cross-Repo Impact (15 min):**
   - Backend only? Client only? Both?
   - API changes required?
   - Coordination strategy

4. **Create Issues (15 min):**
   - Use simplified template (Goal, Scope, Acceptance Criteria, Validation)
   - Size S/M only (no L for small features)

**Total time:** 90-120 minutes (vs 6-10 hours for multi-step)

---

## Tips for High-Quality Planning

1. **Start with "Why"**
   - Every requirement should explain business/technical value
   - "Why it matters" section prevents over-engineering
   - Helps reviewers understand tradeoffs

2. **Be explicit about scope**
   - "Out of scope" is as important as "In scope"
   - Prevents scope creep during implementation
   - Documents deferred work for future steps

3. **Write validation commands early**
   - Forces you to think about testability
   - Becomes the "definition of done"
   - Removes ambiguity for implementers

4. **Analyze dependencies visually**
   - ASCII diagrams clarify sequencing
   - Enables parallel work identification
   - Shows critical path clearly

5. **Target 70% Medium issues**
   - Medium issues (1-2 days) are ideal PR size
   - Avoid too many Small (not enough value per PR)
   - Avoid too many Large (too risky, hard to review)

6. **Plan for 2 developers working concurrently**
   - Maximizes throughput
   - Forces good dependency analysis
   - Realistic team size

7. **Document decisions and rationale**
   - Future you will thank past you
   - Prevents re-litigating decisions
   - Helps onboard new team members

8. **Validate 100% coverage explicitly**
   - Use traceability matrix (requirements → issues → files → tests)
   - Explicit "evidence of completeness" for each requirement
   - Don't assume - verify

9. **Include FAQs proactively**
   - Address "Why not X?" questions
   - Explain alternatives considered
   - Saves time during review

10. **Follow DDD principles rigorously**
    - Maintain domain boundaries (no cross-domain coupling)
    - Keep files small and focused (< 250 lines)
    - Test each layer independently
    - Use dependency injection for testability

---

## Appendix: Planning Checklist

Use this checklist to ensure planning completeness:

### Phase 1: Requirements Analysis ✅
- [ ] Read step definition from `planning/issues/step-N.yml`
- [ ] Review previous step planning docs
- [ ] Analyze DDD architecture compliance
- [ ] Identify 6-9 core requirements

### Phase 2: Requirements Specification ✅
- [ ] Executive summary (goal, scope, success criteria)
- [ ] Context section (how Step N relates to previous)
- [ ] N requirements (R1-R9) with all subsections
- [ ] Requirements traceability matrix
- [ ] Implementation order (3-4 phases)
- [ ] Validation commands (exact bash)
- [ ] Out of scope documentation
- [ ] 8+ FAQs
- [ ] Appendix A: Key decisions
- [ ] Appendix B: DDD architecture
- [ ] File length: 800-900 lines

### Phase 3: Coverage Analysis ✅
- [ ] Requirements coverage matrix (100% table)
- [ ] Coverage validation for each R1-R9
- [ ] Issue size analysis (S/M/L distribution)
- [ ] Dependency analysis (visual diagram)
- [ ] Test coverage analysis (current → target)
- [ ] Risk analysis (5+ risks with mitigation)
- [ ] Cross-repo coordination plan
- [ ] Documentation requirements
- [ ] Quality checklist
- [ ] File length: 550-700 lines

### Phase 4: Implementation Roadmap ✅
- [ ] Planning complete declaration
- [ ] All issues listed (backend + client)
- [ ] Requirements coverage 100% table
- [ ] Detailed implementation plan (week-by-week)
- [ ] Success metrics (10+ quantitative)
- [ ] Comparison to previous steps
- [ ] Readiness assessment
- [ ] File length: 600-700 lines

### Phase 5: Architecture Documentation ✅
- [ ] New Step N architecture section (if applicable)
- [ ] Component diagrams updated
- [ ] Testing patterns documented
- [ ] Revision history updated
- [ ] Added lines: 100-150

### Phase 6: Issue Creation ✅
- [ ] All issues use 10-section template
- [ ] All sections filled (no placeholders)
- [ ] All have 6-10 acceptance criteria
- [ ] All have exact validation commands
- [ ] All sized S/M/L with estimates
- [ ] All in correct repositories

### Phase 7: Planning PR ✅
- [ ] Planning tracking issue created
- [ ] Feature branch created
- [ ] Comprehensive commit message
- [ ] PR description with all sections
- [ ] CI passed
- [ ] PR merged (squash)
- [ ] Planning issue auto-closed
- [ ] Branch deleted
- [ ] Temporary files cleaned up

### Quality Validation ✅
- [ ] 100% requirements coverage validated
- [ ] All issues in correct repos
- [ ] Dependency analysis complete
- [ ] DDD principles maintained
- [ ] File size targets specified
- [ ] Test coverage targets set
- [ ] Cross-repo coordination planned
- [ ] Implementation readiness confirmed

---

**End of Multi-Step Planning Procedure**

**Total length:** ~1100 lines (this document)  
**Expected planning output:** 2000-2300 lines + X issues  
**Planning time:** 6-10 hours  
**Proven success rate:** 100% (Step 2 + Step 3)
