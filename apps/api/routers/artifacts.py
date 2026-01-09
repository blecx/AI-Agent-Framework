"""
Artifacts router for listing and retrieving artifacts.
"""
from fastapi import APIRouter, HTTPException, Request, Response
from typing import List

from models import ArtifactInfo

router = APIRouter()


@router.get("", response_model=List[dict])
async def list_artifacts(project_key: str, request: Request):
    """List all artifacts for a project."""
    git_manager = request.app.state.git_manager
    
    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")
    
    artifacts = git_manager.list_artifacts(project_key)
    
    # Add version info (minimal for MVP)
    for artifact in artifacts:
        artifact["versions"] = [{"version": "current", "date": project_info.get("updated_at")}]
    
    return artifacts


@router.get("/{artifact_path:path}")
async def get_artifact(project_key: str, artifact_path: str, request: Request):
    """Get artifact content."""
    git_manager = request.app.state.git_manager
    
    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")
    
    # Read artifact
    content = git_manager.read_file(project_key, artifact_path)
    if content is None:
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_path} not found")
    
    # Return as markdown or plain text
    media_type = "text/markdown" if artifact_path.endswith(".md") else "text/plain"
    return Response(content=content, media_type=media_type)
