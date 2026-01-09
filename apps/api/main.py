"""
Main FastAPI application for ISO 21500 Project Management AI Agent System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from .routers import projects, commands, artifacts
from .services.git_manager import GitManager
from .services.llm_service import LLMService


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
    title="ISO 21500 Project Management AI Agent",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(commands.router, prefix="/projects/{project_key}/commands", tags=["commands"])
app.include_router(artifacts.router, prefix="/projects/{project_key}/artifacts", tags=["artifacts"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ISO 21500 Project Management AI Agent",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    docs_path = os.getenv("PROJECT_DOCS_PATH", "/projectDocs")
    return {
        "status": "healthy",
        "docs_path": docs_path,
        "docs_exists": os.path.exists(docs_path),
        "docs_is_git": os.path.exists(os.path.join(docs_path, ".git"))
    }
