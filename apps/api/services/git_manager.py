"""
Git repository manager for project documents.
"""

import json
import git
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


class GitManager:
    """Manages git operations for project documents."""

    def __init__(self, base_path: str = "/projectDocs"):
        """Initialize git manager with base path."""
        self.base_path = Path(base_path)
        self.repo: Optional[git.Repo] = None

    def ensure_repository(self):
        """Ensure the base path is a git repository, initialize if needed."""
        self.base_path.mkdir(parents=True, exist_ok=True)

        git_dir = self.base_path / ".git"
        logger = logging.getLogger(__name__)

        # Helper to attempt marking the mounted repo as safe for git
        def add_safe_directory():
            try:
                subprocess.run(
                    [
                        "git",
                        "config",
                        "--global",
                        "--add",
                        "safe.directory",
                        str(self.base_path),
                    ],
                    check=False,
                )
                logger.info("Added %s to git safe.directory", self.base_path)
            except Exception:
                logger.exception("Failed to add safe.directory for %s", self.base_path)

        if not git_dir.exists():
            try:
                self.repo = git.Repo.init(self.base_path)
                # Create initial commit
                readme_path = self.base_path / "README.md"
                readme_path.write_text(
                    "# Project Documents\n\nThis repository contains project management documents.\n"
                )
                try:
                    self.repo.index.add(["README.md"])
                    self.repo.index.commit("Initial commit")
                except Exception:
                    logger.exception(
                        "Initial commit failed in new repo at %s", self.base_path
                    )
            except Exception:
                logger.exception("Failed to initialize git repo at %s", self.base_path)
                # Attempt to mark directory safe and retry
                add_safe_directory()
                try:
                    self.repo = git.Repo(self.base_path)
                except Exception:
                    # If still failing, re-create repository
                    try:
                        backup = (
                            self.base_path
                            / f".git.broken.{int(datetime.now(timezone.utc).timestamp())}"
                        )
                        if git_dir.exists():
                            git_dir.rename(backup)
                        self.repo = git.Repo.init(self.base_path)
                        readme_path = self.base_path / "README.md"
                        readme_path.write_text(
                            "# Project Documents\n\nThis repository contains project management documents.\n"
                        )
                        self.repo.index.add(["README.md"])
                        self.repo.index.commit("Initial commit")
                        logger.warning(
                            "Reinitialized repository at %s, moved old .git to %s",
                            self.base_path,
                            backup,
                        )
                    except Exception:
                        logger.exception(
                            "Failed to reinitialize repository at %s", self.base_path
                        )
        else:
            # Try opening existing repo; handle corrupted or unsafe repos gracefully
            try:
                try:
                    self.repo = git.Repo(self.base_path)
                except Exception:
                    # Try marking safe.directory and retry
                    add_safe_directory()
                    self.repo = git.Repo(self.base_path)
            except Exception:
                logger.exception(
                    "Existing repository at %s appears invalid, attempting reinit",
                    self.base_path,
                )
                try:
                    backup = (
                        self.base_path
                        / f".git.broken.{int(datetime.now(timezone.utc).timestamp())}"
                    )
                    git_dir.rename(backup)
                except Exception:
                    logger.exception("Failed to move broken .git at %s", self.base_path)
                try:
                    self.repo = git.Repo.init(self.base_path)
                    readme_path = self.base_path / "README.md"
                    if not readme_path.exists():
                        readme_path.write_text(
                            "# Project Documents\n\nThis repository contains project management documents.\n"
                        )
                    try:
                        self.repo.index.add(["README.md"])
                        self.repo.index.commit("Initial commit")
                    except Exception:
                        logger.exception(
                            "Initial commit failed after reinit at %s", self.base_path
                        )
                    logger.warning("Reinitialized repository at %s", self.base_path)
                except Exception:
                    logger.exception(
                        "Failed to reinitialize repository at %s", self.base_path
                    )

    def get_project_path(self, project_key: str) -> Path:
        """Get the path for a specific project."""
        return self.base_path / project_key

    def create_project(
        self, project_key: str, project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new project folder with project.json."""
        project_path = self.get_project_path(project_key)
        project_path.mkdir(parents=True, exist_ok=True)

        # Create events directory
        events_path = project_path / "events"
        events_path.mkdir(exist_ok=True)

        # Create artifacts directory
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(exist_ok=True)

        # Write project.json
        project_json_path = project_path / "project.json"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        project_info = {
            **project_data,
            "methodology": "ISO21500",
            "created_at": now,
            "updated_at": now,
        }
        project_json_path.write_text(json.dumps(project_info, indent=2))

        # Commit
        self.repo.index.add([str(project_json_path.relative_to(self.base_path))])
        self.repo.index.commit(f"Create project {project_key}")

        return project_info

    def read_project_json(self, project_key: str) -> Optional[Dict[str, Any]]:
        """Read project.json for a project."""
        project_json_path = self.get_project_path(project_key) / "project.json"
        if not project_json_path.exists():
            return None
        return json.loads(project_json_path.read_text())

    def write_file(self, project_key: str, relative_path: str, content: str):
        """Write a file within a project."""
        project_path = self.get_project_path(project_key)
        file_path = project_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    def read_file(self, project_key: str, relative_path: str) -> Optional[str]:
        """Read a file within a project."""
        file_path = self.get_project_path(project_key) / relative_path
        if not file_path.exists():
            return None
        return file_path.read_text()

    def commit_changes(self, project_key: str, message: str, files: List[str]) -> str:
        """Stage and commit changes for a project."""
        project_path = self.get_project_path(project_key)

        # Convert to relative paths from repo root
        relative_files = []
        for file_path in files:
            full_path = project_path / file_path
            if full_path.exists():
                relative_files.append(str(full_path.relative_to(self.base_path)))

        if relative_files:
            self.repo.index.add(relative_files)
            commit = self.repo.index.commit(message)
            return commit.hexsha
        return ""

    def get_diff(self, project_key: str, file_path: str, content: str) -> str:
        """Generate unified diff for proposed changes."""
        project_path = self.get_project_path(project_key)
        full_path = project_path / file_path

        if not full_path.exists():
            # New file
            lines = content.split("\n")
            diff_lines = [
                "--- /dev/null",
                f"+++ b/{project_key}/{file_path}",
                "@@ -0,0 +1," + str(len(lines)) + " @@",
            ]
            diff_lines.extend([f"+{line}" for line in lines])
            return "\n".join(diff_lines)
        else:
            # Modified file
            old_content = full_path.read_text()
            old_lines = old_content.split("\n")
            new_lines = content.split("\n")

            # Simple diff generation (in production, use difflib)
            diff_lines = [
                f"--- a/{project_key}/{file_path}",
                f"+++ b/{project_key}/{file_path}",
                f"@@ -1,{len(old_lines)} +1,{len(new_lines)} @@",
            ]

            # Show a simplified diff
            max_lines = min(len(old_lines), len(new_lines))
            for i in range(max_lines):
                if old_lines[i] != new_lines[i]:
                    diff_lines.append(f"-{old_lines[i]}")
                    diff_lines.append(f"+{new_lines[i]}")

            # Add remaining lines
            if len(old_lines) > max_lines:
                for i in range(max_lines, len(old_lines)):
                    diff_lines.append(f"-{old_lines[i]}")
            if len(new_lines) > max_lines:
                for i in range(max_lines, len(new_lines)):
                    diff_lines.append(f"+{new_lines[i]}")

            return "\n".join(diff_lines)

    def list_artifacts(self, project_key: str) -> List[Dict[str, Any]]:
        """List artifacts in project with basic version info."""
        artifacts_path = self.get_project_path(project_key) / "artifacts"
        if not artifacts_path.exists():
            return []

        artifacts = []
        for file_path in artifacts_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(
                    self.get_project_path(project_key)
                )
                artifacts.append(
                    {
                        "path": str(relative_path),
                        "name": file_path.name,
                        "type": file_path.suffix[1:] if file_path.suffix else "unknown",
                    }
                )
        return artifacts

    def get_last_commit(self, project_key: str) -> Optional[Dict[str, Any]]:
        """Get last commit info for a project."""
        try:
            # Get commits that touch this project
            commits = list(
                self.repo.iter_commits(paths=str(self.get_project_path(project_key)))
            )
            if commits:
                commit = commits[0]
                return {
                    "hash": commit.hexsha,
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                }
        except Exception:
            pass
        return None

    def log_event(self, project_key: str, event_data: Dict[str, Any]):
        """Append event to NDJSON audit log."""
        events_path = self.get_project_path(project_key) / "events" / "events.ndjson"
        events_path.parent.mkdir(parents=True, exist_ok=True)

        event_line = json.dumps(
            {
                **event_data,
                "timestamp": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            }
        )

        with events_path.open("a") as f:
            f.write(event_line + "\n")
