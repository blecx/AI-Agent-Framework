# CI/CD Quality Gates Documentation

This document describes the comprehensive CI quality gates implemented for the backend to ensure code quality, test coverage, documentation accuracy, and security.

## Overview

The backend uses a **9-gate CI pipeline** that runs on every pull request to `main`. All gates must pass before a PR can be merged.

**CI Workflow**: `.github/workflows/ci-backend.yml`

**CD Workflows**:

- `.github/workflows/reusable-ghcr-publish.yml`
- `.github/workflows/cd-backend.yml`
- `.github/workflows/rollback-backend.yml`
- `.github/workflows/cd-smoke.yml`

**Local Simulation**: `./scripts/ci_backend.sh`

## CD Baseline (Staging + Production)

The repository now includes a baseline backend CD pipeline that:

1. Publishes immutable API and Web images to GHCR on pushes to `main`
2. Deploys to `staging`
3. Runs environment health checks
4. Deploys to `production`

The deploy mechanism is intentionally host-agnostic through a remote command contract (`DEPLOY_COMMAND`) so it can be used with mixed hosting.

### GitHub Environments Required

Create two GitHub Environments:

- `staging`
- `production`

Configure environment protection rules as needed (reviewers, wait timers, branch restrictions).

### Environment Variables and Secrets

Add these values to each environment (`staging` and `production`):

#### Variables

- `DEPLOY_HOST` - SSH host or IP for the target environment
- `DEPLOY_USER` - SSH user on the target host
- `DEPLOY_COMMAND` - Remote shell command that performs deployment
- `HEALTHCHECK_URL` - URL checked after deployment (for example `https://staging.example.com/api/health`)

#### Secrets

- `DEPLOY_SSH_PRIVATE_KEY` - Private key used for SSH deployment
- `DEPLOY_GHCR_USERNAME` - GHCR username with package read access
- `DEPLOY_GHCR_TOKEN` - GHCR token (PAT) with package read access

### Remote Deploy Command Contract

`DEPLOY_COMMAND` runs on the remote host and receives these environment variables from GitHub Actions:

- `API_IMAGE` - Exact API image reference (SHA tag)
- `WEB_IMAGE` - Exact Web image reference (SHA tag)
- `GHCR_USERNAME` - Username for GHCR login
- `GHCR_TOKEN` - Token for GHCR login

Example command for a Docker Compose target host:

```bash
cd /opt/ai-agent-framework && \
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin && \
export API_IMAGE WEB_IMAGE && \
docker compose pull api web && \
docker compose up -d api web
```

### Manual Execution

You can manually trigger `.github/workflows/cd-backend.yml` via `workflow_dispatch` with target:

- `staging`
- `production`
- `both`

### Rollback (Automated)

Rollback is automated via workflow dispatch with immutable GHCR SHA tags:

- Backend rollback workflow: `.github/workflows/rollback-backend.yml`
- Client rollback workflow (client repo): `.github/workflows/rollback.yml`

Both rollback workflows:

- Require full immutable image tags (`ghcr.io/...:sha-...`)
- Reuse the same environment-scoped deploy variables/secrets as CD
- Execute the same remote deployment command contract
- Run post-deploy health checks before finishing

### CD Best Practices (Recommended)

To keep production standards high, apply these controls in both repositories:

1. Enable environment protection on `production`:
   - Required reviewers
   - Branch restrictions (`main` only)
   - Optional wait timer for controlled rollout windows
2. Keep immutable deployment history:
   - Deploy only SHA image tags for rollback-safe releases
   - Store deployed API/WEB/CLIENT SHA tags in release notes or ops log
3. Keep remote deploy commands idempotent:
   - `docker login` + `docker compose pull` + `docker compose up -d`
   - No destructive operations outside explicit migration steps
4. Validate rollback path periodically:
   - Run rollback drill from latest known-good SHA at least once per sprint
5. Apply least privilege:
   - Use environment secrets (not repository-wide secrets)
   - Use a GHCR token with package read-only permissions for deploy hosts

### Smoke Tests (Automated)

The backend repository includes a dedicated smoke workflow:

- `.github/workflows/cd-smoke.yml`

Trigger modes:

- Automatic after successful completion of `Backend CD` and `Backend Rollback`
- Manual via `workflow_dispatch` with `target=staging|production|both`

The smoke workflow uses each environment's `HEALTHCHECK_URL` and retries before failing.

## The 9 Quality Gates

### Gate 1: All Tests Pass ✅

**Purpose**: Ensure all unit, integration, and E2E tests pass.

**What it checks**:
- Unit tests (`tests/unit/`)
- Integration tests (`tests/integration/`)
- E2E tests (`tests/e2e/`)

**How to pass**:
```bash
pytest tests/unit/ -v
pytest tests/integration/ -v
TERM=xterm-256color pytest tests/e2e/ -v
```

**Failure remediation**:
- Run `pytest tests/` locally
- Fix failing tests
- Ensure `projectDocs/` directory exists for E2E tests

---

### Gate 2: Coverage Threshold (80%+) 📊

**Purpose**: Ensure new/changed code has adequate test coverage.

**What it checks**:
- Coverage for all files changed in the PR
- Minimum 80% coverage required for changed files

**How to pass**:
```bash
bash scripts/run_pytest_coverage.sh --ci
python scripts/coverage_diff.py origin/main HEAD
```

For local troubleshooting (when GUI/perf environment is not available), use:

```bash
bash scripts/run_pytest_coverage.sh --local-stable
```

**Failure remediation**:
- Identify uncovered lines in coverage report
- Add tests to cover new/changed code
- Aim for 80%+ coverage on all changed files

**Notes**:
- `__init__.py` files are excluded
- Coverage is calculated per changed file, not globally

---

### Gate 3: Missing Tests Detection 🔍

**Purpose**: Prevent new code from being added without corresponding test files.

**What it checks**:
- For each new/changed Python file in `apps/`, checks if a test file exists
- Expected test path: `tests/unit/test_<module_path>`

**How to pass**:
- When adding `apps/api/services/new_service.py`
- Create `tests/unit/test_services/test_new_service.py`

**Failure remediation**:
```bash
# For each new module file, create a corresponding test file
# Example:
mkdir -p tests/unit/services
touch tests/unit/test_services/test_new_service.py
```

**Notes**:
- `__init__.py` files don't require test files
- Test files should follow the `test_*.py` naming convention

---

### Gate 4: Documentation Sync 📚

**Purpose**: Ensure `tests/README.md` accurately reflects the current test structure.

**What it checks**:
- All test directories documented
- No references to deleted test directories
- pytest commands reference existing directories

**How to pass**:
```bash
python scripts/check_test_docs.py
```

**Failure remediation**:
1. Update `tests/README.md` to document all test directories
2. Remove references to deleted directories
3. Update pytest command examples to match current structure

**Example test directory structure**:
```
tests/
├── README.md          # Must document all directories below
├── unit/              # Unit tests
├── integration/       # Integration tests
├── e2e/               # End-to-end tests
│   └── tui/          # TUI-driven E2E tests
├── fixtures/          # Shared test fixtures
└── helpers/           # Test helper utilities
```

---

### Gate 5: OpenAPI Spec Validation 📝

**Purpose**: Ensure all API endpoints are documented with complete OpenAPI specs.

**What it checks**:
- OpenAPI spec can be generated from FastAPI app
- All endpoints have `summary` or `description`
- Required fields (`openapi`, `info`, `paths`) present

**How to pass**:
```bash
cd apps/api
python -c "from main import app; print(app.openapi())"
```

**Failure remediation**:
1. Add docstrings to API endpoint functions
2. Use FastAPI `summary` or `description` parameters in route decorators
3. Example:
   ```python
   @router.get("/projects", summary="List all projects")
   def list_projects():
       """
       Retrieve all projects from the git repository.
       Returns a list of project metadata.
       """
       ...
   ```

---

### Gate 6: Linting (black + flake8) 🎨

**Purpose**: Enforce consistent code style and catch common Python errors.

**What it checks**:
- `black` formatting (PEP 8 compliant)
- `flake8` linting (code quality checks)

**How to pass**:
```bash
python -m black apps/api/ apps/tui/ tests/
python -m flake8 apps/api/ apps/tui/ tests/
```

**Failure remediation**:
1. Run `black` to auto-format code:
   ```bash
   python -m black apps/api/ apps/tui/ tests/
   ```
2. Fix remaining `flake8` issues manually
3. Common issues:
   - Unused imports (`F401`)
   - Undefined variables (`F821`)
   - Line too long (`E501`) - black usually fixes these
   - Ambiguous variable names (`E741`)

**Configuration**:
- `black`: Uses default settings (88 char line length)
- `flake8`: Configured in `setup.cfg` or `.flake8`

---

### Gate 7: Security Scanning (bandit + safety) 🔒

**Purpose**: Detect security vulnerabilities in code and dependencies.

**What it checks**:
- **bandit**: Scans Python code for security issues
- **safety**: Checks dependencies for known vulnerabilities

**How to pass**:
```bash
pip install bandit safety
bandit -r apps/api/ apps/tui/ -ll
safety check
```

**Failure remediation**:

**For bandit issues**:
- Review flagged code for security concerns
- Fix high-severity issues (SQL injection, hardcoded secrets, etc.)
- Use `# nosec` comment only if false positive
- Example:
  ```python
  # Intentional use of exec for dynamic code - reviewed
  exec(user_code)  # nosec
  ```

**For safety issues**:
- Update vulnerable dependencies to patched versions
- Check for security advisories
- Example:
  ```bash
  pip install --upgrade <vulnerable-package>
  ```

**Notes**:
- Only **high severity** issues fail the build
- Medium/low severity issues are warnings only
- Whitelisting false positives: Add to `bandit.yml` config

---

### Gate 8: Test Execution Time (<10 min) ⏱️

**Purpose**: Prevent test suite from becoming too slow, ensure fast feedback.

**What it checks**:
- Full test suite must complete in under 10 minutes (600 seconds)

**How to pass**:
- Tests naturally fast enough (currently ~3-15 seconds)

**Failure remediation**:
1. Identify slow tests:
   ```bash
   pytest tests/ -v --durations=10
   ```
2. Optimize slow tests:
   - Mock external services (avoid real HTTP calls)
   - Use in-memory databases for integration tests
   - Reduce sleep/wait times
   - Parallelize tests: `pytest -n auto` (requires pytest-xdist)
3. Consider moving long-running tests to separate job/workflow

**Current performance**:
- Unit tests: ~1-2s
- Integration tests: ~2-3s
- E2E tests: ~10-15s
- **Total**: ~15-20s (well under 600s limit)

---

### Gate 9: Flaky Test Detection 🔄

**Purpose**: Identify non-deterministic tests that pass/fail randomly.

**What it checks**:
- Runs full test suite 3 times
- Checks for inconsistent results (different exit codes)

**How to pass**:
- Tests should be deterministic (same result every run)

**Failure remediation**:
1. Identify flaky tests (check CI logs for differences between runs)
2. Common causes of flakiness:
   - Race conditions (timing-dependent tests)
   - Non-mocked network calls
   - Filesystem state dependencies
   - Random data without fixed seeds
   - Shared state between tests
3. Fix examples:
   ```python
   # BAD: Non-deterministic due to random
   import random
   def test_random_data():
       data = random.randint(1, 100)
       assert data > 50  # Fails ~50% of the time
   
   # GOOD: Deterministic with fixed seed
   import random
   def test_random_data():
       random.seed(42)
       data = random.randint(1, 100)
       assert data == 82  # Always passes
   ```

**Notes**:
- This gate is **warning only** (doesn't fail the build)
- Flaky tests harm CI reliability
- Fix flaky tests promptly to maintain trust in CI

---

## Local CI Simulation

Before pushing, run the full CI pipeline locally:

```bash
./scripts/ci_backend.sh
```

This runs all gates (except Gate 9 which is too time-consuming) and provides a summary:

```
==================================================
🔍 Backend CI Quality Gates - Local Simulation
==================================================

Gate 1: All Tests Pass
✅ Gate 1 PASSED

Gate 2: Coverage Threshold (80%+)
✅ Gate 2 PASSED

...

==================================================
CI Gates Summary
==================================================
Passed: 8
Failed: 0

🎉 All gates passed! Ready to push.
```

## CI Workflow Structure

The CI workflow uses a **fail-fast pipeline** with dependencies:

```
test (Gate 1) ─────┬─→ coverage (Gate 2)
                   ├─→ missing-tests (Gate 3)
                   ├─→ docs-sync (Gate 4)
                   ├─→ openapi (Gate 5)
                   ├─→ test-time (Gate 8)
                   └─→ flaky-tests (Gate 9)

lint (Gate 6) ─────┘
security (Gate 7) ─┘

All gates ──→ all-gates-passed (final)
```

**Key points**:
- Gates 2-5, 8-9 depend on Gate 1 (tests must pass first)
- Gates 6-7 run independently (can run in parallel)
- Final gate depends on ALL previous gates

## Helper Scripts

### `scripts/ci_backend.sh`

Local CI simulation script.

**Usage**:
```bash
./scripts/ci_backend.sh
```

**What it does**:
- Runs all 9 gates locally
- Skips Gate 9 (too slow for local use)
- Provides colored output and summary

---

### `scripts/check_test_docs.py`

Documentation sync checker.

**Usage**:
```bash
python scripts/check_test_docs.py
```

**What it does**:
- Scans `tests/` for all test directories
- Parses `tests/README.md` for documented directories
- Reports missing/outdated documentation

**Output**:
```
✅ Documentation sync check PASSED
   - 6 test directories documented
   - 8 pytest commands validated
```

---

### `scripts/coverage_diff.py`

Coverage delta calculator.

**Usage**:
```bash
python scripts/coverage_diff.py <base_ref> <head_ref>
```

**Example**:
```bash
python scripts/coverage_diff.py origin/main HEAD
```

**What it does**:
- Compares coverage between two git refs
- Checks if changed files meet 80% threshold
- Reports files below threshold

**Output**:
```
Checking coverage diff: origin/main...HEAD

Changed files (2):
  - apps/api/services/new_service.py
  - apps/api/routers/new_router.py

✅ All changed files have 80%+ coverage
  - apps/api/services/new_service.py: 92.5%
  - apps/api/routers/new_router.py: 85.3%
```

## Best Practices

### CI Incident Governance (Open/Re-scope Policy)

When opening a new CI issue or re-scoping an older one, require concrete evidence first:

1. **Failed run URL** (exact GitHub Actions run)
2. **Failing workflow/job/step** (precise name)
3. **Local reproduction command** and output
4. **Expected vs actual behavior**
5. **Narrow scope** (clear In Scope / Out of Scope)

Use the dedicated issue form: `.github/ISSUE_TEMPLATE/ci_gate_incident.yml`.

If the original acceptance criteria are already satisfied, close the old issue with validation evidence and open a new, narrowly scoped CI incident issue only when a new failure is reproducible.

### When Adding New Code

1. **Write tests first** (TDD approach)
2. **Run tests locally** before pushing: `pytest tests/`
3. **Check coverage** for your changes: `pytest tests/ --cov=apps/api --cov-report=term-missing`
4. **Run full CI simulation**: `./scripts/ci_backend.sh`
5. **Push to PR** and wait for CI to pass

### When CI Fails

1. **Read the failure message** - each gate has specific remediation steps
2. **Reproduce locally**:
   - Gate 1: `pytest tests/`
   - Gate 2: `python scripts/coverage_diff.py origin/main HEAD`
   - Gate 6: `python -m black --check apps/api/ && python -m flake8 apps/api/`
3. **Fix the issue** based on remediation guidance
4. **Re-run locally** to confirm fix
5. **Push** and wait for CI to re-run

### Maintaining Fast CI

- **Optimize slow tests** (use `pytest --durations=10`)
- **Mock external services** (avoid network calls)
- **Use test fixtures** efficiently (session vs function scope)
- **Parallelize when possible** (`pytest -n auto`)

## FAQ

**Q: Can I skip a failing gate?**
A: No. All gates must pass before merging. This ensures code quality and prevents regressions.

**Q: What if I have a valid reason for a security warning?**
A: Add a `# nosec` comment with explanation, or update the bandit config to whitelist false positives.

**Q: How do I add a new CI gate?**
A: Edit `.github/workflows/ci-backend.yml`, add a new job, update `all-gates-passed` dependencies, and add tests to `tests/ci/test_ci_gates.py`.

**Q: Why is my PR taking so long in CI?**
A: Check the workflow run logs. Gates run sequentially after Gate 1 (tests), so slow tests will delay all other gates.

**Q: Can I run CI locally without Docker?**
A: Yes, use `./scripts/ci_backend.sh` which runs all gates except Gate 9 (flaky test detection).

## Related Documentation

- **[Contributing Guide](../CONTRIBUTING.md)** - General contribution guidelines
- **[Testing Guide](../tests/README.md)** - Comprehensive testing documentation
- **[Development Guide](../development.md)** - Development workflow and best practices
- **[Architecture Documentation](architecture/)** - System design and architecture decisions

## Monitoring & Metrics

**CI Status**: Check the [Actions tab](https://github.com/blecx/AI-Agent-Framework/actions) for recent runs.

**Badges**: README.md shows CI status badges:

- [![Backend Quality Gates](https://github.com/blecx/AI-Agent-Framework/actions/workflows/ci-backend.yml/badge.svg)](https://github.com/blecx/AI-Agent-Framework/actions/workflows/ci-backend.yml)

**Key Metrics**:

- Test execution time (target: <10 min)
- Test coverage (target: 80%+)
- Security scan results (target: 0 high-severity issues)
- Flaky test rate (target: 0%)

---

**Last Updated**: February 15, 2026  
**CI Workflow Version**: 1.0  
**Maintained By**: Backend Team
