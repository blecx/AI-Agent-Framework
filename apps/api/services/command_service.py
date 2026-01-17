"""
Command service for handling project commands with propose/apply flow.
"""

import uuid
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from git_manager import GitManager


class CommandService:
    """Service for handling project commands."""

    def __init__(self):
        """Initialize command service."""
        # Store proposals in memory (in production, use Redis or similar)
        self.proposals: Dict[str, Dict[str, Any]] = {}

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

        # Route to appropriate command handler
        if command == "assess_gaps":
            result = await self._propose_assess_gaps(
                project_key, params, llm_service, git_manager
            )
        elif command == "generate_artifact":
            result = await self._propose_generate_artifact(
                project_key, params, llm_service, git_manager
            )
        elif command == "generate_plan":
            result = await self._propose_generate_plan(
                project_key, params, llm_service, git_manager
            )
        else:
            raise ValueError(f"Unknown command: {command}")

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

    async def _propose_assess_gaps(
        self, project_key: str, params: Dict[str, Any], llm_service, git_manager
    ) -> Dict[str, Any]:
        """Propose gap assessment."""
        # Check what artifacts exist
        artifacts = git_manager.list_artifacts(project_key)

        # Define required ISO21500 artifacts
        required_artifacts = [
            "project_charter.md",
            "stakeholder_register.md",
            "scope_statement.md",
            "wbs.md",
            "schedule.md",
            "budget.md",
            "quality_plan.md",
            "risk_register.md",
            "communication_plan.md",
            "procurement_plan.md",
        ]

        existing_names = [a["name"] for a in artifacts]
        missing = [name for name in required_artifacts if name not in existing_names]
        present = [name for name in required_artifacts if name in existing_names]

        # Render prompt
        prompt = llm_service.render_prompt(
            "assess_gaps.j2",
            {
                "project_key": project_key,
                "missing_artifacts": missing,
                "present_artifacts": present,
            },
        )

        # Get LLM response
        messages = [
            {
                "role": "system",
                "content": "You are an ISO 21500 project management expert.",
            },
            {"role": "user", "content": prompt},
        ]
        llm_response = await llm_service.chat_completion(messages)

        # Generate gap report
        gap_report = llm_service.render_output(
            "gap_report.md",
            {
                "project_key": project_key,
                "missing_artifacts": missing,
                "present_artifacts": present,
                "llm_analysis": llm_response,
                "timestamp": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            },
        )

        # Prepare file change
        file_changes = [
            {
                "path": "reports/gap_assessment.md",
                "operation": "create",
                "diff": git_manager.get_diff(
                    project_key, "reports/gap_assessment.md", gap_report
                ),
                "content": gap_report,
            }
        ]

        return {
            "assistant_message": f"Gap assessment completed. Found {len(missing)} missing artifacts out of {len(required_artifacts)} required.",
            "file_changes": file_changes,
            "draft_commit_message": f"[{project_key}] Add gap assessment report",
        }

    async def _propose_generate_artifact(
        self, project_key: str, params: Dict[str, Any], llm_service, git_manager
    ) -> Dict[str, Any]:
        """Propose artifact generation."""
        artifact_name = params.get("artifact_name", "project_charter.md")
        artifact_type = params.get("artifact_type", "project_charter")

        # Get project info
        project_info = git_manager.read_project_json(project_key)

        # Render prompt
        prompt = llm_service.render_prompt(
            "generate_artifact.j2",
            {
                "project_key": project_key,
                "project_name": project_info.get("name", "Unknown"),
                "artifact_name": artifact_name,
                "artifact_type": artifact_type,
            },
        )

        # Get LLM response
        messages = [
            {
                "role": "system",
                "content": "You are an ISO 21500 project management expert. Generate comprehensive project management artifacts.",
            },
            {"role": "user", "content": prompt},
        ]
        llm_response = await llm_service.chat_completion(messages, max_tokens=2048)

        # Use output template as base and incorporate LLM content
        try:
            template_name = f"{artifact_type}.md"
            artifact_content = llm_service.render_output(
                template_name,
                {
                    "project_key": project_key,
                    "project_name": project_info.get("name", "Unknown"),
                    "generated_content": llm_response,
                    "timestamp": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                },
            )
        except Exception:
            # Fallback if template doesn't exist
            artifact_content = f"""# {artifact_name}

Project: {project_info.get("name", "Unknown")}
Key: {project_key}
Generated: {datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}

{llm_response}
"""

        file_path = f"artifacts/{artifact_name}"
        file_changes = [
            {
                "path": file_path,
                "operation": "create",
                "diff": git_manager.get_diff(project_key, file_path, artifact_content),
                "content": artifact_content,
            }
        ]

        return {
            "assistant_message": f"Generated artifact: {artifact_name}",
            "file_changes": file_changes,
            "draft_commit_message": f"[{project_key}] Generate {artifact_name}",
        }

    async def _propose_generate_plan(
        self, project_key: str, params: Dict[str, Any], llm_service, git_manager
    ) -> Dict[str, Any]:
        """Propose project plan generation."""
        # Get project info
        project_info = git_manager.read_project_json(project_key)

        # Render prompt
        prompt = llm_service.render_prompt(
            "generate_plan.j2",
            {
                "project_key": project_key,
                "project_name": project_info.get("name", "Unknown"),
            },
        )

        # Get LLM response
        messages = [
            {
                "role": "system",
                "content": "You are an ISO 21500 project management expert. Create detailed project schedules.",
            },
            {"role": "user", "content": prompt},
        ]
        llm_response = await llm_service.chat_completion(messages, max_tokens=2048)

        # Generate plan with Mermaid gantt
        plan_content = llm_service.render_output(
            "project_plan.md",
            {
                "project_key": project_key,
                "project_name": project_info.get("name", "Unknown"),
                "llm_schedule": llm_response,
                "timestamp": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            },
        )

        file_path = "artifacts/schedule.md"
        file_changes = [
            {
                "path": file_path,
                "operation": "create",
                "diff": git_manager.get_diff(project_key, file_path, plan_content),
                "content": plan_content,
            }
        ]

        return {
            "assistant_message": "Project schedule generated with timeline and milestones.",
            "file_changes": file_changes,
            "draft_commit_message": f"[{project_key}] Generate project schedule",
        }
