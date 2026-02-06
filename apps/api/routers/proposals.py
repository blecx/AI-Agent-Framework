"""
Proposals router - REST API for proposal lifecycle management.
Delegates to ProposalService for all business logic.
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional

from apps.api.domain.proposals.models import (
    Proposal,
    ProposalCreate,
    ProposalStatus,
    ChangeType,
)
from apps.api.services.proposal_service import ProposalService

router = APIRouter()


@router.post("", response_model=Proposal, status_code=201)
async def create_proposal(
    project_key: str,
    proposal_create: ProposalCreate,
    request: Request,
):
    """
    Create a new proposal for artifact changes.

    Returns: Created proposal with metadata
    """
    git_manager = request.app.state.git_manager
    audit_service = request.app.state.audit_service

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    # Build full Proposal from ProposalCreate + project_key
    proposal = Proposal(project_key=project_key, **proposal_create.model_dump())

    try:
        service = ProposalService(git_manager, audit_service)
        created_proposal = service.create_proposal(proposal)
        return created_proposal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create proposal: {str(e)}"
        )


@router.get("", response_model=list[Proposal])
async def list_proposals(
    project_key: str,
    request: Request,
    status_filter: Optional[ProposalStatus] = Query(
        None, description="Filter by status", alias="status_filter"
    ),
    change_type: Optional[ChangeType] = Query(
        None, description="Filter by change type"
    ),
):
    """
    List all proposals for a project with optional filters.

    Returns: List of proposals matching filters
    """
    git_manager = request.app.state.git_manager
    audit_service = request.app.state.audit_service

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    try:
        service = ProposalService(git_manager, audit_service)
        proposals = service.list_proposals(
            project_key, status=status_filter, change_type=change_type
        )
        return proposals
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list proposals: {str(e)}"
        )


@router.get("/{proposal_id}", response_model=Proposal)
async def get_proposal(
    project_key: str,
    proposal_id: str,
    request: Request,
):
    """
    Get a specific proposal by ID.

    Returns: Proposal details
    """
    git_manager = request.app.state.git_manager
    audit_service = request.app.state.audit_service

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    try:
        service = ProposalService(git_manager, audit_service)
        proposal = service.get_proposal(project_key, proposal_id)

        if not proposal:
            raise HTTPException(
                status_code=404, detail=f"Proposal '{proposal_id}' not found"
            )

        return proposal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get proposal: {str(e)}")


@router.post("/{proposal_id}/apply", response_model=dict)
async def apply_proposal(
    project_key: str,
    proposal_id: str,
    request: Request,
):
    """
    Apply a proposal to its target artifact.

    Returns: Application result with details
    """
    git_manager = request.app.state.git_manager
    audit_service = request.app.state.audit_service

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    try:
        service = ProposalService(git_manager, audit_service)
        result = service.apply_proposal(project_key, proposal_id)
        return result
    except ValueError as e:
        # Handle already-applied, not found, etc.
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "already" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to apply proposal: {str(e)}"
        )


@router.post("/{proposal_id}/reject", response_model=dict)
async def reject_proposal(
    project_key: str,
    proposal_id: str,
    request: Request,
    reject_data: dict,
):
    """
    Reject a proposal with a reason.

    Returns: Rejection result
    """
    git_manager = request.app.state.git_manager
    audit_service = request.app.state.audit_service

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    # Extract reason from body
    reason = reject_data.get("reason", "No reason provided")

    try:
        service = ProposalService(git_manager, audit_service)
        result = service.reject_proposal(project_key, proposal_id, reason)
        # Add reason to result for response
        result["reason"] = reason
        return result
    except ValueError as e:
        # Handle already-rejected, not found, etc.
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "already" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reject proposal: {str(e)}"
        )
