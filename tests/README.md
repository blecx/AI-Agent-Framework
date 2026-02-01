# Backend Tests

This directory contains the comprehensive test suite for the AI-Agent-Framework backend.

## Test Structure

```
tests/
├── unit/               # Unit tests for individual components
│   ├── test_audit_service.py
│   ├── test_command_service.py
│   ├── test_git_manager.py
│   ├── test_governance_service.py
│   ├── test_llm_service.py
│   ├── test_raid_service.py
│   ├── test_workflow_service.py
│   ├── test_skill_registry.py        # Skills registry tests
│   ├── test_memory_skill.py          # Memory skill tests
│   ├── test_planning_skill.py        # Planning skill tests
│   └── test_learning_skill.py        # Learning skill tests
├── integration/        # Integration tests for API endpoints
│   ├── test_core_api.py
│   ├── test_governance_api.py
│   ├── test_raid_api.py
│   ├── test_skills_api.py            # Skills API tests
│   ├── test_versioned_api.py
│   └── test_workflow_api.py
├── e2e/                # End-to-end tests
│   ├── backend_e2e_runner.py           # E2E test harness
│   ├── test_governance_raid_workflow.py # Step 1 workflow tests
│   ├── test_step2_workflow.py          # Step 2 workflow tests (NEW)
│   └── tui/                            # TUI E2E tests (deterministic, CI-ready)
│       ├── conftest.py                 # TUI test fixtures
│       ├── test_workflow_spine.py      # Core workflow scenarios
│       ├── test_proposal_workflow.py   # Proposal lifecycle tests
│       ├── test_audit_fix_cycle.py     # Audit and fix cycle tests
│       └── README.md                   # TUI E2E documentation
├── helpers/            # Test helper utilities
│   └── tui_automation.py               # TUI command automation service
├── fixtures/           # Test data factories
│   └── factories.py                    # Builders for Project, Artifact, Proposal, RAID
└── README.md           # This file
```

## Running Tests Locally

### Prerequisites

Install dependencies including test tools:
```bash
pip install -r requirements.txt
```

Required packages:
- pytest
- pytest-asyncio
- pytest-cov
- httpx (for integration tests)

### All Tests
```bash
pytest
```

### By Test Type
```bash
# Unit tests only
pytest tests/unit

# Integration tests only
pytest tests/integration

# E2E tests only (requires terminal emulation)
TERM=xterm-256color pytest tests/e2e

# TUI E2E tests only (deterministic, CI-ready)
pytest tests/e2e/tui -v

# Skills tests only
pytest tests/unit/test_*skill*.py tests/integration/test_skills_api.py
```

### Specific Test Files
```bash
# Run single test file
pytest tests/unit/test_command_service.py

# Run specific test class
pytest tests/unit/test_git_manager.py::TestProjectOperations

# Run specific test function
pytest tests/unit/test_llm_service.py::TestChatCompletion::test_chat_completion_success
```

### With Verbose Output
```bash
# Verbose with test names
pytest -v tests/unit

# Very verbose with full output
pytest -vv tests/integration
```

### With Coverage
```bash
# Run tests with coverage report
pytest --cov=apps/api --cov-report=term-missing tests/

# Generate HTML coverage report
pytest --cov=apps/api --cov-report=html tests/
# Open htmlcov/index.html in browser

# Coverage with missing lines
pytest --cov=apps/api --cov-report=term-missing tests/

# Run with coverage threshold check (80%)
pytest --cov=apps/api --cov-report=term-missing --cov-fail-under=80 tests/
```

**Note**: Coverage options are not included in pytest.ini by default to allow flexible CI configurations. Always specify coverage options explicitly when needed.

### Running Specific Test Markers
```bash
# Run only unit tests (if marked)
pytest -m unit

# Run only integration tests (if marked)
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Parallel Execution (Optional)
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto tests/
```

## Test Configuration

### pytest.ini
Configuration file located at project root:
- Test discovery paths
- Coverage settings (80% minimum)
- Output formatting
- Asyncio mode settings

### .coveragerc
Coverage configuration:
- Source paths to measure
- Files to omit from coverage
- Reporting options
- Exclusion patterns

## Running Tests in CI

The CI workflow (`.github/workflows/ci.yml`) runs automatically on:
- Push to `main` branch
- Pull requests

The workflow executes:
1. Unit tests: `pytest -q tests/unit`
2. Integration tests: `pytest -q tests/integration`
3. E2E tests: `TERM=xterm-256color pytest -q tests/e2e`
4. Coverage reporting (uploaded as artifact)

## TUI E2E Tests

**New in Step 3**: Deterministic, non-interactive end-to-end tests using the TUI CLI.

### Overview

TUI E2E tests validate complete workflows through the command-line interface:

- **Workflow spine**: Project → artifacts → proposal → apply → audit
- **Proposal workflow**: Manual and AI-assisted proposals, apply/reject
- **Audit fix cycle**: Detect issues → fix via proposals → re-audit → verify clean

**Key Features**:
- ✅ Deterministic execution (no flaky tests)
- ✅ Non-interactive (fully automated)
- ✅ CI-ready (runs in GitHub Actions)
- ✅ Fast feedback (< 5 min full suite)
- ✅ Session-scoped backend (shared across tests)

### Running TUI E2E Tests

```bash
# All TUI E2E tests
pytest tests/e2e/tui/ -v

# Specific test file
pytest tests/e2e/tui/test_workflow_spine.py -v

# Specific test
pytest tests/e2e/tui/test_workflow_spine.py::test_workflow_spine_full_cycle -v

# Skip slow tests
pytest tests/e2e/tui/ -v -m "not slow"

# With detailed output
pytest tests/e2e/tui/ -vv --tb=short
```

### Test Structure

```
tests/e2e/tui/
├── conftest.py                 # Fixtures (backend_server, tui, factories)
├── test_workflow_spine.py      # Core workflow scenarios (5 tests)
├── test_proposal_workflow.py   # Proposal lifecycle (5 tests)
├── test_audit_fix_cycle.py     # Audit and fix cycle (6 tests)
└── README.md                   # Detailed TUI E2E documentation
```

**Supporting infrastructure**:
- `tests/helpers/tui_automation.py` - TUI command execution service (~180 lines)
- `tests/fixtures/factories.py` - Test data builders (~230 lines)

### Key Fixtures

#### `backend_server` (session scope)

Starts FastAPI backend once for all tests, provides `http://localhost:8000` URL.

#### `tui` (function scope)

Provides `TUIAutomation` instance for executing TUI commands.

**Usage:**
```python
def test_example(tui, unique_project_key):
    result = tui.create_project(key=unique_project_key, name="Test")
    assert result.success
    assert unique_project_key in result.stdout
```

#### `unique_project_key` (function scope)

Generates unique project key per test to avoid collisions.

### Test Data Factories

Create deterministic test data with fluent APIs:

```python
from fixtures.factories import ProjectFactory, ArtifactFactory, ProposalFactory, RAIDFactory

# Deterministic project
project = ProjectFactory().with_key("TEST-001").with_name("Test Project").build()

# Seeded random data
project = ProjectFactory().with_seed(12345).build()

# Artifact with custom content
artifact = ArtifactFactory().with_type("pmp").with_content("# PMP\n...").build()
```

### Writing New TUI E2E Tests

See `tests/e2e/tui/README.md` for detailed examples and patterns.

**Basic structure:**
```python
def test_my_workflow(tui, unique_project_key):
    # Arrange: Create project
    result = tui.create_project(key=unique_project_key, name="My Test")
    assert result.success
    
    # Act: Execute TUI commands
    result = tui.execute_command(["projects", "list"])
    
    # Assert: Verify output
    assert result.success
    assert tui.expect_output(result, unique_project_key)
```

### Performance Targets

- Full TUI E2E suite: < 5 minutes
- Individual test: < 30 seconds (excluding `@pytest.mark.slow`)
- Backend startup: < 10 seconds

### Troubleshooting

**Backend fails to start:**
- Check `apps/api/` directory exists
- Verify `uvicorn` installed in venv
- Ensure `PROJECT_DOCS_PATH` is writable

**Flaky tests:**
- Avoid `time.sleep()` - use `tui.wait_for_condition()` instead
- Use deterministic seeds in factories
- Increase backend startup timeout in `conftest.py`

**For more help**, see `tests/e2e/tui/README.md`.

## E2E Test Harness

### Backend E2E Runner

For cross-repo E2E testing with the client, use the backend E2E runner:

```bash
# Start backend server for E2E testing
python tests/e2e/backend_e2e_runner.py --mode server

# Check backend health
python tests/e2e/backend_e2e_runner.py --mode health-check --url http://localhost:8000

# Run validation suite
python tests/e2e/backend_e2e_runner.py --mode validate --url http://localhost:8000

# Wait for backend, then validate
python tests/e2e/backend_e2e_runner.py --mode wait-and-validate --url http://localhost:8000
```

See `E2E_TESTING.md` for detailed cross-repo E2E documentation.

### Step 2 E2E Tests

**File**: `tests/e2e/test_step2_workflow.py`

**Purpose**: Validate complete Step 2 workflow (Templates, Blueprints, Artifacts, Proposals, Audit)

**Test Scenarios**:
1. **Template CRUD Workflow**: Create → List → Get → Update → Delete
2. **Blueprint Creation**: Create blueprint referencing valid templates
3. **Artifact Generation from Template**: Generate PMP artifact with valid content
4. **Artifact Generation from Blueprint**: Generate 5+ artifacts from blueprint
5. **Proposal Workflow** *(disabled - router not yet enabled)*: Create → Apply → Verify
6. **Audit Events Validation**: Verify audit events logged for all operations
7. **Error Handling**: Invalid template ID, non-existent blueprint, etc.

**Running Step 2 E2E Tests**:
```bash
# Run all Step 2 E2E tests
pytest tests/e2e/test_step2_workflow.py -v

# Run specific scenario
pytest tests/e2e/test_step2_workflow.py::test_template_crud_workflow -v

# Run with output (useful for debugging)
pytest tests/e2e/test_step2_workflow.py -v -s

# Skip proposal tests (currently disabled)
pytest tests/e2e/test_step2_workflow.py -v -k "not proposal"
```

**Acceptance Criteria**:
- ✅ All 7 test scenarios pass
- ✅ Test execution time < 60 seconds (individual tests < 5 seconds)
- ✅ Tests are deterministic (no flakiness, no sleep-based waits)
- ✅ Tests use isolated temporary directories (no state leakage)

**Troubleshooting**:
- **Issue**: Template not found after creation
  - **Fix**: Ensure git operations complete; check git_manager service
- **Issue**: Artifact generation fails
  - **Fix**: Verify template schema matches context data
- **Issue**: Audit events not logged
  - **Fix**: Check audit_service initialization in test client

## Writing Tests

### Unit Tests

**Location**: `tests/unit/`

**Purpose**: Test individual functions/classes in isolation

**Guidelines**:
- Mock external dependencies (filesystem, network, database)
- Test one component at a time
- Use fixtures for common setup
- Test both success and failure paths
- Aim for high coverage (>90%)

**Example**:
```python
import pytest
from unittest.mock import Mock
from apps.api.services.example_service import ExampleService

@pytest.fixture
def mock_dependency():
    """Create a mock dependency."""
    return Mock()

def test_example_function(mock_dependency):
    """Test example function with mocked dependency."""
    service = ExampleService(mock_dependency)
    result = service.do_something()
    assert result == expected_value
    mock_dependency.some_method.assert_called_once()
```

### Integration Tests

**Location**: `tests/integration/`

**Purpose**: Test API endpoints and component interactions

**Guidelines**:
- Use FastAPI TestClient
- Create isolated test environment per test
- Use temporary directories for file operations
- Clean up after tests
- Test realistic workflows
- Verify both success and error responses

**Example**:
```python
import pytest
import tempfile
import shutil
from fastapi.testclient import TestClient

@pytest.fixture
def temp_project_dir():
    """Create temporary directory for test."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def client(temp_project_dir):
    """Create test client with isolated environment."""
    # Setup test app with temp directory
    # ... (see test_core_api.py for full example)
    yield test_client

def test_create_project(client):
    """Test project creation endpoint."""
    response = client.post("/projects", json={"key": "TEST", "name": "Test"})
    assert response.status_code == 201
    assert response.json()["key"] == "TEST"
```

### E2E Tests

**Location**: `tests/e2e/`

**Purpose**: Test complete workflows through TUI or API

**Guidelines**:
- Test realistic user scenarios
- Test cross-component workflows
- Ensure tests are deterministic
- Use unique test data per run
- Verify end-to-end outcomes

## Test Isolation

**Critical**: Every test must be independent and isolated.

### Requirements
1. **No shared state** between tests
2. **Unique temp directories** per test
3. **Clean setup and teardown**
4. **No order dependencies**
5. **Parallel-safe** (when using pytest-xdist)

### Example Isolated Test
```python
import pytest
import tempfile
import shutil
import os

@pytest.fixture(scope="function")  # Function scope = new fixture per test
def isolated_env():
    """Create fully isolated test environment."""
    temp_dir = tempfile.mkdtemp()
    os.environ["PROJECT_DOCS_PATH"] = temp_dir
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)
    if "PROJECT_DOCS_PATH" in os.environ:
        del os.environ["PROJECT_DOCS_PATH"]
```

## Coverage Guidelines

### Target Coverage
- **Overall**: 80%+ (enforced in pytest.ini)
- **Services**: 90%+
- **Routers**: 85%+
- **Models**: 100% (simple data classes)

### Reviewing Coverage
```bash
# Generate HTML report
pytest --cov=apps/api --cov-report=html tests/

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Improving Coverage
1. Identify uncovered lines in HTML report
2. Add tests for missing branches
3. Test error handling paths
4. Test edge cases
5. Re-run coverage to verify improvement

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH=/path/to/AI-Agent-Framework:$PYTHONPATH
pytest tests/
```

#### Git Configuration Errors
```bash
# Configure git for test environment
git config --global user.email "test@example.com"
git config --global user.name "Test User"
```

#### Permission Errors
```bash
# Ensure temp directories are writable
# Check /tmp permissions or use alternative:
export TMPDIR=/path/to/writable/temp
```

#### Test Hangs or Timeout
- Check for missing `await` in async tests
- Increase timeout for slow operations
- Use `pytest-timeout` plugin

#### Flaky Tests
- Ensure proper test isolation
- Remove timing dependencies
- Mock external services
- Use deterministic test data

### Debug Mode
```bash
# Run with debug output
pytest -vv --log-cli-level=DEBUG tests/unit/test_example.py

# Drop into debugger on failure
pytest --pdb tests/unit/test_example.py

# Stop on first failure
pytest -x tests/
```

## Best Practices

### Do's ✅
- ✅ Write tests for all new features
- ✅ Test both success and failure paths
- ✅ Use descriptive test names
- ✅ Keep tests focused and simple
- ✅ Use fixtures for common setup
- ✅ Mock external dependencies
- ✅ Clean up resources after tests
- ✅ Make tests deterministic
- ✅ Run tests before committing

### Don'ts ❌
- ❌ Don't share state between tests
- ❌ Don't rely on test execution order
- ❌ Don't use real external services
- ❌ Don't commit test artifacts
- ❌ Don't skip cleanup code
- ❌ Don't use random data without seeds
- ❌ Don't ignore test failures
- ❌ Don't test implementation details

## Continuous Integration

### Pre-Commit Checks
```bash
# Run quick checks before committing
pytest tests/unit -x  # Stop on first failure

# Full test suite
pytest tests/

# With coverage
pytest --cov=apps/api tests/
```

### CI Pipeline
1. **Lint**: Code style checks
2. **Unit Tests**: Fast, isolated tests
3. **Integration Tests**: API endpoint tests
4. **E2E Tests**: Complete workflow tests
5. **Coverage**: Generate and upload coverage report

## Additional Resources

- **E2E Testing Guide**: See `E2E_TESTING.md` for cross-repo E2E documentation
- **Pytest Documentation**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Coverage.py**: https://coverage.readthedocs.io/

## Support

For questions or issues with tests:
1. Check this README for common solutions
2. Review existing tests for examples
3. Create issue in GitHub repository
4. Tag with `testing` label
