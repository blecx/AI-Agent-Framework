"""
Projects router for creating and managing projects.
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List

from models import ProjectCreate, ProjectInfo, ProjectState

router = APIRouter()


@router.post("", response_model=ProjectInfo, status_code=201)
async def create_project(project: ProjectCreate, request: Request):
    """Create a new project with ISO21500 methodology."""
    git_manager = request.app.state.git_manager
    
    # Check if project already exists
    existing = git_manager.read_project_json(project.key)
    if existing:
        raise HTTPException(status_code=409, detail=f"Project {project.key} already exists")
    
    # Create project
    project_info = git_manager.create_project(
        project.key,
        {"key": project.key, "name": project.name}
    )
    
    # Log event
    git_manager.log_event(project.key, {
        "event_type": "project_created",
        "project_key": project.key,
        "project_name": project.name
    })
    
    return ProjectInfo(**project_info)


@router.get("/{project_key}/state", response_model=ProjectState)
async def get_project_state(project_key: str, request: Request):
    """Get aggregated project state."""
    git_manager = request.app.state.git_manager
    
    # Get project info
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")
    
    # Get artifacts
    artifacts = git_manager.list_artifacts(project_key)
    
    # Get last commit
    last_commit = git_manager.get_last_commit(project_key)
    
    return ProjectState(
        project_info=ProjectInfo(**project_info),
        artifacts=artifacts,
        last_commit=last_commit
    )


@router.get("", response_model=List[ProjectInfo])
async def list_projects(request: Request):
    """List all projects."""
    git_manager = request.app.state.git_manager
    
    projects = []
    base_path = git_manager.base_path
    
    # Iterate through directories
    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            project_json_path = item / "project.json"
            if project_json_path.exists():
                project_info = git_manager.read_project_json(item.name)
                if project_info:
                    projects.append(ProjectInfo(**project_info))
    
    return projects
