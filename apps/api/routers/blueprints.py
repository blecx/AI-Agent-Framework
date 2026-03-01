"""
Blueprint router for managing project blueprints.
Aligned with DDD architecture - thin controller pattern.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List

try:
    from ..domain.blueprints.models import (
        Blueprint,
        BlueprintCreate,
        BlueprintUpdate,
    )
    from ..domain.errors import not_found
    from ..services.blueprint_service import BlueprintService
except ImportError:
    from domain.blueprints.models import (
        Blueprint,
        BlueprintCreate,
        BlueprintUpdate,
    )
    from domain.errors import not_found
    from services.blueprint_service import BlueprintService


router = APIRouter()


def _get_blueprint_service(request: Request) -> BlueprintService:
    """Helper to instantiate BlueprintService with git_manager from app state."""
    git_manager = request.app.state.git_manager
    return BlueprintService(git_manager=git_manager, project_key="system")


# ============================================================================
# Blueprint CRUD Endpoints
# ============================================================================


@router.post("", response_model=Blueprint, status_code=201)
async def create_blueprint(blueprint_create: BlueprintCreate, request: Request):
    """
    Create a new blueprint.

    Returns:
        Created blueprint

    Raises:
        HTTPException 400: Invalid blueprint data or duplicate ID
        HTTPException 422: Validation error (Pydantic)
    """
    service = _get_blueprint_service(request)
    try:
        return service.create_blueprint(blueprint_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[Blueprint])
async def list_blueprints(request: Request):
    """
    List all blueprints.

    Returns:
        List of all blueprints (empty list if none exist)
    """
    service = _get_blueprint_service(request)
    return service.list_blueprints()


@router.get("/{blueprint_id}", response_model=Blueprint)
async def get_blueprint(blueprint_id: str, request: Request):
    """
    Get blueprint by ID.

    Args:
        blueprint_id: Blueprint ID to retrieve

    Returns:
        Blueprint data

    Raises:
        HTTPException 404: Blueprint not found
    """
    service = _get_blueprint_service(request)
    blueprint = service.get_blueprint(blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail=not_found("Blueprint", blueprint_id))
    return blueprint


@router.put("/{blueprint_id}", response_model=Blueprint)
async def update_blueprint(
    blueprint_id: str, blueprint_update: BlueprintUpdate, request: Request
):
    """
    Update an existing blueprint.

    Args:
        blueprint_id: Blueprint ID to update
        blueprint_update: Fields to update

    Returns:
        Updated blueprint

    Raises:
        HTTPException 400: Invalid update data
        HTTPException 404: Blueprint not found
    """
    service = _get_blueprint_service(request)
    try:
        return service.update_blueprint(blueprint_id, blueprint_update)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{blueprint_id}", status_code=204)
async def delete_blueprint(blueprint_id: str, request: Request):
    """
    Delete a blueprint.

    Args:
        blueprint_id: Blueprint ID to delete

    Raises:
        HTTPException 404: Blueprint not found
    """
    service = _get_blueprint_service(request)
    try:
        service.delete_blueprint(blueprint_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
