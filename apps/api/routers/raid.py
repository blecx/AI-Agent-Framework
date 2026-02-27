"""
RAID register router for managing Risks, Assumptions, Issues, and Dependencies.
Aligned with ISO 21500/21502 standards.
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional

from models import (
    RAIDItem,
    RAIDItemCreate,
    RAIDItemUpdate,
    RAIDItemList,
    RAIDType,
    RAIDStatus,
    RAIDPriority,
)
from services.avatar_service import infer_owner_avatar_url
from services.raid_service import RAIDService

router = APIRouter()

# Single instance of RAID service
raid_service = RAIDService()


def _enrich_owner_avatar(item: dict) -> dict:
    enriched = dict(item)
    enriched["owner_avatar_url"] = infer_owner_avatar_url(enriched.get("owner"))
    return enriched


# ============================================================================
# RAID Item CRUD Endpoints
# ============================================================================


@router.get("", response_model=RAIDItemList)
async def list_raid_items(
    project_key: str,
    request: Request,
    type: Optional[RAIDType] = Query(None, description="Filter by RAID type"),
    status: Optional[RAIDStatus] = Query(None, description="Filter by status"),
    owner: Optional[str] = Query(None, description="Filter by owner"),
    priority: Optional[RAIDPriority] = Query(None, description="Filter by priority"),
):
    """List and filter RAID items for a project."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    # Get all items
    all_items = raid_service.get_raid_items(project_key, git_manager)

    # Apply filters
    filtered_items = raid_service.filter_raid_items(
        all_items,
        raid_type=type.value if type else None,
        status=status.value if status else None,
        owner=owner,
        priority=priority.value if priority else None,
    )

    return RAIDItemList(
        items=[RAIDItem(**_enrich_owner_avatar(item)) for item in filtered_items],
        total=len(filtered_items),
        filtered_by={
            "type": type.value if type else None,
            "status": status.value if status else None,
            "owner": owner,
            "priority": priority.value if priority else None,
        },
    )


@router.get("/{raid_id}", response_model=RAIDItem)
async def get_raid_item(project_key: str, raid_id: str, request: Request):
    """Get a specific RAID item."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    item = raid_service.get_raid_item(project_key, raid_id, git_manager)
    if item is None:
        from domain.errors import not_found

        raise HTTPException(status_code=404, detail=not_found("RAID item", raid_id))

    return RAIDItem(**_enrich_owner_avatar(item))


@router.post("", response_model=RAIDItem, status_code=201)
async def create_raid_item(project_key: str, item: RAIDItemCreate, request: Request):
    """Create a new RAID item."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        created = raid_service.create_raid_item(
            project_key, item.model_dump(), git_manager
        )
        return RAIDItem(**_enrich_owner_avatar(created))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create RAID item: {str(e)}"
        )


@router.put("/{raid_id}", response_model=RAIDItem)
async def update_raid_item(
    project_key: str, raid_id: str, updates: RAIDItemUpdate, request: Request
):
    """Update an existing RAID item."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        updated = raid_service.update_raid_item(
            project_key, raid_id, updates.model_dump(exclude_unset=True), git_manager
        )
        return RAIDItem(**_enrich_owner_avatar(updated))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update RAID item: {str(e)}"
        )


@router.delete("/{raid_id}")
async def delete_raid_item(project_key: str, raid_id: str, request: Request):
    """Delete a RAID item."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    success = raid_service.delete_raid_item(project_key, raid_id, git_manager)
    if not success:
        raise HTTPException(status_code=404, detail=f"RAID item {raid_id} not found")

    return {"message": "RAID item deleted successfully"}


# ============================================================================
# Traceability Endpoints
# ============================================================================


@router.post("/{raid_id}/link-decision/{decision_id}")
async def link_raid_to_decision(
    project_key: str, raid_id: str, decision_id: str, request: Request
):
    """Link a RAID item to a governance decision."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    success = raid_service.link_raid_to_decision(
        project_key, raid_id, decision_id, git_manager
    )

    if not success:
        raise HTTPException(status_code=404, detail=f"RAID item {raid_id} not found")

    return {"message": "RAID item linked to decision successfully"}


@router.get("/by-decision/{decision_id}", response_model=RAIDItemList)
async def get_raid_items_by_decision(
    project_key: str, decision_id: str, request: Request
):
    """Get all RAID items linked to a specific decision."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    items = raid_service.get_raid_items_by_decision(
        project_key, decision_id, git_manager
    )

    return RAIDItemList(
        items=[RAIDItem(**_enrich_owner_avatar(item)) for item in items],
        total=len(items),
        filtered_by={"decision_id": decision_id},
    )
