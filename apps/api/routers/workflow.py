"""
Workflow router for managing project workflow state transitions and audit events.
Aligned with ISO 21500 standards.
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional

from models import (
    WorkflowStateInfo,
    WorkflowStateUpdate,
    AuditEventList,
)
from services.workflow_service import WorkflowService
from services.audit_service import AuditService

router = APIRouter()

# Service instances
workflow_service = WorkflowService()
audit_service = AuditService()


# ============================================================================
# Workflow State Endpoints
# ============================================================================


@router.get("/{project_key}/workflow/state", response_model=WorkflowStateInfo)
async def get_workflow_state(project_key: str, request: Request):
    """Get current workflow state for a project."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    state = workflow_service.get_workflow_state(project_key, git_manager)
    return WorkflowStateInfo(**state)


@router.patch("/{project_key}/workflow/state", response_model=WorkflowStateInfo)
async def transition_workflow_state(
    project_key: str, state_update: WorkflowStateUpdate, request: Request
):
    """
    Transition project workflow state.

    Validates the requested state transition and emits an audit event.
    """
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        # Attempt state transition
        new_state = workflow_service.transition_state(
            project_key=project_key,
            to_state=state_update.to_state.value,
            actor=state_update.actor,
            reason=state_update.reason,
            git_manager=git_manager,
            correlation_id=request.headers.get("X-Correlation-ID"),
        )

        return WorkflowStateInfo(**new_state)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to transition workflow state: {str(e)}"
        )


@router.get("/{project_key}/workflow/allowed-transitions")
async def get_allowed_transitions(project_key: str, request: Request):
    """Get list of allowed state transitions from current state."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    state = workflow_service.get_workflow_state(project_key, git_manager)
    allowed = workflow_service.get_allowed_transitions(project_key, git_manager)

    return {
        "current_state": state["current_state"],
        "allowed_transitions": allowed,
    }


# ============================================================================
# Audit Events Endpoints
# ============================================================================


@router.get("/{project_key}/audit-events", response_model=AuditEventList)
async def get_audit_events(
    project_key: str,
    request: Request,
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    actor: Optional[str] = Query(None, description="Filter by actor"),
    since: Optional[str] = Query(
        None, description="Filter events since timestamp (ISO 8601)"
    ),
    until: Optional[str] = Query(
        None, description="Filter events until timestamp (ISO 8601)"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
):
    """
    Retrieve audit events for a project.

    Supports filtering by event type, actor, and time range.
    Results are paginated using limit and offset.
    """
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        result = audit_service.get_audit_events(
            project_key=project_key,
            git_manager=git_manager,
            event_type=event_type,
            actor=actor,
            since=since,
            until=until,
            limit=limit,
            offset=offset,
        )

        return AuditEventList(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve audit events: {str(e)}"
        )
