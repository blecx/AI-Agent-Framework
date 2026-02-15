"""
Projects router for creating and managing projects.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timezone
import json

from models import ProjectCreate, ProjectInfo, ProjectState, ProjectUpdate
from services.workflow_service import WorkflowService

router = APIRouter()
workflow_service = WorkflowService()


@router.post("", response_model=ProjectInfo, status_code=201)
async def create_project(project: ProjectCreate, request: Request):
    """Create a new project with ISO21500 methodology."""
    git_manager = request.app.state.git_manager

    # Check if project already exists
    existing = git_manager.read_project_json(project.key)
    if existing:
        raise HTTPException(
            status_code=409, detail=f"Project '{project.key}' already exists"
        )

    # Create project
    project_info = git_manager.create_project(
        project.key,
        {
            "key": project.key,
            "name": project.name,
            "description": project.description,
        },
    )

    # Initialize workflow state
    workflow_service.initialize_workflow_state(project.key, git_manager)

    # Log event
    git_manager.log_event(
        project.key,
        {
            "event_type": "project_created",
            "project_key": project.key,
            "project_name": project.name,
            "project_description": project.description,
        },
    )

    return ProjectInfo(**project_info)


@router.get("/{project_key}/state", response_model=ProjectState)
async def get_project_state(project_key: str, request: Request):
    """Get aggregated project state."""
    git_manager = request.app.state.git_manager

    # Get project info
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        from domain.errors import not_found

        raise HTTPException(status_code=404, detail=not_found("Project", project_key))

    # Get artifacts
    artifacts = git_manager.list_artifacts(project_key)

    # Get last commit
    last_commit = git_manager.get_last_commit(project_key)

    return ProjectState(
        project_info=ProjectInfo(**project_info),
        artifacts=artifacts,
        last_commit=last_commit,
    )


@router.get("", response_model=List[ProjectInfo])
async def list_projects(request: Request):
    """List all projects."""
    git_manager = request.app.state.git_manager

    projects = []
    base_path = git_manager.base_path

    # Iterate through directories
    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            project_json_path = item / "project.json"
            if project_json_path.exists():
                project_info = git_manager.read_project_json(item.name)
                if project_info:
                    projects.append(ProjectInfo(**project_info))

    return projects


@router.get("/{project_key}", response_model=ProjectInfo)
async def get_project(project_key: str, request: Request):
    """Get a specific project by key."""
    git_manager = request.app.state.git_manager

    # Get project info
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    return ProjectInfo(**project_info)


@router.put("/{project_key}", response_model=ProjectInfo)
async def update_project(project_key: str, update: ProjectUpdate, request: Request):
    """Update project metadata."""
    git_manager = request.app.state.git_manager

    # Check if project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    # Update fields that are provided
    if update.name is not None:
        project_info["name"] = update.name
    if update.description is not None:
        project_info["description"] = update.description
    if update.methodology is not None:
        project_info["methodology"] = update.methodology

    # Update timestamp
    project_info["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Write updated project.json
    git_manager.write_file(
        project_key, "project.json", json.dumps(project_info, indent=2)
    )

    # Commit the change
    git_manager.commit_changes(
        project_key, f"[{project_key}] Update project metadata", ["project.json"]
    )

    # Log event
    git_manager.log_event(
        project_key,
        {
            "event_type": "project_updated",
            "project_key": project_key,
            "updates": update.model_dump(exclude_none=True),
        },
    )

    return ProjectInfo(**project_info)


@router.delete("/{project_key}", status_code=204)
async def delete_project(project_key: str, request: Request):
    """Delete a project (soft-delete with audit trail)."""
    git_manager = request.app.state.git_manager

    # Check if project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    # Log event before deletion
    git_manager.log_event(
        project_key,
        {
            "event_type": "project_deleted",
            "project_key": project_key,
            "project_name": project_info.get("name"),
        },
    )

    # Soft-delete: Mark project as deleted in metadata
    project_info["deleted"] = True
    project_info["deleted_at"] = datetime.now(timezone.utc).isoformat()
    git_manager.write_file(
        project_key, "project.json", json.dumps(project_info, indent=2)
    )

    # Commit the change
    git_manager.commit_changes(
        project_key, f"[{project_key}] Mark project as deleted", ["project.json"]
    )

    # Return 204 No Content
    return None
