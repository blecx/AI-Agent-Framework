# TUI E2E Test Suite

Deterministic, non-interactive end-to-end tests for the ISO 21500 AI-Agent Framework TUI (Text User Interface).

## Overview

This test suite validates complete workflows using the TUI CLI:

- **Workflow spine**: Project creation → artifact generation → proposal → apply → audit
- **Proposal workflow**: Manual and AI-assisted proposals, apply/reject actions
- **Audit fix cycle**: Run audit → detect issues → fix via proposals → re-audit → verify clean

## Architecture

```
tests/e2e/tui/
├── conftest.py                     # Pytest fixtures (backend server, TUI automation)
├── test_workflow_spine.py          # Core workflow scenarios
├── test_proposal_workflow.py       # Proposal lifecycle tests
└── test_audit_fix_cycle.py         # Audit and fix cycle tests
```

Supporting infrastructure:

- `tests/helpers/tui_automation.py` - TUI command execution service
- `tests/fixtures/factories.py` - Test data builders (Project, Artifact, Proposal, RAID)

## Running Tests

### Prerequisites

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if not done)
pip install -r requirements.txt
```

### Run All TUI E2E Tests

```bash
pytest tests/e2e/tui/ -v
```

### Run Specific Test File

```bash
pytest tests/e2e/tui/test_workflow_spine.py -v
```

### Run Specific Test

```bash
pytest tests/e2e/tui/test_workflow_spine.py::test_workflow_spine_full_cycle -v
```

### Skip Slow Tests

```bash
pytest tests/e2e/tui/ -v -m "not slow"
```

## Test Data

All test data is generated using deterministic factories:

```python
from fixtures.factories import ProjectFactory, ArtifactFactory

# Create deterministic project
project = ProjectFactory().with_key("TEST-001").with_name("My Project").build()

# Create random but seeded project
project = ProjectFactory().with_seed(12345).build()
```

## Fixtures

### `backend_server` (session scope)

Starts the FastAPI backend on `http://localhost:8000` for the test session. Automatically terminates after all tests complete.

### `tui` (function scope)

Provides `TUIAutomation` instance for executing TUI commands.

**Usage:**

```python
def test_example(tui):
    result = tui.create_project(key="TEST-01", name="Example")
    assert result.success
    assert "TEST-01" in result.stdout
```

### `unique_project_key` (function scope)

Generates a unique project key for each test to avoid collisions.

## Writing New Tests

### Basic Test Structure

```python
def test_my_scenario(tui, unique_project_key):
    # Create project
    result = tui.create_project(key=unique_project_key, name="Test Project")
    assert result.success
    
    # Execute TUI commands
    result = tui.execute_command(["projects", "list"])
    assert result.success
    assert unique_project_key in result.stdout
```

### Checking Output Patterns

```python
result = tui.list_projects()
assert tui.expect_output(result, r"TEST-\d+")  # Regex match
```

### Handling Expected Failures

```python
result = tui.execute_command(["invalid", "command"], check=False)
assert not result.success  # Expect failure
```

### Waiting for Conditions

```python
def check_project_exists():
    result = tui.list_projects()
    return unique_project_key in result.stdout

tui.wait_for_condition(check_project_exists, timeout=10.0)
```

## CI Integration

Tests run automatically in CI via `.github/workflows/ci.yml` (or similar).

**CI command:**

```bash
pytest tests/e2e/tui/ -v --tb=short --maxfail=3
```

## Performance Targets

- Full suite: < 5 minutes
- Individual test: < 30 seconds (excluding slow tests)
- Backend startup: < 10 seconds

## Troubleshooting

### Backend Fails to Start

**Symptom:** Tests fail with "Backend server failed to start"

**Fix:**
- Ensure `apps/api/` exists and is valid
- Check `PROJECT_DOCS_PATH` is writable
- Verify Python environment has `uvicorn` installed

### Tests Are Flaky

**Symptom:** Tests pass/fail non-deterministically

**Fix:**
- Check for `time.sleep()` usage (use `wait_for_condition` instead)
- Ensure test data uses deterministic seeds
- Verify backend fully starts before tests run (increase `max_wait` in conftest)

### Command Timeouts

**Symptom:** "Command timed out after 30s"

**Fix:**
- Increase timeout: `tui.execute_command(cmd, timeout=60.0)`
- Check backend health: `curl http://localhost:8000/health`
- Review command complexity (split into smaller steps)

## Future Enhancements

- [ ] Add artifact generation tests (requires TUI artifact commands)
- [ ] Add proposal apply/reject tests (requires TUI propose commands)
- [ ] Add audit run tests (requires TUI audit command)
- [ ] Add RAID item management tests (requires TUI raid commands)
- [ ] Parallel test execution (pytest-xdist)
- [ ] Test duration tracking and alerting
