"""
Commands router for propose/apply flow.
"""

from fastapi import APIRouter, HTTPException, Request

from models import CommandPropose, CommandProposal, CommandApply, CommandApplyResult
from services.command_service import CommandService

router = APIRouter()

# Single instance of command service (in production, use dependency injection)
command_service = CommandService()


@router.post("/propose", response_model=CommandProposal)
async def propose_command(
    project_key: str, command_request: CommandPropose, request: Request
):
    """Propose a command with changes preview."""
    git_manager = request.app.state.git_manager
    llm_service = request.app.state.llm_service

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(status_code=404, detail=f"Project {project_key} not found")

    try:
        proposal = await command_service.propose_command(
            project_key,
            command_request.command,
            command_request.params or {},
            llm_service,
            git_manager,
        )

        return CommandProposal(**proposal)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to propose command: {str(e)}"
        )


@router.post("/apply", response_model=CommandApplyResult)
async def apply_command(
    project_key: str, apply_request: CommandApply, request: Request
):
    """Apply a previously proposed command."""
    git_manager = request.app.state.git_manager

    # Verify project exists
    project_info = git_manager.read_project_json(project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project '{project_key}' not found"
        )

    try:
        result = await command_service.apply_proposal(
            apply_request.proposal_id,
            git_manager,
            log_content=False,  # Compliance: only log hashes by default
        )

        return CommandApplyResult(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to apply command: {str(e)}"
        )
