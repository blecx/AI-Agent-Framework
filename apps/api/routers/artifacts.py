"""
Artifacts router for listing, retrieving, and generating artifacts.
"""

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()


# ============================================================================
# Request Models
# ============================================================================


class GenerateArtifactRequest(BaseModel):
    """Request model for generating artifact from template."""

    template_id: str
    context: Dict[str, Any]


class GenerateFromBlueprintRequest(BaseModel):
    """Request model for generating artifacts from blueprint."""

    blueprint_id: str
    context: Dict[str, Any] = {}


@router.get("", response_model=List[dict])
async def list_artifacts(project_key: str, request: Request):
    """List all artifacts for a project."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    artifacts = git_manager.list_artifacts(project_key)

    # Add version info (minimal for MVP)
    for artifact in artifacts:
        artifact["versions"] = [
            {"version": "current", "date": project_info.get("updated_at")}
        ]

    return artifacts


@router.get("/{artifact_path:path}")
async def get_artifact(project_key: str, artifact_path: str, request: Request):
    """Get artifact content."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    # Read artifact
    content = git_manager.read_file(project_key, artifact_path)
    if content is None:
        raise HTTPException(
            status_code=404, detail=f"Artifact '{artifact_path}' not found"
        )

    # Return as markdown or plain text
    media_type = "text/markdown" if artifact_path.endswith(".md") else "text/plain"
    return Response(content=content, media_type=media_type)


# ============================================================================
# POST /artifacts/generate - Generate from Template
# ============================================================================


@router.post("/generate", status_code=201)
async def generate_artifact(
    project_key: str, request_body: GenerateArtifactRequest, request: Request
):
    """
    Generate artifact from template.

    Args:
        project_key: Project identifier
        request_body: Template ID and context variables
        request: FastAPI request object

    Returns:
        Generated artifact details (path, content, metadata)

    Raises:
        404: Project or template not found
        400: Invalid context data (validation error)
        422: Invalid request body
    """
    from services.artifact_generation_service import (
        ArtifactGenerationService,
        ArtifactGenerationError,
        ValidationError,
    )
    from services.template_service import TemplateService
    from services.blueprint_service import BlueprintService

    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    # Initialize services
    template_service = TemplateService(git_manager)
    blueprint_service = BlueprintService(git_manager)
    generation_service = ArtifactGenerationService(
        template_service, blueprint_service, git_manager
    )

    # Generate artifact
    try:
        result = generation_service.generate_from_template(
            request_body.template_id, project_key, request_body.context
        )
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ArtifactGenerationError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# POST /artifacts/generate-from-blueprint - Generate from Blueprint
# ============================================================================


@router.post("/generate-from-blueprint", status_code=201)
async def generate_from_blueprint(
    project_key: str, request_body: GenerateFromBlueprintRequest, request: Request
):
    """
    Generate all artifacts from blueprint.

    Args:
        project_key: Project identifier
        request_body: Blueprint ID and optional base context
        request: FastAPI request object

    Returns:
        List of generated artifacts with paths and metadata

    Raises:
        404: Project or blueprint not found
        400: Generation errors (partial failures included in response)
    """
    from services.artifact_generation_service import (
        ArtifactGenerationService,
        ArtifactGenerationError,
    )
    from services.template_service import TemplateService
    from services.blueprint_service import BlueprintService

    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    # Initialize services
    template_service = TemplateService(git_manager)
    blueprint_service = BlueprintService(git_manager)
    generation_service = ArtifactGenerationService(
        template_service, blueprint_service, git_manager
    )

    # Generate from blueprint
    try:
        results = generation_service.generate_from_blueprint(
            request_body.blueprint_id, project_key, request_body.context
        )
        return {
            "blueprint_id": request_body.blueprint_id,
            "generated_artifacts": results,
        }
    except ArtifactGenerationError as e:
        raise HTTPException(status_code=404, detail=str(e))
