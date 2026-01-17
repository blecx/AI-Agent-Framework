"""
Proposals router - compatibility layer for client proposal API.
Wraps the existing propose/apply command flow.
"""

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone

from models import (
    Proposal,
    ProposalCreate,
    ProposalList,
    ProposalStatus,
)
from services.command_service import CommandService

router = APIRouter()
command_service = CommandService()


@router.post("", response_model=Proposal, status_code=201)
async def create_proposal(
    project_key: str, proposal_request: ProposalCreate, request: Request
):
    """Create a new proposal (wraps propose_command)."""
    git_manager = request.app.state.git_manager
    llm_service = request.app.state.llm_service

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        # Call existing propose_command
        proposal_data = await command_service.propose_command(
            project_key,
            proposal_request.command,
            proposal_request.params or {},
            llm_service,
            git_manager,
        )

        # Convert to Proposal model for client compatibility
        now = datetime.now(timezone.utc).isoformat()
        proposal = Proposal(
            id=proposal_data["proposal_id"],
            project_key=project_key,
            command=proposal_data["command"],
            params=proposal_data["params"],
            status=ProposalStatus.PENDING,
            assistant_message=proposal_data["assistant_message"],
            file_changes=proposal_data["file_changes"],
            draft_commit_message=proposal_data["draft_commit_message"],
            created_at=now,
            updated_at=now,
        )

        # Persist proposal to NDJSON
        command_service.persist_proposal(
            project_key, proposal.model_dump(), git_manager
        )

        return proposal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create proposal: {str(e)}"
        )


@router.get("", response_model=ProposalList)
async def list_proposals(project_key: str, request: Request):
    """List all proposals for a project."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        # Load proposals from storage
        proposals_data = command_service.load_proposals(project_key, git_manager)
        proposals = [Proposal(**p) for p in proposals_data]

        return ProposalList(proposals=proposals, total=len(proposals))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to load proposals: {str(e)}"
        )


@router.get("/{proposal_id}", response_model=Proposal)
async def get_proposal(project_key: str, proposal_id: str, request: Request):
    """Get a specific proposal by ID."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        # Load proposal from storage
        proposal_data = command_service.load_proposal(
            project_key, proposal_id, git_manager
        )
        if not proposal_data:
            raise HTTPException(
                status_code=404, detail=f"Proposal {proposal_id} not found"
            )

        return Proposal(**proposal_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to load proposal: {str(e)}"
        )


@router.post("/{proposal_id}/apply", response_model=Proposal)
async def apply_proposal(project_key: str, proposal_id: str, request: Request):
    """Apply a proposal (wraps apply_command)."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        # Load proposal to check it exists and is pending
        proposal_data = command_service.load_proposal(
            project_key, proposal_id, git_manager
        )
        if not proposal_data:
            raise HTTPException(
                status_code=404, detail=f"Proposal {proposal_id} not found"
            )

        proposal = Proposal(**proposal_data)
        if proposal.status != ProposalStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Proposal {proposal_id} is already {proposal.status}",
            )

        # Apply the proposal
        result = await command_service.apply_proposal(
            proposal_id, git_manager, log_content=False
        )

        # Update proposal status
        proposal.status = ProposalStatus.APPLIED
        proposal.applied_at = datetime.now(timezone.utc).isoformat()
        proposal.updated_at = proposal.applied_at
        proposal.commit_hash = result["commit_hash"]

        # Persist updated proposal
        command_service.update_proposal(
            project_key, proposal_id, proposal.model_dump(), git_manager
        )

        return proposal
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to apply proposal: {str(e)}"
        )


@router.post("/{proposal_id}/reject", response_model=Proposal)
async def reject_proposal(project_key: str, proposal_id: str, request: Request):
    """Reject a proposal."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        # Load proposal to check it exists and is pending
        proposal_data = command_service.load_proposal(
            project_key, proposal_id, git_manager
        )
        if not proposal_data:
            raise HTTPException(
                status_code=404, detail=f"Proposal {proposal_id} not found"
            )

        proposal = Proposal(**proposal_data)
        if proposal.status != ProposalStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Proposal {proposal_id} is already {proposal.status}",
            )

        # Update proposal status
        proposal.status = ProposalStatus.REJECTED
        proposal.rejected_at = datetime.now(timezone.utc).isoformat()
        proposal.updated_at = proposal.rejected_at

        # Persist updated proposal
        command_service.update_proposal(
            project_key, proposal_id, proposal.model_dump(), git_manager
        )

        return proposal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reject proposal: {str(e)}"
        )
