import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

"""Main FastAPI application for ISO 21500 Project Management AI Agent System."""

try:
    # Package execution (e.g. `uvicorn apps.api.main:app`)
    from .routers import (
        projects,
        commands,
        artifacts,
        governance,
        raid,
        workflow,
        skills,
        proposals,
        commands_global,
        templates,
        blueprints,
        health,
    )
    from .services.git_manager import GitManager
    from .services.llm_service import LLMService
    from .services.audit_service import AuditService
    from .services.monitoring_service import (
        MetricsCollector,
        REQUEST_IN_PROGRESS,
    )
except ImportError:
    # Local execution from apps/api (e.g. `uvicorn main:app`)
    from routers import (
        projects,
        commands,
        artifacts,
        governance,
        raid,
        workflow,
        skills,
        proposals,
        commands_global,
        templates,
        blueprints,
        health,
    )
    from services.git_manager import GitManager
    from services.llm_service import LLMService
    from services.audit_service import AuditService
    from services.monitoring_service import (
        MetricsCollector,
        REQUEST_IN_PROGRESS,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    # Initialize project docs git repository
    docs_path = os.getenv("PROJECT_DOCS_PATH", "/projectDocs")
    
    # Initialize git manager with error handling
    try:
        git_manager = GitManager(docs_path)
        git_manager.ensure_repository()
        app.state.git_manager = git_manager
    except Exception as e:
        # Log error but don't fail startup - health checks will report this
        # This handles cases like missing Git, permission issues, or mounted volumes
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Git manager initialization failed: {e}", exc_info=True)
        print(f"Warning: Git manager initialization failed: {e}")
        print(f"API will start but project document management may be unavailable.")
        app.state.git_manager = None

    # Store services in app state
    app.state.llm_service = LLMService()
    app.state.audit_service = AuditService()

    yield

    # Cleanup if needed
    pass


app = FastAPI(
    title="ISO 21500 Project Management AI Agent", version="1.0.0", lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Monitoring Middleware
# ============================================================================


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Middleware to collect request metrics.

    Tracks:
    - Request count by method/endpoint/status
    - Request duration
    - Requests in progress
    - Correlation ID for tracing
    """
    # Generate correlation ID
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id

    # Track in-progress requests
    REQUEST_IN_PROGRESS.inc()

    start_time = time.time()

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Record metrics
        MetricsCollector.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response

    except Exception as e:
        duration = time.time() - start_time

        # Record error metrics
        MetricsCollector.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=500,
            duration=duration,
        )
        MetricsCollector.record_error(
            error_type=type(e).__name__,
            endpoint=request.url.path,
        )

        raise

    finally:
        REQUEST_IN_PROGRESS.dec()


# ============================================================================
# Metrics Endpoint
# ============================================================================


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in OpenMetrics format for Prometheus scraping.
    """
    return Response(
        content=MetricsCollector.generate_metrics(),
        media_type=MetricsCollector.get_content_type(),
    )


# ============================================================================
# API v1 Routes (Versioned)
# ============================================================================

# Include versioned routers under /api/v1
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects-v1"])
app.include_router(
    commands_global.router, prefix="/api/v1/commands", tags=["commands-global-v1"]
)
app.include_router(
    commands.router,
    prefix="/api/v1/projects/{project_key}/commands",
    tags=["commands-v1"],
)
app.include_router(
    proposals.router,
    prefix="/api/v1/projects/{project_key}/proposals",
    tags=["proposals-v1"],
)
app.include_router(
    artifacts.router,
    prefix="/api/v1/projects/{project_key}/artifacts",
    tags=["artifacts-v1"],
)
app.include_router(
    governance.router,
    prefix="/api/v1/projects/{project_key}/governance",
    tags=["governance-v1"],
)
app.include_router(
    raid.router, prefix="/api/v1/projects/{project_key}/raid", tags=["raid-v1"]
)
app.include_router(workflow.router, prefix="/api/v1/projects", tags=["workflow-v1"])
app.include_router(skills.router, prefix="/api/v1/agents", tags=["skills-v1"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates-v1"])
app.include_router(
    blueprints.router, prefix="/api/v1/blueprints", tags=["blueprints-v1"]
)
app.include_router(health.router, tags=["health"])

# ============================================================================
# Backward Compatibility Routes (Deprecated - use /api/v1/ instead)
# ============================================================================

# Legacy unversioned routes for backward compatibility
# These will be removed in a future major version
app.include_router(projects.router, prefix="/projects", tags=["projects (deprecated)"])
app.include_router(
    commands_global.router, prefix="/commands", tags=["commands-global (deprecated)"]
)
app.include_router(
    commands.router,
    prefix="/projects/{project_key}/commands",
    tags=["commands (deprecated)"],
)
app.include_router(
    proposals.router,
    prefix="/projects/{project_key}/proposals",
    tags=["proposals (deprecated)"],
)
app.include_router(
    artifacts.router,
    prefix="/projects/{project_key}/artifacts",
    tags=["artifacts (deprecated)"],
)
app.include_router(
    governance.router,
    prefix="/projects/{project_key}/governance",
    tags=["governance (deprecated)"],
)
app.include_router(
    raid.router, prefix="/projects/{project_key}/raid", tags=["raid (deprecated)"]
)
app.include_router(workflow.router, prefix="/projects", tags=["workflow (deprecated)"])
app.include_router(skills.router, prefix="/agents", tags=["skills (deprecated)"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ISO 21500 Project Management AI Agent",
        "version": "1.0.0",
        "api_version": "v1",
    }


@app.get("/info")
async def info():
    """Info endpoint (returns name and version)."""
    return {
        "name": "ISO 21500 Project Management AI Agent",
        "version": "1.0.0",
    }


@app.get("/api/v1/info")
async def info_v1():
    """Info endpoint (versioned)."""
    return {
        "name": "ISO 21500 Project Management AI Agent",
        "version": "1.0.0",
        "api_version": "v1",
    }
