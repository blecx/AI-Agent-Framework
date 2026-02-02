"""
Template router for managing artifact templates.
Aligned with DDD architecture - thin controller pattern.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List

from domain.templates.models import Template, TemplateCreate, TemplateUpdate
from services.template_service import TemplateService


router = APIRouter()


def _get_template_service(request: Request) -> TemplateService:
    """Helper to instantiate TemplateService with git_manager from app state."""
    git_manager = request.app.state.git_manager
    return TemplateService(git_manager=git_manager, project_key="system")


# ============================================================================
# Template CRUD Endpoints
# ============================================================================


@router.post("", response_model=Template, status_code=201)
async def create_template(template_create: TemplateCreate, request: Request):
    """
    Create a new template.

    Returns:
        Created template with generated ID

    Raises:
        HTTPException 400: Invalid template data or duplicate ID
        HTTPException 422: Validation error (Pydantic)
    """
    service = _get_template_service(request)
    try:
        return service.create_template(template_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[Template])
async def list_templates(request: Request):
    """
    List all templates.

    Returns:
        List of all templates (empty list if none exist)
    """
    service = _get_template_service(request)
    return service.list_templates()


@router.get("/{template_id}", response_model=Template)
async def get_template(template_id: str, request: Request):
    """
    Get template by ID.

    Args:
        template_id: Unique template identifier

    Returns:
        Template object

    Raises:
        HTTPException 404: Template not found
    """
    service = _get_template_service(request)
    template = service.get_template(template_id)
    if not template:
        from domain.errors import not_found

        raise HTTPException(status_code=404, detail=not_found("Template", template_id))
    return template


@router.put("/{template_id}", response_model=Template)
async def update_template(
    template_id: str, template_update: TemplateUpdate, request: Request
):
    """
    Update an existing template.

    Args:
        template_id: Unique template identifier
        template_update: Fields to update (partial update supported)

    Returns:
        Updated template object

    Raises:
        HTTPException 404: Template not found
        HTTPException 400: Invalid update data
    """
    service = _get_template_service(request)
    try:
        updated = service.update_template(template_id, template_update)
        if not updated:
            from domain.errors import not_found

            raise HTTPException(
                status_code=404, detail=not_found("Template", template_id)
            )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{template_id}", status_code=204)
async def delete_template(template_id: str, request: Request):
    """
    Delete a template.

    Args:
        template_id: Unique template identifier

    Raises:
        HTTPException 404: Template not found
    """
    service = _get_template_service(request)
    success = service.delete_template(template_id)
    if not success:
        from domain.errors import not_found

        raise HTTPException(status_code=404, detail=not_found("Template", template_id))
    return None
