# Step 3: Complete Requirements Specification

## Executive Summary

**Step 3 Goal:** Harden the system with comprehensive E2E testing, robust audit rules, stable diffs, and CI quality gates to ensure production readiness.

**What Step 3 adds to Step 2:** TUI-driven E2E test infrastructure, enhanced cross-artifact audit validation, diff stability for proposals, client-side error handling, and comprehensive CI quality gates that enforce testing and documentation standards.

**Success criteria:** All workflows are covered by deterministic E2E tests running in CI, audit system validates complex cross-artifact relationships, proposal diffs are stable and accurate, client handles all error scenarios gracefully, and CI prevents merging code without complete tests and documentation.

---

## Context: How Step 3 Relates to Previous Steps

### Step 1 Delivered (Completed)

- ✅ Core platform (projects, Git storage, REST API, React WebUI)
- ✅ RAID register (full CRUD, filtering, status updates)
- ✅ Workflow engine (state machine, transitions, validation)
- ✅ Audit system (event logging, impact tracking, viewer UI)
- ✅ Domain-Driven Design architecture

### Step 2 Delivered (18 Issues)

- ✅ Template system (domain models + service + API)
- ✅ Blueprint management
- ✅ Artifact generation from templates
- ✅ Visual artifact editor (WebUI)
- ✅ Proposal workflow (create → review → apply/reject)
- ✅ Cross-artifact audit system
- ✅ End-to-end test coverage (basic)

### Step 3 Focus: Production Hardening

Step 1 and Step 2 delivered **functional capability**. Step 3 delivers **production quality** through:

1. **Comprehensive E2E Testing**: TUI-driven deterministic tests covering all workflows
2. **Enhanced Audit Rules**: Cross-artifact validation, dependency cycles, date consistency
3. **Diff Stability**: Deterministic proposal diffs with conflict detection
4. **Client Resilience**: Error handling, validation, network recovery, accessibility
5. **CI Quality Gates**: Enforce testing, documentation, coverage, and code quality standards

**Why Step 3 exists:** Production systems require rigorous testing, error handling, and quality enforcement. Step 3 transforms a "working prototype" into a "production-ready system."

---

## Complete Step 3 Requirements (6 Core)

### R1: TUI-Driven E2E Test Suite (Backend)

**Description:** Comprehensive, deterministic, non-interactive E2E test suite using the TUI that covers complete workflow spine from project creation through audit cycles.

**Why it matters:** Manual testing doesn't scale and isn't repeatable. TUI-driven E2E tests ensure all workflows work end-to-end and catch integration issues before production.

**Must deliver:**

- ✅ TUI automation framework (`tests/e2e/tui/` infrastructure)
- ✅ Test data factories for projects, artifacts, proposals, RAID items
- ✅ Deterministic test execution (no sleep-based timing, proper awaits)
- ✅ Comprehensive scenario coverage (happy path + error recovery)
- ✅ CI integration (headless, automated, fast feedback)

**Acceptance criteria:**

- [ ] TUI E2E framework supports scripted (non-interactive) execution
- [ ] Tests placed in `tests/e2e/tui/` with clear naming
- [ ] Workflow spine test: create project → generate artifacts → edit → propose → apply → audit
- [ ] Proposal workflow test: create manual + AI proposals → review → apply/reject → verify
- [ ] Audit fix cycle test: run audit → detect issues → fix → re-run → verify clean
- [ ] Tests run reliably in CI (5 consecutive passes required)
- [ ] Test execution time < 5 minutes for full suite
- [ ] `tests/README.md` documents TUI E2E setup, commands, CI integration

**API/interfaces involved:**

- TUI command execution interface
- Project creation, artifact generation, proposal lifecycle
- Audit execution and result parsing
- Test harness for input/output capture

**Mapped to issue:**

- BE-17: TUI-driven deterministic E2E test suite (backend) (#TBD)

**Validation:**

```bash
# Run TUI E2E tests locally
pytest tests/e2e/tui/ -v

# Run in CI mode (headless)
TERM=xterm-256color pytest tests/e2e/tui/ --tb=short

# Check test stability (5 runs)
for i in {1..5}; do pytest tests/e2e/tui/ || exit 1; done

# Verify coverage report
pytest tests/e2e/tui/ --cov=apps/api --cov-report=html
```

**Testing requirements:**

- Unit tests: TUI automation helpers, test factories
- Integration tests: TUI command execution with real backend
- E2E tests: Full workflow scenarios end-to-end
- All tests deterministic (no flaky failures)

---

### R2: Enhanced Cross-Artifact Audit Rules

**Description:** Comprehensive audit validation system that checks cross-artifact references, date consistency, owner validation, dependency cycles, and completeness scoring.

**Why it matters:** Basic field validation (Step 2) isn't enough for production. Complex projects have interdependencies (RAID → PMP milestones, dates must align, owners must exist) that require sophisticated validation.

**Must deliver:**

- ✅ Cross-reference validation engine (RAID items ↔ PMP deliverables/milestones)
- ✅ Date consistency checks (milestone dates vs. project dates, RAID due dates)
- ✅ Owner/actor validation (referenced users/roles exist in project)
- ✅ Dependency cycle detection (circular dependencies in RAID/tasks)
- ✅ Completeness scoring (percentage of required fields populated per template)
- ✅ Configurable rule sets per blueprint
- ✅ Custom rule definition interface (extensibility)
- ✅ Bulk audit across all projects
- ✅ Audit history tracking

**Acceptance criteria:**

- [ ] Cross-reference validation: RAID item references non-existent PMP milestone → error
- [ ] Date consistency: RAID due date after project end date → warning
- [ ] Owner validation: RAID owner not in project team → error
- [ ] Dependency cycle detection: RAID-1 depends on RAID-2 depends on RAID-1 → error
- [ ] Completeness scoring: PMP with 8/10 required fields → 80% score shown
- [ ] Custom rules: Blueprint can define additional validation rules
- [ ] Bulk audit: `POST /audit/bulk` audits all projects and returns summary
- [ ] Audit history: Previous audit results stored and queryable
- [ ] Each rule has comprehensive unit tests (100% coverage target)

**API/interfaces involved:**

- `POST /api/v1/projects/{key}/audit` - Run audit with enhanced rules
- `GET /api/v1/projects/{key}/audit/history` - Get audit history
- `POST /api/v1/audit/bulk` - Bulk audit all projects
- `GET /api/v1/blueprints/{id}/rules` - Get audit rules for blueprint
- `POST /api/v1/blueprints/{id}/rules` - Add custom rule

**Mapped to issue:**

- BE-18: Enhanced cross-artifact audit rules + diff stability (backend) (#TBD)

**Validation:**

```bash
# Run audit with enhanced rules
curl -X POST http://localhost:8000/api/v1/projects/PROJ-001/audit

# Response includes:
# - cross-reference errors (RAID → PMP)
# - date consistency warnings
# - owner validation errors
# - dependency cycle detection
# - completeness score

# Run bulk audit
curl -X POST http://localhost:8000/api/v1/audit/bulk

# Get audit history
curl http://localhost:8000/api/v1/projects/PROJ-001/audit/history
```

**Testing requirements:**

- Unit tests: Each audit rule individually (isolated testing)
- Integration tests: Full audit with all rules active, cross-artifact scenarios
- E2E tests: Complex validation scenarios (multi-artifact dependencies)
- Performance tests: Bulk audit with 100+ projects completes < 30s

---

### R3: Diff Stability and Conflict Detection

**Description:** Ensure proposal diffs are deterministic, accurate, and handle concurrent proposals gracefully with conflict detection.

**Why it matters:** Inconsistent diffs confuse users and cause trust issues. Concurrent proposals without conflict detection can corrupt artifacts. Production systems need reliable, predictable diffs.

**Must deliver:**

- ✅ Standardized diff format (unified diff or structured JSON)
- ✅ Deterministic diff generation (same changes → identical diff every time)
- ✅ Whitespace/formatting consistency (ignore insignificant changes)
- ✅ Concurrent proposal detection (multiple proposals to same artifact)
- ✅ Conflict detection before apply (has artifact changed since proposal created?)
- ✅ Diff preview accuracy (preview matches actual apply result)
- ✅ Line-level accuracy (exact line numbers, context lines)

**Acceptance criteria:**

- [ ] Same artifact changes generate identical diff 100% of time
- [ ] Whitespace-only changes don't generate diff noise
- [ ] Concurrent proposals detected: API returns `409 Conflict` if artifact changed
- [ ] Diff preview matches apply result: integration test verifies byte-for-byte match
- [ ] Line numbers in diff match actual file lines (off-by-one errors caught)
- [ ] Context lines (3 before/after) included in unified diff format
- [ ] Diff determinism tested: 1000 iterations of same change → identical output

**API/interfaces involved:**

- `POST /api/v1/projects/{key}/proposals` - Create proposal (includes diff generation)
- `GET /api/v1/projects/{key}/proposals/{id}/preview` - Preview diff before apply
- `POST /api/v1/projects/{key}/proposals/{id}/apply` - Apply with conflict check

**Mapped to issue:**

- BE-18: Enhanced cross-artifact audit rules + diff stability (backend) (#TBD)

**Validation:**

```bash
# Test diff determinism
for i in {1..100}; do
  curl -X POST http://localhost:8000/api/v1/projects/PROJ-001/proposals \
    -d '{"artifactId":"pmp-001","changes":{...}}' > diff-$i.json
done
# Verify all diffs identical
md5sum diff-*.json | awk '{print $1}' | sort -u | wc -l
# Should output: 1 (all MD5 hashes identical)

# Test concurrent proposal detection
curl -X POST .../proposals -d '{"artifactId":"pmp-001",...}' # Proposal A
curl -X PATCH .../artifacts/pmp-001 -d '{...}' # Direct edit (changes artifact)
curl -X POST .../proposals/{A}/apply # Should fail with 409 Conflict
```

**Testing requirements:**

- Unit tests: Diff generation algorithms, whitespace handling, conflict detection logic
- Integration tests: Concurrent proposals, preview vs. apply accuracy
- E2E tests: Full proposal workflow with conflict scenarios
- Property-based tests: Diff determinism across random inputs (1000+ iterations)

---

### R4: Client E2E Test Suite (Web UI)

**Description:** Comprehensive, deterministic E2E tests for Web UI covering complete user workflows using automation tools (Playwright/Cypress).

**Why it matters:** Frontend bugs often slip through unit tests. E2E tests catch integration issues, visual regressions, and real user workflow problems before production.

**Must deliver:**

- ✅ Client E2E framework (Playwright or Cypress in `tests/e2e/`)
- ✅ Page object model or component testing pattern
- ✅ Full workflow coverage (create project → artifacts → proposals → audit → fix)
- ✅ Multi-artifact navigation and editing scenarios
- ✅ Proposal diff visualization and interaction tests
- ✅ Audit results interaction (click issue → navigate to artifact field)
- ✅ Error state testing (network failures, API errors, validation failures)
- ✅ Visual regression testing for key screens
- ✅ CI integration (headless mode, screenshot capture on failure)

**Acceptance criteria:**

- [ ] E2E framework configured in `tests/e2e/` with Playwright or Cypress
- [ ] Page objects for: ProjectView, ArtifactEditor, ProposalList, ProposalReviewModal, AuditViewer
- [ ] Full workflow test: login → create project → generate PMP/RAID → edit → create proposal → review → apply → audit → fix
- [ ] Proposal workflow test: create manual proposal → review diff → apply → verify artifact updated
- [ ] Audit interaction test: run audit → click error → navigate to field → fix → re-audit
- [ ] Error recovery test: simulate network failure → retry → success
- [ ] Visual regression: Capture screenshots of 10+ key screens, detect pixel diffs
- [ ] Tests run reliably in CI (5 consecutive passes)
- [ ] Test execution time < 10 minutes for full suite
- [ ] `tests/README.md` documents Web UI E2E setup, dependencies, CI integration

**API/interfaces involved:**

- All Web UI components (ProjectView, ArtifactEditor, ProposalList, etc.)
- API client integration
- Browser automation (Playwright/Cypress)

**Mapped to issue:**

- UX-17: TUI-driven client E2E test suite (client) (#TBD in AI-Agent-Framework-Client)

**Validation:**

```bash
# Run client E2E tests locally
cd _external/AI-Agent-Framework-Client
npm run test:e2e

# Run in CI mode (headless)
npm run test:e2e:ci

# Check visual regressions
npm run test:e2e:visual

# Check test stability (5 runs)
for i in {1..5}; do npm run test:e2e || exit 1; done
```

**Testing requirements:**

- E2E tests: Full user workflows end-to-end
- Visual regression: Baseline screenshots with pixel-diff comparison
- Accessibility: Automated ARIA and screen reader checks
- Performance: Lighthouse CI integration

---

### R5: Client-Side Validation and Error Handling

**Description:** Comprehensive client-side validation matching backend schemas, robust error handling with network recovery, and resilient user experience patterns.

**Why it matters:** Users shouldn't submit invalid data that fails server-side. Network issues shouldn't leave users in ambiguous states. Production UIs must handle all error scenarios gracefully.

**Must deliver:**

- ✅ Client-side validation matching backend Pydantic schemas
- ✅ Real-time validation feedback (instant, as user types)
- ✅ Prevent invalid form submissions (disabled submit buttons)
- ✅ Validation error aggregation (show all errors at once)
- ✅ Network error recovery (auto-retry with exponential backoff)
- ✅ API error response handling (user-friendly messages, not raw JSON)
- ✅ Optimistic updates with rollback (instant UI update, revert on failure)
- ✅ Loading states and skeletons (avoid blank screens)
- ✅ Global error boundary (catch React errors, show fallback UI)
- ✅ Unsaved changes warning (browser navigation protection)
- ✅ Confirmation dialogs for destructive actions (delete artifact, reject proposal)
- ✅ Keyboard navigation support (tab order, escape to cancel)
- ✅ Accessibility improvements (ARIA labels, screen reader announcements)

**Acceptance criteria:**

- [ ] All forms validate against backend schemas (shared validation logic)
- [ ] Real-time validation: Type invalid email → error shown immediately
- [ ] Submit button disabled when form has validation errors
- [ ] Network error: API call fails → auto-retry 3x with backoff → show error toast
- [ ] Optimistic update: Save artifact → UI updates instantly → if fails, revert + show error
- [ ] Loading skeletons: Artifact loading → show skeleton UI, not blank screen
- [ ] Global error boundary: React error → show "Something went wrong" page + error details
- [ ] Unsaved changes: Navigate away with unsaved form → confirmation dialog
- [ ] Destructive action: Delete artifact → confirmation dialog required
- [ ] Keyboard navigation: Tab through form, Enter to submit, Escape to cancel
- [ ] Accessibility audit: Lighthouse accessibility score ≥ 90
- [ ] Screen reader: All interactive elements announced correctly

**API/interfaces involved:**

- Form validation logic (shared with backend schemas)
- API client error handling (axios interceptors or similar)
- React error boundaries
- Browser navigation APIs (`beforeunload` event)

**Mapped to issue:**

- UX-18: Client-side validation and error handling hardening (client) (#TBD in AI-Agent-Framework-Client)

**Validation:**

```bash
# Run validation tests
cd _external/AI-Agent-Framework-Client
npm run test -- ValidationForm

# Test network error recovery
# (In browser DevTools: Network tab → Throttle to "Offline")
# Create proposal → expect retry UI → restore network → success

# Test accessibility
npm run lighthouse:a11y
# Should report score ≥ 90

# Test keyboard navigation
# (Manual: Tab through form, verify logical order, Escape cancels)
```

**Testing requirements:**

- Unit tests: Validation logic, error handlers, utility functions
- Integration tests: API error scenarios, network failure simulation
- E2E tests: Error recovery workflows, unsaved changes warning
- Accessibility tests: Automated ARIA checks, screen reader compatibility

---

### R6: CI Quality Gates and Documentation Enforcement

**Description:** Comprehensive CI quality gates for both backend and client that enforce testing, documentation, coverage, code quality, and performance standards.

**Why it matters:** Without CI gates, code quality degrades over time. Missing tests, outdated docs, and low coverage accumulate technical debt. Gates ensure every PR meets production standards.

**Must deliver:**

#### Backend CI Gates:

- ✅ All tests pass (unit + integration + E2E)
- ✅ Test coverage threshold (80%+ for new code, coverage diff check)
- ✅ No missing tests for new features (detect new code without tests)
- ✅ Documentation completeness check (`tests/README.md` current)
- ✅ API documentation complete (OpenAPI/Swagger up-to-date)
- ✅ Linting and formatting checks (black, flake8)
- ✅ Security vulnerability scanning (bandit, safety)
- ✅ Test execution time monitoring (alert if > 10min)
- ✅ Flaky test detection (track intermittent failures)

#### Client CI Gates:

- ✅ All tests pass (unit + integration + E2E)
- ✅ Test coverage threshold (80%+ for components, coverage diff check)
- ✅ No missing tests for new components (detect new files without tests)
- ✅ Build succeeds without warnings
- ✅ Bundle size limits enforced (main bundle < 500KB gzipped)
- ✅ Linting and formatting checks (ESLint, Prettier)
- ✅ TypeScript strict mode (if applicable)
- ✅ Lighthouse score thresholds (performance ≥ 80, accessibility ≥ 90)
- ✅ No console errors in production build
- ✅ Visual regression baseline updates (approve before merge)

**Acceptance criteria:**

- [ ] CI configuration files: `.github/workflows/ci-backend.yml` and `ci-client.yml`
- [ ] Backend: PR fails if coverage delta < 80% for changed files
- [ ] Backend: PR fails if `tests/README.md` out of sync with test structure
- [ ] Backend: PR fails if new files added without corresponding test files
- [ ] Backend: OpenAPI spec auto-generated and validated on every PR
- [ ] Client: PR fails if bundle size exceeds 500KB gzipped
- [ ] Client: PR fails if Lighthouse performance score < 80
- [ ] Client: PR fails if new components added without tests
- [ ] Both: Clear failure messages with remediation steps (not just "failed")
- [ ] Both: Flaky test tracker (report intermittent failures to team)
- [ ] Documentation validation: ADRs required for major architectural changes

**API/interfaces involved:**

- `.github/workflows/` - GitHub Actions configuration
- Coverage tools: `pytest-cov` (backend), `vitest coverage` (client)
- Linters: `black`, `flake8`, `ESLint`, `Prettier`
- Security: `bandit`, `safety`, `npm audit`
- Performance: Lighthouse CI

**Mapped to issues:**

- BE-19: CI quality gates + documentation enforcement (backend) (#TBD)
- UX-19: Client CI quality gates + documentation (client) (#TBD in AI-Agent-Framework-Client)

**Validation:**

```bash
# Backend: Simulate CI locally
pytest --cov=apps/api --cov-report=term-missing --cov-fail-under=80
python -m black apps/api/ --check
python -m flake8 apps/api/
bandit -r apps/api/

# Client: Simulate CI locally
cd _external/AI-Agent-Framework-Client
npm run lint
npm run test -- --coverage --coverageThreshold='{"global":{"lines":80}}'
npm run build # Should have no warnings
npm run lighthouse:ci

# Check documentation sync
# (Script checks if tests/README.md mentions all test files)
python scripts/check_test_docs.py
```

**Testing requirements:**

- CI pipeline tests: Validate gate logic (mock scenarios)
- Documentation checker tests: Detect out-of-sync docs
- Coverage validation tests: Calculate diffs correctly
- Integration: Run full CI locally before pushing

---

## Requirements Traceability Matrix

| Requirement                    | Backend Issues | Backend Files                                                       | Client Issues | Client Files                                                             | Tests                                                    |
| ------------------------------ | -------------- | ------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------ | -------------------------------------------------------- |
| R1: TUI E2E Suite              | #TBD (BE-17)   | `tests/e2e/tui/`, `tests/helpers/`, `tests/fixtures/`               | N/A           | N/A                                                                      | `tests/e2e/tui/workflow_spine_test.py`, etc.             |
| R2: Enhanced Audit Rules       | #TBD (BE-18)   | `apps/api/services/audit_service.py`, `domain/audit/rules.py`       | N/A           | N/A                                                                      | `tests/unit/test_audit_rules.py`, `tests/integration/`   |
| R3: Diff Stability             | #TBD (BE-18)   | `apps/api/services/proposal_service.py`, `domain/proposals/diff.py` | N/A           | N/A                                                                      | `tests/unit/test_diff_generation.py`, property tests     |
| R4: Client E2E Suite           | N/A            | N/A                                                                 | #TBD (UX-17)  | `tests/e2e/`, `tests/pages/`, `playwright.config.ts`                     | `tests/e2e/full_workflow_spec.ts`, visual regression     |
| R5: Client Validation & Errors | N/A            | N/A                                                                 | #TBD (UX-18)  | `src/validation/`, `src/utils/errorHandling.ts`, `src/hooks/useRetry.ts` | `tests/unit/`, `tests/integration/`, E2E error scenarios |
| R6: CI Gates (Backend)         | #TBD (BE-19)   | `.github/workflows/ci-backend.yml`, `scripts/check_test_docs.py`    | N/A           | N/A                                                                      | CI pipeline validation, documentation checker            |
| R6: CI Gates (Client)          | N/A            | N/A                                                                 | #TBD (UX-19)  | `.github/workflows/ci-client.yml`, `lighthouse-config.js`                | CI pipeline validation, bundle size tests, Lighthouse CI |

---

## Implementation Order & Dependencies

### Phase 1: Testing Infrastructure (Weeks 1-2)

**Backend:**

- Week 1: Issue BE-17 (TUI E2E framework) - 1 dev
  - TUI automation helpers, test fixtures, data factories
  - First E2E scenario (workflow spine)
  - CI integration

- Week 2: Issue BE-17 (TUI E2E scenarios) - 1 dev
  - Proposal workflow test
  - Audit fix cycle test
  - Determinism validation

**Client:**

- Week 1-2: Issue UX-17 (Client E2E framework) - 1 dev
  - Playwright/Cypress setup
  - Page object model
  - Full workflow E2E test
  - Visual regression setup

**Deliverable:** E2E test infrastructure operational, initial scenarios passing

---

### Phase 2: Quality Hardening (Weeks 3-4)

**Backend:**

- Week 3: Issue BE-18 (Audit rules + diff stability) - 1 dev
  - Cross-reference validation
  - Date consistency checks
  - Owner validation
  - Diff determinism

- Week 4: Issue BE-18 (Advanced audit + conflict detection) - 1 dev
  - Dependency cycle detection
  - Completeness scoring
  - Concurrent proposal handling
  - Bulk audit

**Client:**

- Week 3-4: Issue UX-18 (Validation + error handling) - 1 dev
  - Client-side validation framework
  - Network error recovery
  - Optimistic updates
  - Error boundaries
  - Accessibility improvements

**Deliverable:** Robust validation, error handling, and audit capabilities

---

### Phase 3: CI Gates & Documentation (Week 5)

**Backend:**

- Week 5: Issue BE-19 (CI quality gates) - 1 dev
  - Coverage enforcement
  - Documentation validation
  - Security scanning
  - Performance monitoring

**Client:**

- Week 5: Issue UX-19 (Client CI gates) - 1 dev
  - Bundle size limits
  - Lighthouse CI
  - Visual regression automation
  - Test coverage enforcement

**Deliverable:** Full CI/CD pipeline with quality gates enforced

---

### Total Estimated Time: 5 weeks (with 2-3 devs)

- **Concurrent work:** Backend + Client E2E (Weeks 1-2)
- **Concurrent work:** Backend audit + Client validation (Weeks 3-4)
- **Concurrent work:** Backend CI + Client CI (Week 5)

---

## Out of Scope for Step 3

These features are explicitly **NOT included** in Step 3 (deferred to Step 4 or later):

1. **Performance Optimization:**
   - Caching strategies
   - Database indexing
   - API response time optimization
   - Frontend bundle splitting optimization

2. **Advanced Audit Features:**
   - Machine learning for anomaly detection
   - Predictive analytics for project risk
   - Custom audit dashboards

3. **Advanced Error Recovery:**
   - Offline mode with local storage
   - Conflict resolution UI for concurrent edits
   - Undo/redo functionality

4. **Production Deployment:**
   - Kubernetes manifests
   - Cloud provider integrations
   - Monitoring and alerting setup
   - Backup and disaster recovery

5. **User Management:**
   - Authentication and authorization
   - Role-based access control (RBAC)
   - Multi-tenancy support

**Rationale:** Step 3 focuses on **quality and testing**, not new features or production operations. Features above are valuable but separate from core testing/hardening goals.

---

## Success Criteria

### Step 3 Complete When:

#### Backend:

- ✅ All 3 backend issues implemented and merged (#BE-17, #BE-18, #BE-19)
- ✅ TUI E2E suite covers all workflows and runs reliably in CI
- ✅ Enhanced audit rules validate cross-artifact relationships
- ✅ Proposal diffs are deterministic and stable
- ✅ Concurrent proposals handled with conflict detection
- ✅ CI gates enforce 80%+ coverage for all new code
- ✅ Documentation validation prevents stale docs
- ✅ All tests passing in CI (unit + integration + E2E)
- ✅ `tests/README.md` updated with Step 3 content

#### Client:

- ✅ All 3 client issues implemented and merged (#UX-17, #UX-18, #UX-19)
- ✅ Web UI E2E suite covers all user workflows
- ✅ Client-side validation matches backend schemas
- ✅ Network errors handled gracefully with retry
- ✅ Accessibility score ≥ 90 (Lighthouse)
- ✅ Bundle size < 500KB gzipped
- ✅ CI gates enforce 80%+ coverage for all new components
- ✅ Visual regression tests prevent UI breakage
- ✅ All tests passing in CI (unit + integration + E2E)
- ✅ `tests/README.md` updated with client E2E content

#### Integration:

- ✅ Backend + Client E2E tests run together in CI
- ✅ No flaky tests (5 consecutive passes required)
- ✅ Test execution time acceptable (backend < 5min, client < 10min)
- ✅ CI fails appropriately for missing tests or docs
- ✅ Both repos deployable independently with quality gates enforced

---

## Frequently Asked Questions

**Q:** Why is Step 3 only 6 issues when Step 2 had 18?

**A:** Step 3 focuses on **quality infrastructure** (testing, CI gates), not new features. Each issue is larger in scope (M/L size) because they involve cross-cutting concerns (E2E tests touch all features). Step 2 decomposed features into many small issues; Step 3 has fewer, broader issues.

---

**Q:** Can we skip E2E tests and rely on unit/integration tests?

**A:** No. E2E tests catch integration issues that unit tests miss (component interactions, workflow ordering, real user scenarios). Production systems require E2E coverage. This is non-negotiable for Step 3 completion.

---

**Q:** Should TUI E2E tests use the same framework as client E2E tests?

**A:** No. TUI E2E uses Python-based TUI automation (likely `pexpect` or similar for terminal interaction). Client E2E uses Playwright/Cypress for browser automation. Different tools for different interfaces.

---

**Q:** What if CI gates are too strict and slow down development?

**A:** Gates should be **strict but fast**. Optimize test execution time, parallelize CI jobs, and cache dependencies. If gates are too slow, improve performance; don't lower standards. Fast feedback requires investment in CI infrastructure.

---

**Q:** How do we handle flaky tests?

**A:** Flaky tests are **bugs** and must be fixed. Options: (1) Improve test determinism (proper waits, not sleeps), (2) Add retry logic for genuinely intermittent failures (network), (3) Quarantine flaky tests (mark as `@flaky`, investigate later). Never ignore flaky tests.

---

**Q:** Should all Step 3 issues be worked on sequentially or in parallel?

**A:** **Parallel when possible:**

- Backend BE-17 (TUI E2E) + Client UX-17 (Web E2E) can be concurrent (Weeks 1-2)
- Backend BE-18 (Audit + Diff) + Client UX-18 (Validation + Errors) can be concurrent (Weeks 3-4)
- Backend BE-19 (CI gates) + Client UX-19 (Client CI) can be concurrent (Week 5)

**Sequential dependencies:**

- CI gates (BE-19, UX-19) should come **after** E2E tests are working (BE-17, UX-17)
- Don't create CI gates before you have comprehensive tests to validate

---

**Q:** What coverage percentage is acceptable for Step 3?

**A:** **Minimum 80% for all new code** (measured by coverage diff). Existing code doesn't need retroactive coverage, but all Step 3 work must meet 80% threshold. Stretch goal: 90%+ for critical paths (audit rules, diff generation, validation logic).

---

## Validation Commands

### Backend Validation

```bash
# Activate environment
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run TUI E2E tests
pytest tests/e2e/tui/ -v

# Check coverage
pytest --cov=apps/api --cov-report=term-missing --cov-fail-under=80

# Run linters
python -m black apps/api/ --check
python -m flake8 apps/api/

# Run security scans
bandit -r apps/api/
safety check

# Validate test documentation
python scripts/check_test_docs.py

# Simulate CI locally
./scripts/ci_backend.sh
```

### Client Validation

```bash
# Navigate to client
cd _external/AI-Agent-Framework-Client

# Install dependencies
npm install

# Run all tests
npm run test

# Run E2E tests
npm run test:e2e

# Check coverage
npm run test -- --coverage --coverageThreshold='{"global":{"lines":80}}'

# Run linters
npm run lint

# Build (should have no warnings)
npm run build

# Run Lighthouse audit
npm run lighthouse:ci

# Check bundle size
npm run build:stats

# Validate test documentation
npm run validate:test-docs

# Simulate CI locally
./scripts/ci_client.sh
```

---

## Appendix A: Issue Template Checklist

Each Step 3 issue must include:

- [ ] **Goal** (1-2 sentences, what and why)
- [ ] **Scope** (In/Out, clear boundaries)
- [ ] **Acceptance Criteria** (checkboxes, testable)
- [ ] **API Contract / Interfaces** (if applicable)
- [ ] **Technical Approach** (architecture, patterns, tools)
- [ ] **Testing Requirements** (unit, integration, E2E)
- [ ] **Documentation Updates** (which files, what content)
- [ ] **Dependencies** (other issues, external libs)
- [ ] **Estimated Effort** (S/M/L, 1-5 days)
- [ ] **Labels** (step:3, backend/client, tests/e2e, ci/cd)

---

## Appendix B: DDD Architecture for Testing

**Testing infrastructure follows DDD principles:**

- **Test Domain Layer** (`tests/helpers/`, `tests/fixtures/`)
  - Test data factories (project, artifact, proposal builders)
  - Test utilities (assertion helpers, data generators)
  - Test fixtures (reusable test data)

- **Test Service Layer** (`tests/e2e/tui/`, `tests/e2e/`)
  - TUI automation service (command execution, output parsing)
  - Web automation service (Playwright page objects)
  - API test client (http request wrappers)

- **Test Infrastructure** (`tests/unit/`, `tests/integration/`)
  - Unit test framework (pytest)
  - Integration test setup (database, API server)
  - E2E test harness (TUI automation, browser automation)

**Key principles:**

- **SRP:** Each test helper does ONE thing
- **DRY:** Shared logic in fixtures/helpers, not copy-paste
- **Type Safety:** Test data factories return typed objects
- **Determinism:** No random data in tests (use seeds), no sleep-based waits

---

**Document Version:** 1.0  
**Date:** 2026-02-01  
**Status:** DRAFT - Ready for Review  
**Total Requirements:** 6 core requirements  
**Total Issues:** 6 (3 backend + 3 client)  
**Estimated Duration:** 5 weeks (with 2-3 devs)
