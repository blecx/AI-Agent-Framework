# Contributing to AI-Agent-Framework

Thank you for contributing! This guide covers coding conventions and best practices for this project.

## Development Setup

See [QUICKSTART.md](QUICKSTART.md) for initial setup instructions.

## Architecture Overview

This project follows **Domain-Driven Design (DDD)** architecture:

```text
apps/api/
├── domain/          # Core business logic (entities, value objects, validators)
├── services/        # Application services (orchestration, business logic)
├── routers/         # API layer (HTTP protocol concerns only)
└── models.py        # Backward compatibility facade (deprecated, use domain imports)
```

### Key Principles

1. **Single Responsibility:** Each class/module has ONE clear purpose
2. **Domain Separation:** Clear boundaries between domains (Templates, Blueprints, Proposals, etc.)
3. **Type Safety:** Explicit interfaces and Pydantic models for all domain objects
4. **Dependencies:** Infrastructure → Services → Domain (never reversed)

## Import Patterns (CRITICAL)

**Always use relative imports** - The API runs inside a Docker container with working directory `/app` (not workspace root).

### ✅ CORRECT Import Patterns

```python
# In routers/
from domain.templates.models import Template, TemplateCreate
from services.template_service import TemplateService
from models import ProjectCreate  # Backward compatibility facade

# In services/
from domain.proposals.models import Proposal, ProposalStatus
from services.git_manager import GitManager

# In domain layer
from domain.shared.validators import validate_identifier
```

### ❌ INCORRECT Import Patterns (Will Break in Docker)

```python
# NEVER use these - they only work in workspace root, not in containers
from apps.api.domain.templates.models import Template
from apps.api.services.template_service import TemplateService
```

### Why This Matters

Docker containers set `WORKDIR /app` which maps to `apps/api/`. Absolute imports starting with `apps.api.*` fail because Python cannot find an `apps` module inside `/app`.

**If imports work locally but fail in Docker**, check for `apps.api.*` patterns.

## Code Style

### Python

- **Formatter:** `black apps/api/` (automatic formatting)
- **Linter:** `flake8 apps/api/` (style checking)
- **Type hints:** Use where helpful, not required everywhere
- **Docstrings:** Use for public APIs, optional for internal functions
- **Line length:** 88 characters (black default)

### TypeScript/React (Client)

- **Strict mode:** Enabled (no `any` types in production code)
- **Formatter:** Built into ESLint config
- **Linter:** `npm run lint` in `apps/web/`
- **Tests:** Vitest + React Testing Library

## Testing Requirements

### Backend

- **Target:** 90%+ test ratio (currently 92%)
- **Run:** `pytest` or `pytest tests/unit` or `pytest tests/e2e`
- **Write tests for:**
  - New service methods
  - Domain validators
  - API endpoints (integration tests)

### Frontend

- **Current:** 23% test ratio (tracking issue: #147)
- **Target:** 50%+ test ratio
- **Run:** `npm run test` or `npm run test -- --run`
- **Write tests for:**
  - Complex components
  - API client classes
  - State management

## Domain-Specific Guidelines

### Adding a New Domain

1. Create domain directory: `apps/api/domain/my_domain/`
2. Add models: `apps/api/domain/my_domain/models.py`
3. Add validators: `apps/api/domain/my_domain/validators.py`
4. Create service: `apps/api/services/my_domain_service.py`
5. Create router: `apps/api/routers/my_domain.py`
6. Register router in `apps/api/main.py`
7. Add tests: `tests/unit/domain/test_my_domain.py`
8. Update `models.py` facade if needed (backward compatibility)

### File Size Targets

- **Domain models:** < 50 lines per file
- **Services:** < 200 lines per file (split if larger)
- **Routers:** < 100 lines per file
- **Components (UX):** < 100 lines per file

## Git Workflow

### Branches

- `main` - Production-ready code (protected)
- `feat/description-issue-number` - Feature development
- `fix/description-issue-number` - Bug fixes

### Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(templates): add template versioning support
fix(health): handle missing LLM service gracefully
docs(contributing): add import pattern guidelines
test(proposals): add conflict detection tests
```

### Pull Requests

1. **Small PRs:** < 200 lines changed (prefer < 100)
2. **One concern per PR:** Don't mix features with refactoring
3. **Tests included:** All new functionality must have tests
4. **CI passing:** All checks must pass before merge
5. **Squash merge:** Use squash commits to keep history clean

## Common Pitfalls

### 1. Import Paths in Docker

**Problem:** Code works locally but fails in Docker with `ModuleNotFoundError: No module named 'apps'`

**Solution:** Use relative imports (see [Import Patterns](#import-patterns-critical) above)

### 2. Missing PROJECT_DOCS_PATH

**Problem:** API fails to start with Git initialization error

**Solution:** Set environment variable: `PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload`

### 3. LLM Service Configuration

**Problem:** API shows "degraded" status due to LLM unavailable

**Solution:** This is normal - LLM is optional. System falls back to templates. See `configs/llm.default.json` for configuration options.

### 4. Test Imports

**Problem:** Tests cannot import from `apps.api.*`

**Solution:** Run tests from workspace root (not from `apps/api/`). Pytest will handle PYTHONPATH.

## Security Guidelines

- **No secrets in code:** Use environment variables or mounted configs
- **Input validation:** Always validate via Pydantic models
- **SQL injection:** Not applicable (we use Git, not SQL)
- **Path traversal:** Validate file paths in git_manager
- **CORS:** Configured in `main.py` for development (restrict in production)

## Questions?

- **Architecture questions:** See `docs/architecture/`
- **API questions:** Check `/docs` endpoint (FastAPI auto-docs)
- **Issues:** Create a GitHub issue with `question` label
- **Urgent:** Contact maintainers via GitHub

## Resources

- [Project README](README.md) - Full project overview
- [Quick Start](QUICKSTART.md) - Fast setup guide
- [Development Guide](docs/development.md) - Detailed dev workflow
- [Architecture Docs](docs/architecture/) - System design and ADRs

---

Thank you for contributing to AI-Agent-Framework! 🚀
