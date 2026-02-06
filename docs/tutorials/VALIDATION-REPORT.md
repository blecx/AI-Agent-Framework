# Tutorial Validation Report

**Generated:** 2026-02-06 (Phase 3 validation - Issue #144)  
**Status:** ⚠️ Validation Complete with Findings

## Executive Summary

**Issue #144 Phase 3 Validation Results:**

- **Total Tests:** 48 tests with `@pytest.mark.tutorial_validation` marker
- **Passed:** 1 ✅
- **Failed:** 10 ❌
- **Errors:** 20 ⛔
- **Skipped:** 17 ⊙

**Pass Rate:** 2% (1/48 tests executable)

**Critical Finding:** Majority of TUI tests fail due to API connectivity issues and command timeouts. GUI tests fail due to Docker port conflicts. Advanced workflow tests skip due to missing API.

## Test Results by Module

### TUI Basics Tutorials (5 tutorials, 19 tests)

**Status:** ❌ **CRITICAL ISSUES - API Connectivity Failures**

| Test Class | Tests | Passed | Failed | Errors | Issues |
|------------|-------|--------|--------|--------|--------|
| TestTutorial01QuickStart | 3 | 1 | 2 | 0 | Timeouts on `health` command, missing `show` in help |
| TestTutorial02FirstProject | 5 | 0 | 5 | 0 | `--description` flag not supported, timeouts on create |
| TestTutorial03ArtifactWorkflow | 3 | 0 | 0 | 3 | Setup timeouts (project creation hangs) |
| TestTutorial04RAIDManagement | 5 | 0 | 0 | 5 | Setup timeouts (project creation hangs) |
| TestTutorial05FullLifecycle | 2 | 0 | 0 | 2 | Setup timeouts (project creation hangs) |
| Integration Test | 1 | 0 | 1 | 0 | `health` command timeout |

**Key Findings:**
1. **Command Timeouts:** `health` and `projects create` commands timeout after 30s
2. **Missing API Flag:** Tutorial documents `--description` flag which doesn't exist in current TUI
3. **Help Output Mismatch:** `projects --help` doesn't show `show` command (test expects it)
4. **API Dependency:** All tests require running API server at `http://localhost:8000`

**Tutorial Impact:**
- ❌ `docs/tutorials/tui-basics/01-quick-start.md` - Commands timeout
- ❌ `docs/tutorials/tui-basics/02-first-project.md` - Unsupported `--description` flag
- ❌ `docs/tutorials/tui-basics/03-artifact-workflow.md` - Cannot validate (setup fails)
- ❌ `docs/tutorials/tui-basics/04-raid-management.md` - Cannot validate (setup fails)
- ❌ `docs/tutorials/tui-basics/05-full-lifecycle.md` - Cannot validate (setup fails)

### GUI Basics Tutorials (5 tutorials, 10 tests)

**Status:** ⛔ **DOCKER PORT CONFLICT - Cannot Start Test Environment**

| Test Class | Tests | Passed | Failed | Errors | Issues |
|------------|-------|--------|--------|--------|--------|
| TestGUITutorial01WebInterface | 2 | 0 | 0 | 2 | Docker port 8000 already in use |
| TestGUITutorial02ProjectCreation | 2 | 0 | 0 | 2 | Docker port 8000 already in use |
| TestGUITutorial03CommandsProposals | 2 | 0 | 0 | 2 | Docker port 8000 already in use |
| TestGUITutorial04ArtifactBrowsing | 2 | 0 | 0 | 2 | Docker port 8000 already in use |
| TestGUITutorial05WorkflowStates | 2 | 0 | 0 | 2 | Docker port 8000 already in use |

**Key Findings:**
1. **Port Conflict:** Tests require Docker but port 8000 is in use (likely background API server)
2. **Environment Issue:** `docker-compose.yml` version attribute is obsolete (warning)
3. **Previous Success:** Historical data shows these tests passed when run with proper Docker setup

**Tutorial Impact:**
- ⚠️ `docs/tutorials/gui-basics/01-web-interface.md` - Cannot validate (Docker conflict)
- ⚠️ `docs/tutorials/gui-basics/02-project-creation.md` - Cannot validate (Docker conflict)
- ⚠️ `docs/tutorials/gui-basics/03-commands-and-proposals.md` - Cannot validate (Docker conflict)
- ⚠️ `docs/tutorials/gui-basics/04-artifact-browsing.md` - Cannot validate (Docker conflict)
- ⚠️ `docs/tutorials/gui-basics/05-workflow-states.md` - Cannot validate (Docker conflict)

**Note:** These tests have 100% pass rate when Docker environment is properly configured.

### Advanced Workflows Tutorials (3 tutorials, 13 tests + 2 OLD tests)

**Status:** ⊙ **SKIPPED - API Not Running**

| Test Class | Tests | Passed | Failed | Skipped | Issues |
|------------|-------|--------|--------|---------|--------|
| TestTutorial01HybridWorkflow | 6 | 0 | 0 | 6 | API not running, documentation gap on RAID commands |
| TestTutorial02CompleteLifecycle | 3 | 0 | 0 | 3 | API not running |
| TestTutorial03AutomationScripting | 2 | 0 | 0 | 2 | API not running |
| TestActualTUICapabilities | 2 | 0 | 0 | 2 | API not running |
| TestTutorial01/02 (OLD file) | 4 | 0 | 2 | 2 | `--description` flag doesn't exist |

**Key Findings:**
1. **API Dependency:** All tests skip when API is not available
2. **DOCUMENTATION GAP:** Tutorials document TUI commands that don't exist:
   - `python main.py raid add --type risk ...` - NO 'raid' command exists
   - `python main.py artifacts create --type charter ...` - NO 'artifacts create' exists
   - `python main.py workflow update --state Planning` - NO 'workflow' command exists
3. **Reality Check:** Tests validate actual TUI capabilities vs documented capabilities
4. **OLD Tests:** Legacy tests fail due to unsupported `--description` flag

**Tutorial Impact:**
- ⚠️ `docs/tutorials/advanced/01-tui-gui-hybrid.md` - **MAJOR DOCUMENTATION ISSUES**
- ⚠️ `docs/tutorials/advanced/02-complete-iso21500.md` - Commands may not match reality
- ⚠️ `docs/tutorials/advanced/03-automation-scripting.md` - Scripting examples may be incorrect

**Remediation Required:**
- Update tutorials to match actual TUI API (propose/apply workflow)
- OR implement missing TUI commands (raid, artifacts, workflow)
- See test file comments for detailed gap analysis

## Failure Details

### Critical Issues (Blockers)

#### 1. TUI Command Timeouts (10 failed tests)
**Symptom:** Commands hang for 30 seconds then timeout  
**Commands Affected:** `health`, `projects create`  
**Root Cause:** Unknown - API appears to be required but connection issues  
**Tests Affected:**
- `test_health_check` - TIMEOUT
- `test_list_projects` - TIMEOUT (setup)
- `test_show_project` - TIMEOUT (setup)
- `test_project_state` - TIMEOUT (setup)
- `test_delete_project` - TIMEOUT (setup)
- All Tutorial 03, 04, 05 tests - TIMEOUT during setup

**Error Example:**
```
TimeoutError: Command timed out after 30s: 
/home/sw/work/AI-Agent-Framework/.venv/bin/python3.12 
/home/sw/work/AI-Agent-Framework/apps/tui/main.py health
```

**Fix Required:** Investigate why TUI commands hang when API is available

#### 2. Unsupported --description Flag (3 failed tests)
**Symptom:** `projects create --description` returns "No such option"  
**Tests Affected:**
- `test_create_project` (Tutorial 02)
- `test_initiating_phase` (Advanced OLD)
- `test_planning_phase` (Advanced OLD)

**Error Example:**
```
Error: No such option: --description
```

**Fix Required:** Either add `--description` flag or update tutorials to remove it

#### 3. Missing 'show' Command (1 failed test)
**Symptom:** `projects --help` doesn't list `show` command  
**Test Affected:** `test_projects_help`

**Actual Output:**
```
Commands:
  create  Create a new project.
  get     Get project details and state.
  list    List all projects.
```

**Expected:** Should include `show` command (or test should expect `get` instead)

#### 4. Docker Port Conflicts (10 error tests)
**Symptom:** Cannot start Docker environment - port 8000 in use  
**Tests Affected:** All GUI tutorial tests (10 tests)

**Error Example:**
```
Error response from daemon: failed to bind host port 0.0.0.0:8000/tcp: 
address already in use
```

**Fix Required:** Stop background API servers before running Docker-based tests

## How to Use This Report

1. **Pass Rate 100%:** ✅ All GUI tutorial tests passing
2. **Failed Tests:** None in current run
3. **Skipped Tests:** TUI and Advanced tests not yet marked with `tutorial_validation` marker
4. **Next Steps:** Add `@pytest.mark.tutorial_validation` to remaining test files

## Re-running Validation

```bash
# Run all tutorial validation tests
cd /home/sw/work/AI-Agent-Framework
source .venv/bin/activate
pytest -m tutorial_validation -v --tb=short

# Run with duration report
pytest -m tutorial_validation --durations=0

# Run specific tutorial module
pytest tests/e2e/tutorial/test_gui_basics.py -v
```

## Manual Tutorial Validation

For manual validation of tutorial content:
1. Follow each tutorial step-by-step
2. Compare actual output with expected output in `expected-outputs/`
3. Document discrepancies in GitHub issues
4. Update tutorials or expected outputs as needed

### Documentation Gaps (MAJOR)

#### Advanced Tutorials Document Non-Existent Commands

**Issue:** Tutorials describe TUI commands that don't exist in current implementation

**Documented (WRONG):**
```bash
# Tutorial 01: TUI/GUI Hybrid
python main.py raid add --type risk --description "Server downtime"

# Tutorial 01: TUI/GUI Hybrid  
python main.py artifacts create --type charter --name "Project Charter"

# Tutorial 02: Complete ISO 21500
python main.py workflow update --state Planning
```

**Reality (CORRECT):**
- NO `raid` command - use API propose/apply workflow
- NO `artifacts create` - use `commands propose --command generate_artifact`
- NO `workflow` command - use propose/apply workflow

**Tests Document This:**
- `test_raid_operations_not_supported` - SKIPPED with documentation gap note
- `test_artifacts_create_not_supported` - SKIPPED with documentation gap note

**Impact:** Advanced tutorials (01-03) are **misleading and unusable**

**Fix Options:**
- **Option A (Recommended):** Update tutorials to show actual TUI/API workflow
- **Option B:** Implement the missing TUI commands

---

## Known Issues

### Blocker Issues (Must Fix)

1. **BLOCKER-1:** TUI command timeouts (health, projects create) - 10 failed tests
   - Severity: HIGH
   - Impact: All TUI tutorials unusable
   - Status: Needs investigation

2. **BLOCKER-2:** Missing `--description` flag in `projects create`
   - Severity: HIGH  
   - Impact: Tutorial 02 (First Project) incorrect
   - Status: Needs decision (add flag or update tutorial)

3. **BLOCKER-3:** Docker port conflicts prevent GUI test execution
   - Severity: MEDIUM
   - Impact: Cannot validate GUI tutorials in current environment
   - Status: Operational issue (stop background servers before tests)

### Documentation Issues (Must Update)

4. **DOC-GAP-1:** Advanced tutorials document non-existent TUI commands
   - Severity: CRITICAL
   - Impact: Advanced tutorials 01-03 completely unusable
   - Status: Tutorials need rewriting or TUI needs new commands

5. **DOC-GAP-2:** Missing `show` command or incorrect test expectation
   - Severity: LOW
   - Impact: Help output doesn't match test expectations
   - Status: Need to verify if `show` should exist or test should use `get`

### Minor Warnings (Non-blocking)

1. **Pytest config warning:** Unknown config option `env` in pytest.ini
   - Impact: Cosmetic only, does not affect test execution
   - Status: Can be ignored or cleaned up in future refactor

2. **Pydantic field shadowing:** Field name "schema" in Template models shadows BaseModel attribute
   - Impact: Cosmetic warning, no functional impact
   - Location: `apps/api/domain/templates/models.py` (lines 14, 65, 78)
   - Status: Low priority cleanup

## Workarounds

No workarounds needed - all tests passing successfully.

## Test Coverage Analysis

### Tutorial Coverage Status

| Tutorial Category | Tutorials | Tests | Status | Pass Rate |
|-------------------|-----------|-------|--------|-----------|
| TUI Basics | 5 | 19 | ❌ Failed | 5% (1/19) |
| GUI Basics | 5 | 10 | ⛔ Error | 0% (port conflict) |
| Advanced Workflows | 3 | 13 | ⊙ Skipped | N/A (API missing) |
| **TOTAL** | **13** | **48** | **❌ Critical** | **2% (1/48)** |

### Detailed Tutorial Status

#### TUI Basics: 5 tutorials, 19 tests - ❌ FAILED
- ❌ 01-quick-start.md - Timeouts on basic commands
- ❌ 02-first-project.md - Unsupported flags
- ❌ 03-artifact-workflow.md - Cannot test (setup fails)
- ❌ 04-raid-management.md - Cannot test (setup fails)
- ❌ 05-full-lifecycle.md - Cannot test (setup fails)

#### GUI Basics: 5 tutorials, 10 tests - ⛔ ENVIRONMENT ERROR
- ⚠️ 01-web-interface.md - Docker conflict
- ⚠️ 02-project-creation.md - Docker conflict
- ⚠️ 03-commands-and-proposals.md - Docker conflict
- ⚠️ 04-artifact-browsing.md - Docker conflict
- ⚠️ 05-workflow-states.md - Docker conflict
- **Note:** Historical data shows 100% pass rate with proper Docker setup

#### Advanced Workflows: 3 tutorials, 13 tests - ⊙ DOCUMENTATION GAP
- ❌ 01-tui-gui-hybrid.md - **MAJOR ISSUES** (documents non-existent commands)
- ⚠️ 02-complete-iso21500.md - Skipped (API required)
- ⚠️ 03-automation-scripting.md - Skipped (API required)

## Recommendations

### Immediate Actions (Week 1)

1. **Fix TUI Command Timeouts (BLOCKER-1)**
   - Debug why `health` and `projects create` hang
   - Check API dependency and connectivity
   - Expected effort: 4-6 hours

2. **Resolve --description Flag (BLOCKER-2)**  
   - Decision: Add flag OR update Tutorial 02
   - If adding flag: Update TUI command parser
   - If removing: Update tutorial docs and tests
   - Expected effort: 2-4 hours

3. **Fix Test Environment (BLOCKER-3)**
   - Update test runner to kill background processes
   - Add pre-test environment cleanup
   - Expected effort: 1-2 hours

### Short-term Actions (Week 2-3)

4. **Update Advanced Tutorials (DOC-GAP-1) - CRITICAL**
   - Rewrite tutorials 01-03 to match actual TUI API
   - Document propose/apply workflow correctly
   - Remove references to non-existent commands
   - Expected effort: 8-12 hours (manual work)

5. **Verify Expected Outputs**
   - After fixes, re-run validation
   - Capture actual outputs
   - Update `expected-outputs/` files
   - Expected effort: 2-3 hours

### Long-term Actions (Future)

6. **Consider Implementing Missing Commands**
   - Evaluate if `raid`, `artifacts`, `workflow` commands should exist
   - If yes, implement as thin wrappers around API
   - Update tutorials accordingly
   - Expected effort: 20-30 hours

7. **Improve Test Reliability**
   - Add retry logic for flaky tests
   - Better timeout handling
   - More informative error messages
   - Expected effort: 4-6 hours

## Action Items for Issue #144 Resolution

- [x] Add `@pytest.mark.tutorial_validation` markers to all test classes
- [x] Run full validation suite
- [x] Document all failures and issues
- [x] Update VALIDATION-REPORT.md with comprehensive findings
- [ ] Create follow-up issues for blockers (BLOCKER-1, BLOCKER-2, BLOCKER-3)
- [ ] Create follow-up issue for documentation gaps (DOC-GAP-1)
- [ ] Update expected-outputs/ after fixes applied

## Validation History

| Date | Total | Passed | Failed/Error | Skipped | Pass Rate | Notes |
|------|-------|--------|--------------|---------|-----------|-------|
| 2026-02-06 (before) | 10 | 10 | 0 | 0 | 100% | GUI tests only (Docker working) |
| 2026-02-06 (Issue #144) | 48 | 1 | 30 | 17 | 2% | Full validation with markers added |

---

## Appendix: Raw Test Output

**Test Command:**
```bash
pytest -m tutorial_validation -v --tb=short
```

**Summary:**
- Platform: Linux Python 3.12.0, pytest-7.4.4
- Duration: 550.10s (9 minutes 10 seconds)
- Selected: 48 tests (586 deselected)
- Results: 1 passed, 10 failed, 20 errors, 17 skipped

**Key Error Patterns:**
1. **Timeout:** `subprocess.TimeoutExpired` after 30 seconds
2. **Port Conflict:** `address already in use` for port 8000
3. **Missing Option:** `No such option: --description`
4. **API Unavailable:** Tests skip with "API not running"

Full test output saved to: `.tmp/validation-run-144.log`

---

*Report generated by: Issue #144 Phase 3 validation*  
*Generated: 2026-02-06*  
*Next: Create follow-up issues for blockers and documentation gaps*
