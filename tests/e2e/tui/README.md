# TUI E2E Test Scenarios

This directory contains end-to-end tests for the TUI (Terminal User Interface) client. These tests validate complete workflows from project creation through audit verification.

## Overview

The TUI E2E tests use automated command execution to test the full feature spine without manual interaction. Tests are deterministic, CI-friendly, and designed for fast feedback.

## Test Architecture

```
tests/e2e/tui/
├── test_workflow_spine.py      # Core workflow from project to audit
├── test_proposal_workflow.py   # Proposal lifecycle (manual + AI)
└── test_audit_fix_cycle.py     # Audit → fix → re-audit cycles
```

Supporting infrastructure:

```
tests/
├── helpers/
│   └── tui_automation.py       # TUI command execution service
├── fixtures/
│   ├── factories.py            # Test data builders
│   └── fixtures.py             # Pytest fixtures
└── unit/
    ├── test_tui_automation.py  # Unit tests for automation
    └── test_factories.py       # Unit tests for factories
```

## Running Tests

### Prerequisites

Ensure Python environment is set up:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Run All TUI E2E Tests

```bash
pytest tests/e2e/tui/ -v
```

### Run Specific Scenario

```bash
# Workflow spine test only
pytest tests/e2e/tui/test_workflow_spine.py -v

# Proposal workflow test only
pytest tests/e2e/tui/test_proposal_workflow.py -v

# Audit fix cycle test only
pytest tests/e2e/tui/test_audit_fix_cycle.py -v
```

### Run in CI Mode (Headless)

```bash
TERM=xterm-256color pytest tests/e2e/tui/ --tb=short -v
```

### Run Specific Test

```bash
pytest tests/e2e/tui/test_workflow_spine.py::test_workflow_spine_complete -v
```

### Run Without API Server

Tests will automatically start the API server if not running. To use an existing server:

```bash
API_BASE_URL=http://localhost:8000 pytest tests/e2e/tui/ -v
```

### Performance Testing

```bash
# Run performance-tagged tests
pytest tests/e2e/tui/ -v -m "not slow"

# Include slow tests
pytest tests/e2e/tui/ -v
```

## Test Scenarios

### 1. Workflow Spine Test

**File:** `test_workflow_spine.py`

**Purpose:** Validates the complete workflow from project creation to audit verification.

**Scenario:**

1. Create project TEST-SPINE
2. Generate PMP artifact from template
3. Generate RAID artifact from template
4. Verify artifacts exist and are retrievable
5. Edit PMP artifact (add scope section)
6. Create proposal for changes
7. Review and apply proposal
8. Run audit on project
9. Verify audit passes with no errors

**Validation:**

- Project is created and appears in list
- Artifacts are generated with correct structure
- Proposals are applied and artifacts updated
- Audit runs successfully and passes
- All operations complete within performance targets

**Current Status:** Basic project operations implemented. Artifact and proposal operations are placeholders pending TUI command implementation.

### 2. Proposal Workflow Test

**File:** `test_proposal_workflow.py`

**Purpose:** Validates proposal creation, review, and apply/reject workflows.

**Scenario:**

1. Create test project
2. Create manual proposal with specific changes
3. Create AI-assisted proposal
4. Review proposals (view diffs)
5. Apply first proposal
6. Reject second proposal
7. Verify artifact updates and audit events

**Validation:**

- Both manual and AI proposals work correctly
- Diffs are properly formatted and displayed
- Apply updates artifacts correctly
- Reject leaves artifacts unchanged
- All actions are logged in audit trail

**Current Status:** Placeholder tests pending proposal TUI commands.

### 3. Audit Fix Cycle Test

**File:** `test_audit_fix_cycle.py`

**Purpose:** Validates audit detection, issue fixing, and convergence to clean state.

**Scenario:**

1. Create project with artifacts
2. Run initial audit (detects issues)
3. Identify specific issues (missing fields, invalid refs)
4. Create proposals to fix issues
5. Apply proposals
6. Re-run audit
7. Verify audit passes (no errors)

**Validation:**

- Audit detects missing required fields
- Audit detects invalid cross-references
- Fixes resolve detected issues
- Re-audit confirms clean state
- Multiple iterations converge correctly

**Current Status:** Placeholder tests pending audit TUI commands.

## Test Infrastructure

### TUI Automation Service

**File:** `tests/helpers/tui_automation.py`

Provides programmatic TUI command execution:

```python
from tests.helpers.tui_automation import TUIAutomation, TUIAssertions

# Initialize automation
tui = TUIAutomation(api_base_url="http://localhost:8000")

# Execute command
result = tui.execute_command("projects list")

# Assert on results
assertions = TUIAssertions()
assertions.assert_success(result)
assertions.assert_contains(result, "TEST-001")
```

**Key Features:**

- Deterministic execution (no sleep-based timing)
- Timeout handling with retries
- JSON output parsing
- Regex pattern matching
- Performance measurement

### Test Data Factories

**File:** `tests/fixtures/factories.py`

Fluent builders for creating test data:

```python
from tests.fixtures.factories import ProjectFactory, ProposalFactory

# Create project
project = (ProjectFactory()
          .with_key("TEST-001")
          .with_name("My Test Project")
          .build())

# Create proposal
proposal = (ProposalFactory()
           .with_project("TEST-001")
           .for_artifact("art-123")
           .with_changes("Add scope")
           .build())
```

**Available Factories:**

- `ProjectFactory` - Test projects
- `ArtifactFactory` - Test artifacts
- `ProposalFactory` - Test proposals
- `RAIDItemFactory` - Test RAID items
- `AuditResultFactory` - Test audit results

### Pytest Fixtures

**File:** `tests/fixtures/fixtures.py`

Reusable test fixtures:

- `api_server` - Starts/manages API server
- `tui` - TUIAutomation instance
- `assertions` - TUIAssertions helper
- `project_factory` - ProjectFactory instance
- `test_project` - Creates and cleans up test project

## Writing New Tests

### 1. Use TUI Automation Service

```python
def test_my_scenario(tui: TUIAutomation, assertions: TUIAssertions):
    result = tui.execute_command("projects list")
    assertions.assert_success(result)
    assertions.assert_contains(result, "expected text")
```

### 2. Use Test Data Factories

```python
def test_with_factory(project_factory: ProjectFactory):
    project = project_factory.with_key("TEST-NEW").build()
    # Use project data
```

### 3. Ensure Deterministic Execution

❌ **Bad:** Using sleep for timing

```python
time.sleep(2)  # Wait for operation
```

✅ **Good:** Using expect_output with timeout

```python
tui.expect_output("projects list", "TEST-001", timeout=5.0)
```

### 4. Clean Up Resources

```python
def test_with_cleanup(tui: TUIAutomation, project_factory: ProjectFactory):
    project = project_factory.build()
    project_key = project["key"]

    # Create project
    tui.execute_command(f"projects create --key {project_key}")

    # Use project...

    # Always cleanup
    tui.cleanup_project(project_key)
```

Or use the `test_project` fixture:

```python
def test_with_fixture(test_project: str, tui: TUIAutomation):
    # test_project is already created and will be cleaned up
    result = tui.execute_command(f"projects get --key {test_project}")
```

### 5. Mark Test Attributes

```python
@pytest.mark.e2e
def test_basic_workflow(...):
    """Fast E2E test."""
    pass

@pytest.mark.e2e
@pytest.mark.slow
def test_comprehensive_workflow(...):
    """Comprehensive but slower E2E test."""
    pass
```

## Performance Targets

- **Project operations:** < 2s
- **Artifact operations:** < 3s
- **Proposal operations:** < 3s
- **Audit operations:** < 5s
- **Full test suite:** < 5 minutes

## CI Integration

Tests run automatically on push/PR via `.github/workflows/ci-backend.yml`:

```yaml
jobs:
  test-e2e:
    runs-on: ubuntu-latest
    steps:
      - name: Run TUI E2E tests
        env:
          TERM: xterm-256color
        run: |
          pytest tests/e2e/tui/ -v --tb=short --maxfail=1
```

## Debugging Tests

### View Detailed Output

```bash
pytest tests/e2e/tui/ -v -s
```

### Run Single Test with Full Traceback

```bash
pytest tests/e2e/tui/test_workflow_spine.py::test_workflow_spine_complete -vv --tb=long
```

### Enable Debug Logging

```bash
pytest tests/e2e/tui/ -v --log-cli-level=DEBUG
```

### Inspect Failed Command Output

Test assertions include stdout/stderr in failure messages:

```
AssertionError: Command should succeed
Stdout: [command output]
Stderr: [error output]
```

## Known Limitations

1. **TUI Command Availability:** Some tests are placeholders pending implementation of:
   - Artifact management commands
   - Proposal commands
   - Audit commands

2. **Project Cleanup:** TUI doesn't currently have delete commands, so cleanup is best-effort.

3. **Parallel Execution:** Tests are not yet optimized for parallel execution due to shared API server.

## CI Integration

TUI E2E tests run automatically in GitHub Actions on push/PR.

**Workflow:** `.github/workflows/ci.yml`

**Steps:**

1. Setup Python 3.12 environment
2. Install dependencies from `requirements.txt`
3. Configure git for test commits
4. Run unit tests with coverage
5. Run integration tests with coverage
6. Run backend E2E tests (non-TUI)
7. **Run TUI E2E tests** (`pytest tests/e2e/tui/`)

**CI Configuration:**

```yaml
- name: Run TUI E2E tests
  if: hashFiles('tests/e2e/tui/**') != ''
  run: PYTHONPATH=$GITHUB_WORKSPACE TERM=xterm-256color pytest -v tests/e2e/tui --tb=short --maxfail=1
```

**CI Requirements:**

- Tests must complete in < 5 minutes (current: ~12 seconds)
- All tests must pass (13/13 passing)
- Tests must be deterministic (no flaky failures)
- Exit on first failure (`--maxfail=1`) for fast feedback

**Viewing CI Results:**

```bash
# Check PR status
gh pr checks <pr-number>

# View workflow run
gh run view <run-id>

# View failed test logs
gh run view <run-id> --log-failed
```

## Future Enhancements

- [ ] Implement remaining TUI commands (artifacts, proposals, audit)
- [ ] Add parallel test execution support
- [ ] Add test data seeding for faster execution
- [ ] Add snapshot testing for output formats
- [ ] Add mutation testing for robustness
- [ ] Add load testing scenarios

## Support

For issues or questions:

1. Check `tests/README.md` for general test information
2. Review unit tests for infrastructure examples
3. Check CI logs for failure patterns
4. Consult `docs/development.md` for development guidelines
