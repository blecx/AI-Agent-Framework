"""
Commands router - global command execution and history.
Provides endpoints for executing commands globally and retrieving command history.
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional
from datetime import datetime, timezone
import uuid

from models import (
    CommandHistory,
    CommandExecute,
    CommandHistoryList,
    CommandStatus,
)
from services.command_service import CommandService

router = APIRouter()
command_service = CommandService()


@router.post("", response_model=CommandHistory, status_code=201)
async def execute_command(command_request: CommandExecute, request: Request):
    """Execute a command and return command history entry."""
    git_manager = request.app.state.git_manager
    llm_service = request.app.state.llm_service

    # Verify project exists
    project_info = git_manager.read_project_json(command_request.project_key)
    if not project_info:
        raise HTTPException(
            status_code=404, detail=f"Project {command_request.project_key} not found"
        )

    command_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    try:
        # Create command history entry
        command_data = {
            "id": command_id,
            "project_key": command_request.project_key,
            "command": command_request.command,
            "params": command_request.params or {},
            "status": CommandStatus.RUNNING,
            "created_at": now,
            "started_at": now,
        }

        # Log the command
        command_service.log_command(command_data, git_manager)

        # Execute the command (propose + apply flow)
        try:
            # Propose command
            proposal_data = await command_service.propose_command(
                command_request.project_key,
                command_request.command,
                command_request.params or {},
                llm_service,
                git_manager,
            )

            proposal_id = proposal_data["proposal_id"]

            # Apply command automatically (for global command execution)
            result = await command_service.apply_proposal(
                proposal_id, git_manager, log_content=False
            )

            # Update command status to completed
            command_data["status"] = CommandStatus.COMPLETED
            command_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            command_data["proposal_id"] = proposal_id
            command_data["commit_hash"] = result["commit_hash"]

        except Exception as e:
            # Update command status to failed
            command_data["status"] = CommandStatus.FAILED
            command_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            command_data["error_message"] = str(e)

        # Update the command log
        command_service.update_command(command_id, command_data, git_manager)

        return CommandHistory(**command_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to execute command: {str(e)}"
        )


@router.get("/{command_id}", response_model=CommandHistory)
async def get_command(command_id: str, request: Request):
    """Get a specific command by ID."""
    git_manager = request.app.state.git_manager

    try:
        command_data = command_service.load_command(command_id, git_manager)
        if not command_data:
            raise HTTPException(
                status_code=404, detail=f"Command {command_id} not found"
            )

        return CommandHistory(**command_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load command: {str(e)}")


@router.get("", response_model=CommandHistoryList)
async def list_commands(
    request: Request, projectKey: Optional[str] = Query(None, alias="projectKey")
):
    """List all commands, optionally filtered by project key."""
    git_manager = request.app.state.git_manager

    try:
        # Load commands with optional project key filter
        commands_data = command_service.load_all_commands(
            git_manager, project_key_filter=projectKey
        )

        commands = [CommandHistory(**c) for c in commands_data]

        return CommandHistoryList(commands=commands, total=len(commands))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to load commands: {str(e)}"
        )
