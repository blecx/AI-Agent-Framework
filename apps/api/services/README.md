# Service Layer

## Overview

The service layer sits between the domain layer and the API layer in our Domain-Driven Design (DDD) architecture. Services orchestrate business logic, coordinate between domains, and integrate with external systems.

**Architectural Position:**
```
API Layer (routers/) → Service Layer (services/) → Domain Layer (domain/)
                     ↓
            Infrastructure (git, LLM, external APIs)
```

## Responsibilities

The service layer handles:

1. **Application Logic**: Orchestrate workflows across multiple domains
2. **External Integration**: Adapt external systems (LLM, Git) to domain needs
3. **Transaction Coordination**: Manage multi-step operations with rollback capability
4. **Cross-Cutting Concerns**: Audit logging, validation, error handling
5. **Abstraction**: Shield API layer from infrastructure details

**What Services Should NOT Do:**
- Contain HTTP/REST concerns (that's the router's job)
- Include domain business rules (that belongs in domain models)
- Couple directly to frameworks (use abstractions/interfaces)

## Dependency Injection

We use FastAPI's application state (`app.state`) for service lifecycle management.

### Initialization (Lifespan)

Services are initialized once at application startup in `main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    docs_path = os.getenv("PROJECT_DOCS_PATH", "/projectDocs")
    
    # Initialize singleton services
    app.state.git_manager = GitManager(docs_path)
    app.state.git_manager.ensure_repository()
    app.state.llm_service = LLMService()
    app.state.audit_service = AuditService()
    
    yield
    # Cleanup if needed
```

### Request-Scoped Access

Routers access services via `request.app.state`:

```python
@router.post("", response_model=ProjectInfo)
async def create_project(project: ProjectCreate, request: Request):
    git_manager = request.app.state.git_manager
    audit_service = request.app.state.audit_service
    
    # Use services...
    project_info = git_manager.create_project(...)
    audit_service.log_audit_event(...)
```

**Why Not FastAPI `Depends()`?**
- Simpler for singleton services (no factory functions needed)
- Explicit service access in function signatures
- Easier to test (mock `request.app.state` directly)
- Avoids circular dependency issues

## Service Lifecycle

1. **Startup**: Services initialized in `lifespan()` function
2. **Request**: Services accessed via `request.app.state`
3. **Shutdown**: Cleanup in `lifespan()` context manager exit
4. **Stateless**: Services should be stateless or use external state stores (Git repo, Redis)

## Common Service Patterns

### 1. Repository Pattern (GitManager)

**Purpose**: Abstraction over data persistence (Git repository as storage)

**Example**: `git_manager.py`

```python
class GitManager:
    """Manages git operations for project documents."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.repo = None
    
    def create_project(self, key: str, data: Dict) -> Dict:
        """Create project folder and commit initial data."""
        # Abstract away Git implementation details
        
    def read_project_json(self, key: str) -> Optional[Dict]:
        """Read project metadata from Git."""
        
    def commit_artifact(self, key: str, path: str, content: str, msg: str):
        """Version-control artifact with Git commit."""
```

**When to Use:**
- Abstracting database/storage implementation
- Need to swap persistence layer (Git → SQL → NoSQL)
- Centralizing data access logic

**Benefits:**
- Decouples domain from infrastructure
- Easier to test (mock repository interface)
- Supports multiple storage backends

**Related ADR**: [0001-docs-repo-mounted-git.md](../../docs/adr/0001-docs-repo-mounted-git.md)

### 2. Strategy Pattern (CommandService)

**Purpose**: Pluggable algorithms/handlers for different command types

**Example**: `command_service.py`

```python
class CommandService:
    """Service for handling project commands with pluggable handlers."""
    
    def __init__(self):
        # Registry of command handlers (Strategy objects)
        self.handlers = {
            "assess_gaps": AssessGapsHandler(),
            "generate_artifact": GenerateArtifactHandler(),
            "generate_plan": GeneratePlanHandler(),
        }
    
    async def propose_command(self, command: str, params: Dict, ...) -> Dict:
        """Delegate to appropriate handler based on command type."""
        if command not in self.handlers:
            raise ValueError(f"Unknown command: {command}")
        
        handler = self.handlers[command]
        return await handler.propose(project_key, params, llm_service, git_manager)
```

**When to Use:**
- Multiple algorithms for the same operation
- Need to add new behaviors without modifying core service
- Behavior selected at runtime based on input

**Benefits:**
- Open/Closed Principle (extend without modifying)
- Easier to test individual handlers
- Clear separation of concerns

**Related ADR**: [0003-propose-apply-before-commit.md](../../docs/adr/0003-propose-apply-before-commit.md)

### 3. Facade Pattern (AuditService)

**Purpose**: Simplified interface to a complex subsystem

**Example**: `audit_service.py`

```python
class AuditService:
    """
    Backward-compatible facade for audit operations.
    Delegates to focused services: AuditEventLogger, AuditRulesEngine, AuditOrchestrator.
    """
    
    def __init__(self):
        self.event_logger = AuditEventLogger()
        self.rules_engine = AuditRulesEngine()
        self.orchestrator = AuditOrchestrator(self.event_logger, self.rules_engine)
    
    def log_audit_event(self, project_key: str, event_type: str, ...) -> Dict:
        """Delegate to AuditEventLogger."""
        return self.event_logger.log_audit_event(...)
    
    def get_audit_events(self, project_key: str, ...) -> List[Dict]:
        """Delegate to AuditOrchestrator."""
        return self.orchestrator.get_audit_events(...)
```

**When to Use:**
- Complex subsystem with multiple collaborating classes
- Need backward compatibility during refactoring
- Simplifying API for common use cases

**Benefits:**
- Reduces coupling between subsystems
- Easier migration path (keep old API while refactoring internals)
- Simplifies client code

### 4. External Integration Pattern (LLMService)

**Purpose**: Adapt external systems to domain interfaces

**Example**: `llm_service.py`

```python
class LLMService:
    """Service for interacting with LLM via HTTP."""
    
    def __init__(self):
        self.config = self._load_config()
        self.client = httpx.AsyncClient(timeout=self.config.get("timeout", 120))
        self.jinja_env = Environment(loader=FileSystemLoader(...))
    
    async def chat_completion(self, messages: List[Dict], ...) -> str:
        """Make HTTP request to LLM and return response."""
        url = f"{self.config['base_url']}/chat/completions"
        # Handle HTTP, retries, errors, etc.
        
    async def generate_from_template(self, template_name: str, context: Dict) -> str:
        """Render prompt template and get LLM completion."""
        # Combine templating + LLM call
```

**When to Use:**
- Integrating with external APIs (LLM, payment, email)
- Need to swap providers (OpenAI → Anthropic → local LLM)
- Handling protocol-specific concerns (HTTP, retries, auth)

**Benefits:**
- Isolates external dependencies
- Easier to mock in tests
- Centralized configuration and error handling

**Related ADR**: [0002-llm-http-adapter-json-config.md](../../docs/adr/0002-llm-http-adapter-json-config.md)

## Service Directory Structure

```
services/
├── README.md                          # This file
├── __init__.py
│
# Application Services (orchestration)
├── command_service.py                 # Command execution (Strategy pattern)
├── proposal_service.py                # Proposal lifecycle management
├── workflow_service.py                # Workflow state transitions
├── raid_service.py                    # RAID register operations
├── governance_service.py              # Governance framework operations
├── template_service.py                # Template CRUD operations
├── blueprint_service.py               # Blueprint CRUD operations
├── artifact_generation_service.py     # Artifact generation logic
├── diff_service.py                    # Diff calculation for proposals
│
# Infrastructure Services
├── git_manager.py                     # Git repository abstraction (Repository pattern)
├── llm_service.py                     # LLM HTTP adapter (External Integration)
│
# Audit Subsystem
├── audit_service.py                   # Audit facade (Facade pattern)
└── audit/                             # Focused audit services
    ├── event_logger.py                # Event logging
    ├── rules_engine.py                # Validation rules
    └── orchestrator.py                # Coordination logic
│
# Command Handlers (Strategy implementations)
└── commands/
    ├── assess_gaps.py                 # Gap assessment handler
    ├── generate_artifact.py           # Artifact generation handler
    └── generate_plan.py               # Plan generation handler
```

## Testing Services

### Unit Tests (Isolated)

Mock dependencies to test service logic in isolation:

```python
import pytest
from unittest.mock import Mock, AsyncMock

def test_command_service_propose_unknown_command():
    """Test error handling for unknown commands."""
    service = CommandService()
    
    with pytest.raises(ValueError, match="Unknown command"):
        await service.propose_command(
            project_key="TEST",
            command="invalid_command",
            params={},
            llm_service=Mock(),
            git_manager=Mock(),
        )

@pytest.mark.asyncio
async def test_llm_service_chat_completion():
    """Test LLM service with mocked HTTP client."""
    service = LLMService()
    service.client = AsyncMock()
    service.client.post.return_value.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    
    result = await service.chat_completion([{"role": "user", "content": "Hi"}])
    assert result == "Test response"
```

### Integration Tests (With Real Dependencies)

Test service interactions with real infrastructure:

```python
import pytest
from pathlib import Path
from services.git_manager import GitManager

@pytest.fixture
def temp_git_repo(tmp_path):
    """Create temporary Git repository."""
    return GitManager(str(tmp_path / "docs"))

def test_git_manager_create_project(temp_git_repo):
    """Test project creation with real Git operations."""
    git_manager = temp_git_repo
    git_manager.ensure_repository()
    
    project = git_manager.create_project("TEST-001", {"name": "Test Project"})
    
    assert project["key"] == "TEST-001"
    assert (git_manager.base_path / "TEST-001" / "project.json").exists()
    
    # Verify Git commit
    commits = list(git_manager.repo.iter_commits())
    assert len(commits) >= 1
    assert "TEST-001" in commits[0].message
```

### Testing Best Practices

1. **Mock External Dependencies**: Don't call real LLM APIs or external services in tests
2. **Use Fixtures**: Create reusable test fixtures for common setup
3. **Test Error Paths**: Verify error handling and edge cases
4. **Integration Tests Sparingly**: Most tests should be fast unit tests
5. **Parameterize Tests**: Use `@pytest.mark.parametrize` for multiple scenarios
6. **Async Tests**: Use `@pytest.mark.asyncio` for async service methods

## Best Practices

### 1. Single Responsibility Principle (SRP)

Each service should have one clear purpose:

✅ **Good**: `TemplateService` (CRUD for templates only)  
❌ **Bad**: `ProjectManagementService` (does everything)

### 2. Stateless Services

Services should be stateless or delegate state to external stores:

✅ **Good**: Store proposals in Git, Redis, or database  
❌ **Bad**: Store proposals in `self.proposals` dict (lost on restart)

### 3. Dependency Injection

Accept dependencies as constructor/method parameters:

✅ **Good**:
```python
async def propose_command(self, llm_service, git_manager):
    # Injected dependencies
```

❌ **Bad**:
```python
async def propose_command(self):
    llm_service = LLMService()  # Hard-coded dependency
```

### 4. Error Handling

Translate infrastructure errors to domain errors:

✅ **Good**:
```python
try:
    result = git_manager.read_project_json(key)
except GitError as e:
    raise ValueError(f"Project not found: {key}") from e
```

❌ **Bad**: Let Git exceptions bubble up to API layer

### 5. Logging

Log at service layer for observability:

```python
import logging

logger = logging.getLogger(__name__)

class TemplateService:
    def create_template(self, template: Template) -> Template:
        logger.info("Creating template: %s", template.id)
        # ...
        logger.debug("Template created successfully: %s", template.id)
```

### 6. Template Persistence Contract

`TemplateService` persists templates under each project repository using a stable JSON-file layout:

- Directory: `.templates/`
- File pattern: `.templates/{template_id}.json`
- Serialization: `Template.model_dump()` JSON with `indent=2`
- Commit model: one commit per create/update/delete operation with `[TEMPLATE]` prefix

This format is intentionally simple and deterministic so downstream readers, migrations, and audits can rely on predictable paths and payload shape.

### 7. Artifact Generation Flow

`ArtifactGenerationService` orchestrates template/blueprint-driven rendering with validation and persistence.

**Required inputs (`generate_from_template`)**
- `template_id`: existing template identifier
- `project_key`: target project repository key
- `context`: JSON-serializable payload satisfying the template JSON Schema

**Flow**
1. Resolve template by `template_id`
2. Sanitize and enrich context (`project_key`, `generated_at`)
3. Validate context against template schema
4. Render markdown via Jinja2
5. Persist to `artifacts/{artifact_type}.md`
6. Commit generated artifact through `GitManager`

**Blueprint mode (`generate_from_blueprint`)**
- Resolves the blueprint, iterates required template IDs, and generates each artifact.
- Missing references or validation/rendering failures are returned as actionable error entries per template.

## Related Documentation

### Domain Layer
- [Templates Domain](../domain/templates/README.md)
- [Audit Domain](../domain/audit/README.md)
- [RAID Domain](../domain/raid/README.md)
- [Proposals Domain](../domain/proposals/README.md)
- [Workflow Domain](../domain/workflow/README.md)

### Architecture Decision Records (ADRs)
- [ADR-0001: Docs Repo as Mounted Git](../../docs/adr/0001-docs-repo-mounted-git.md)
- [ADR-0002: LLM HTTP Adapter JSON Config](../../docs/adr/0002-llm-http-adapter-json-config.md)
- [ADR-0003: Propose/Apply Before Commit](../../docs/adr/0003-propose-apply-before-commit.md)

### Development Guides
- [Development Guide](../../docs/development.md)
- [API Documentation](../../docs/api/README.md)
- [Testing Guide](../../docs/testing.md)

## Contributing

When adding new services:

1. **Follow Established Patterns**: Use Repository, Strategy, Facade, or External Integration patterns
2. **Keep Services Focused**: Target < 200 lines per service (split if larger)
3. **Document Public Methods**: Include docstrings with parameter descriptions
4. **Add Tests**: Unit tests for logic, integration tests for infrastructure
5. **Update This README**: Document new service patterns or conventions
6. **Link to ADRs**: Reference relevant architectural decisions

For detailed contribution guidelines, see [CONTRIBUTING.md](../../docs/CONTRIBUTING.md).
