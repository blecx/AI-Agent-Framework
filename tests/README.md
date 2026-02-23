# Backend Tests

This folder contains the backend test suite for the AI-Agent-Framework.

## Test structure (directories)

These are the test directories that contain Python test files (used by CI Gate 4's docs sync checker):

- `tests/unit/` (unit tests)
- `tests/unit/test_commands/` (TUI command unit tests)
- `tests/unit/domain/templates/`
- `tests/unit/domain/blueprints/`
- `tests/unit/domain/proposals/`
- `tests/integration/` (integration tests)
- `tests/integration/routers/`
- `tests/integration/services/`
- `tests/e2e/` (end-to-end tests)
- `tests/e2e/tui/` (deterministic TUI E2E)
- `tests/e2e/tutorial/` (tutorial-oriented E2E)
- `tests/performance/` (performance-focused tests)
- `tests/agents/` (agent framework tests)
- `tests/ci/` (CI gate validation tests)

## Running tests locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run everything:

```bash
pytest
```

Run by suite:

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# E2E tests (some require terminal emulation)
TERM=xterm-256color pytest tests/e2e

# Deterministic TUI E2E tests
pytest tests/e2e/tui -v

# Deterministic baseline spine test (run 3x)
for i in 1 2 3; do pytest tests/e2e/tui/test_workflow_spine.py -q; done

# Tutorial E2E tests
pytest tests/e2e/tutorial -v

# Agent framework tests
pytest tests/agents -v

# CI workflow validation tests
pytest tests/ci -v

# Performance tests
pytest tests/performance -v
```

Filter to a specific area (without hardcoding file paths):

```bash
# Examples:
pytest tests/unit -k command_service
pytest tests/integration -k templates
pytest tests/e2e -k step2
```

### Coverage

```bash
bash scripts/run_pytest_coverage.sh --ci
python scripts/coverage_diff.py origin/main HEAD
```

Local stable run (deterministic core suites only):

```bash
bash scripts/run_pytest_coverage.sh --local-stable
```

## CI notes

- Backend quality gates run in `.github/workflows/ci-backend.yml` (tests, coverage, docs sync, lint, security, etc.).
- The separate `.github/workflows/ci.yml` workflow is intentionally PR-meta/hygiene only.

## TUI E2E notes

`tests/e2e/tui/` starts a session-scoped backend for the suite and binds it to a dynamically chosen free localhost port (to avoid CI port conflicts).

For deterministic baseline verification (Issue #388 acceptance), run `tests/e2e/tui/test_workflow_spine.py` three consecutive times and ensure all runs pass.

For cross-repo E2E harness usage, prefer invoking the runner as a module (avoids hardcoding paths):

```bash
python -m tests.e2e.backend_e2e_runner --mode server
python -m tests.e2e.backend_e2e_runner --mode health-check --url http://localhost:8000
python -m tests.e2e.backend_e2e_runner --mode validate --url http://localhost:8000
```

