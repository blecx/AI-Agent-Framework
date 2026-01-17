import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
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
    )
    from .services.git_manager import GitManager
    from .services.llm_service import LLMService
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
    )
    from services.git_manager import GitManager
    from services.llm_service import LLMService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    # Initialize project docs git repository
    docs_path = os.getenv("PROJECT_DOCS_PATH", "/projectDocs")
    git_manager = GitManager(docs_path)
    git_manager.ensure_repository()

    # Store in app state
    app.state.git_manager = git_manager
    app.state.llm_service = LLMService()

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


@app.get("/health")
async def health():
    """Detailed health check (deprecated - use /api/v1/health)."""
    docs_path = os.getenv("PROJECT_DOCS_PATH", "/projectDocs")
    return {
        "status": "healthy",
        "docs_path": docs_path,
        "docs_exists": os.path.exists(docs_path),
        "docs_is_git": os.path.exists(os.path.join(docs_path, ".git")),
    }


@app.get("/api/v1/health")
async def health_v1():
    """Detailed health check (versioned)."""
    docs_path = os.getenv("PROJECT_DOCS_PATH", "/projectDocs")
    return {
        "status": "healthy",
        "docs_path": docs_path,
        "docs_exists": os.path.exists(docs_path),
        "docs_is_git": os.path.exists(os.path.join(docs_path, ".git")),
        "api_version": "v1",
    }
