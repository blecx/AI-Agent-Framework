# Backend Tests

This directory contains the test suite for the AI-Agent-Framework backend.

## Test Structure

```
tests/
├── unit/          # Unit tests for individual components
├── integration/   # Integration tests for component interactions
└── e2e/           # End-to-end tests (TUI-driven)
```

## Running Tests Locally

### All Tests
```bash
pytest
```

### By Test Type
```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# E2E tests (TUI-driven, requires terminal)
TERM=xterm-256color pytest tests/e2e
```

### With Verbose Output
```bash
pytest -v tests/unit
```

### With Coverage
```bash
pytest --cov=src tests/
```

## Running Tests in CI

The CI workflow (`.github/workflows/ci.yml`) runs automatically on:
- Push to `main` branch
- Pull requests

The workflow executes:
1. Unit tests: `pytest -q tests/unit`
2. Integration tests: `pytest -q tests/integration`
3. E2E tests: `TERM=xterm-256color pytest -q tests/e2e`

## E2E Tests Notes

- **TUI-driven**: E2E tests interact with the Text User Interface
- **Non-interactive**: Tests run without user input
- **Deterministic**: Tests produce consistent, reproducible results
- **Terminal emulation**: Requires `TERM=xterm-256color` environment variable

## Prerequisites

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

Ensure pytest is installed:
```bash
pip install pytest
```

## Writing Tests

### Unit Tests
Place in `tests/unit/` and focus on testing individual functions/classes in isolation.

### Integration Tests
Place in `tests/integration/` and test interactions between multiple components.

### E2E Tests
Place in `tests/e2e/` and test complete user workflows through the TUI.
