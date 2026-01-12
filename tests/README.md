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
│   └── test_workflow_service.py
├── integration/        # Integration tests for API endpoints
│   ├── test_core_api.py
│   ├── test_governance_api.py
│   ├── test_raid_api.py
│   └── test_workflow_api.py
├── e2e/                # End-to-end tests
│   ├── backend_e2e_runner.py  # E2E test harness
│   └── test_governance_raid_workflow.py
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
pytest --cov=apps/api tests/

# Generate HTML coverage report
pytest --cov=apps/api --cov-report=html tests/
# Open htmlcov/index.html in browser

# Coverage with missing lines
pytest --cov=apps/api --cov-report=term-missing tests/
```

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
