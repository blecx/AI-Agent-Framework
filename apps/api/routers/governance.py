"""
Governance router for managing governance metadata and decision logs.
Aligned with ISO 21500/21502 standards.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List

from models import (
    GovernanceMetadata,
    GovernanceMetadataUpdate,
    DecisionLogEntry,
    DecisionLogEntryCreate,
)
from services.governance_service import GovernanceService

router = APIRouter()

# Single instance of governance service
governance_service = GovernanceService()


# ============================================================================
# Governance Metadata Endpoints
# ============================================================================


@router.get("/metadata", response_model=GovernanceMetadata)
async def get_governance_metadata(project_key: str, request: Request):
    """Get governance metadata for a project."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    metadata = governance_service.get_governance_metadata(project_key, git_manager)
    if metadata is None:
        raise HTTPException(
            status_code=404,
            detail=f"Governance metadata not found for project '{project_key}'",
        )

    return GovernanceMetadata(**metadata)


@router.post("/metadata", response_model=GovernanceMetadata, status_code=201)
async def create_governance_metadata(
    project_key: str, metadata: GovernanceMetadata, request: Request
):
    """Create governance metadata for a project."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    # Check if metadata already exists
    existing = governance_service.get_governance_metadata(project_key, git_manager)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Governance metadata already exists for project '{project_key}'",
        )

    try:
        created = governance_service.create_governance_metadata(
            project_key, metadata.model_dump(), git_manager
        )
        return GovernanceMetadata(**created)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create governance metadata: {str(e)}"
        )


@router.put("/metadata", response_model=GovernanceMetadata)
async def update_governance_metadata(
    project_key: str, updates: GovernanceMetadataUpdate, request: Request
):
    """Update governance metadata for a project."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    try:
        updated = governance_service.update_governance_metadata(
            project_key, updates.model_dump(exclude_unset=True), git_manager
        )
        return GovernanceMetadata(**updated)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update governance metadata: {str(e)}"
        )


# ============================================================================
# Decision Log Endpoints
# ============================================================================


@router.get("/decisions", response_model=List[DecisionLogEntry])
async def get_decisions(project_key: str, request: Request):
    """Get all decision log entries for a project."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    decisions = governance_service.get_decisions(project_key, git_manager)
    return [DecisionLogEntry(**d) for d in decisions]


@router.get("/decisions/{decision_id}", response_model=DecisionLogEntry)
async def get_decision(project_key: str, decision_id: str, request: Request):
    """Get a specific decision log entry."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    decision = governance_service.get_decision(project_key, decision_id, git_manager)
    if decision is None:
        raise HTTPException(
            status_code=404, detail=f"Decision '{decision_id}' not found"
        )

    return DecisionLogEntry(**decision)


@router.post("/decisions", response_model=DecisionLogEntry, status_code=201)
async def create_decision(
    project_key: str, decision: DecisionLogEntryCreate, request: Request
):
    """Create a new decision log entry."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    try:
        created = governance_service.create_decision(
            project_key, decision.model_dump(), git_manager
        )
        return DecisionLogEntry(**created)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create decision: {str(e)}"
        )


@router.post("/decisions/{decision_id}/link-raid/{raid_id}")
async def link_decision_to_raid(
    project_key: str, decision_id: str, raid_id: str, request: Request
):
    """Link a decision to a RAID item."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    success = governance_service.link_decision_to_raid(
        project_key, decision_id, raid_id, git_manager
    )

    if not success:
        raise HTTPException(
            status_code=404, detail=f"Decision '{decision_id}' not found"
        )

    return {"message": "Decision linked to RAID item successfully"}
