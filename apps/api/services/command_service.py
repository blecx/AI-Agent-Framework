"""
Command service for handling project commands with propose/apply flow.
"""

import uuid
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from .commands import (
    AssessGapsHandler,
    GenerateArtifactHandler,
    GeneratePlanHandler,
)

if TYPE_CHECKING:
    from git_manager import GitManager


class CommandService:
    """Service for handling project commands."""

    def __init__(self):
        """Initialize command service."""
        # Store proposals in memory (in production, use Redis or similar)
        self.proposals: Dict[str, Dict[str, Any]] = {}

        # Initialize command handlers (Strategy pattern)
        self.handlers = {
            "assess_gaps": AssessGapsHandler(),
            "generate_artifact": GenerateArtifactHandler(),
            "generate_plan": GeneratePlanHandler(),
        }

    async def propose_command(
        self,
        project_key: str,
        command: str,
        params: Dict[str, Any],
        llm_service,
        git_manager,
    ) -> Dict[str, Any]:
        """Generate a proposal for a command."""
        proposal_id = str(uuid.uuid4())

        # Get project info
        project_info = git_manager.read_project_json(project_key)
        if not project_info:
            raise ValueError(f"Project {project_key} not found")

        # Delegate to appropriate command handler (Strategy pattern)
        if command not in self.handlers:
            raise ValueError(f"Unknown command: {command}")

        handler = self.handlers[command]
        result = await handler.propose(project_key, params, llm_service, git_manager)

        # Store proposal
        proposal_data = {
            "proposal_id": proposal_id,
            "project_key": project_key,
            "command": command,
            "params": params,
            **result,
        }
        self.proposals[proposal_id] = proposal_data

        return proposal_data

    async def apply_proposal(
        self, proposal_id: str, git_manager, log_content: bool = False
    ) -> Dict[str, Any]:
        """Apply a previously proposed command."""
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")

        proposal = self.proposals[proposal_id]
        project_key = proposal["project_key"]

        # Write all files
        changed_files = []
        for file_change in proposal["file_changes"]:
            path = file_change["path"]
            content = file_change.get("content", "")

            git_manager.write_file(project_key, path, content)
            changed_files.append(path)

        # Commit changes
        commit_hash = git_manager.commit_changes(
            project_key, proposal["draft_commit_message"], changed_files
        )

        # Log event
        event_data = {
            "event_type": "command_applied",
            "proposal_id": proposal_id,
            "command": proposal["command"],
            "commit_hash": commit_hash,
            "files_changed": changed_files,
        }

        # Only log content hashes for compliance
        if log_content:
            event_data["params"] = proposal["params"]
            event_data["message"] = proposal["assistant_message"]
        else:
            # Store only hashes
            event_data["params_hash"] = hashlib.sha256(
                str(proposal["params"]).encode()
            ).hexdigest()
            event_data["message_hash"] = hashlib.sha256(
                proposal["assistant_message"].encode()
            ).hexdigest()

        git_manager.log_event(project_key, event_data)

        # Clean up proposal
        del self.proposals[proposal_id]

        return {
            "commit_hash": commit_hash,
            "changed_files": changed_files,
            "message": "Changes applied successfully",
        }

    def persist_proposal(
        self, project_key: str, proposal_data: Dict[str, Any], git_manager: "GitManager"
    ) -> None:
        """Persist proposal to NDJSON file."""
        proposals_dir = Path(git_manager.base_path) / project_key / "proposals"
        proposals_dir.mkdir(parents=True, exist_ok=True)
        proposals_file = proposals_dir / "proposals.ndjson"

        # Append proposal as NDJSON line
        with open(proposals_file, "a") as f:
            f.write(json.dumps(proposal_data) + "\n")

    def load_proposals(
        self, project_key: str, git_manager: "GitManager"
    ) -> List[Dict[str, Any]]:
        """Load all proposals for a project from NDJSON file."""
        proposals_file = (
            Path(git_manager.base_path) / project_key / "proposals" / "proposals.ndjson"
        )

        if not proposals_file.exists():
            return []

        proposals = []
        with open(proposals_file, "r") as f:
            for line in f:
                if line.strip():
                    proposals.append(json.loads(line))

        return proposals

    def load_proposal(
        self, project_key: str, proposal_id: str, git_manager: "GitManager"
    ) -> Optional[Dict[str, Any]]:
        """Load a specific proposal by ID."""
        proposals = self.load_proposals(project_key, git_manager)
        for proposal in proposals:
            if proposal.get("id") == proposal_id:
                return proposal
        return None

    def update_proposal(
        self,
        project_key: str,
        proposal_id: str,
        updated_data: Dict[str, Any],
        git_manager: "GitManager",
    ) -> None:
        """Update a proposal in NDJSON file."""
        import fcntl

        proposals_file = (
            Path(git_manager.base_path) / project_key / "proposals" / "proposals.ndjson"
        )

        if not proposals_file.exists():
            return

        # Read all proposals with file locking to prevent race conditions
        with open(proposals_file, "r+") as f:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                proposals = []
                for line in f:
                    if line.strip():
                        proposals.append(json.loads(line))

                # Update the specific proposal
                for i, proposal in enumerate(proposals):
                    if proposal.get("id") == proposal_id:
                        proposals[i] = updated_data
                        break

                # Write all proposals back
                f.seek(0)
                f.truncate()
                for proposal in proposals:
                    f.write(json.dumps(proposal) + "\n")
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def log_command(
        self, command_data: Dict[str, Any], git_manager: "GitManager"
    ) -> None:
        """Log a command execution to NDJSON file."""
        project_key = command_data.get("project_key")
        commands_dir = Path(git_manager.base_path) / project_key / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        commands_file = commands_dir / "commands.ndjson"

        # Append command as NDJSON line
        with open(commands_file, "a") as f:
            f.write(json.dumps(command_data) + "\n")

    def load_commands(
        self, project_key: str, git_manager: "GitManager"
    ) -> List[Dict[str, Any]]:
        """Load all commands for a project from NDJSON file."""
        commands_file = (
            Path(git_manager.base_path) / project_key / "commands" / "commands.ndjson"
        )

        if not commands_file.exists():
            return []

        commands = []
        with open(commands_file, "r") as f:
            for line in f:
                if line.strip():
                    commands.append(json.loads(line))

        return commands

    def load_all_commands(
        self, git_manager: "GitManager", project_key_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Load all commands across all projects, optionally filtered by project key."""
        all_commands = []

        # Iterate through all project directories
        base_path = Path(git_manager.base_path)
        for project_dir in base_path.iterdir():
            if not project_dir.is_dir() or project_dir.name.startswith("."):
                continue

            # Skip if filtering by project key and this doesn't match
            if project_key_filter and project_dir.name != project_key_filter:
                continue

            commands_file = project_dir / "commands" / "commands.ndjson"
            if commands_file.exists():
                with open(commands_file, "r") as f:
                    for line in f:
                        if line.strip():
                            all_commands.append(json.loads(line))

        return all_commands

    def load_command(
        self, command_id: str, git_manager: "GitManager"
    ) -> Optional[Dict[str, Any]]:
        """Load a specific command by ID across all projects."""
        all_commands = self.load_all_commands(git_manager)
        for command in all_commands:
            if command.get("id") == command_id:
                return command
        return None

    def update_command(
        self, command_id: str, updated_data: Dict[str, Any], git_manager: "GitManager"
    ) -> None:
        """Update a command in NDJSON file."""
        import fcntl

        project_key = updated_data.get("project_key")
        commands_file = (
            Path(git_manager.base_path) / project_key / "commands" / "commands.ndjson"
        )

        if not commands_file.exists():
            return

        # Read all commands with file locking to prevent race conditions
        with open(commands_file, "r+") as f:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                commands = []
                for line in f:
                    if line.strip():
                        commands.append(json.loads(line))

                # Update the specific command
                for i, command in enumerate(commands):
                    if command.get("id") == command_id:
                        commands[i] = updated_data
                        break

                # Write all commands back
                f.seek(0)
                f.truncate()
                for command in commands:
                    f.write(json.dumps(command) + "\n")
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
