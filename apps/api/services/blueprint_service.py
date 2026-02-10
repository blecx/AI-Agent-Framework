"""
Blueprint service for managing project blueprints.

Implements CRUD operations following DDD architecture:
- Business logic and validation in service layer
- Persistence delegated to GitManager (repository pattern)
- Storage format: JSON files in .blueprints/{blueprint_id}.json
"""

import json
from pathlib import Path
from typing import List, Optional

from domain.blueprints.models import (
    Blueprint,
    BlueprintCreate,
    BlueprintUpdate,
)
from services.git_manager import GitManager
from services.template_service import TemplateService


class BlueprintService:
    """Service for handling blueprint operations."""

    def __init__(self, git_manager: GitManager, project_key: str = "system"):
        """
        Initialize blueprint service.

        Args:
            git_manager: GitManager instance for persistence
            project_key: Project key for storage (default: 'system' for global blueprints)
        """
        self.git_manager = git_manager
        self.project_key = project_key
        self.blueprint_dir = ".blueprints"
        self.template_service = TemplateService(git_manager, project_key)

    def create_blueprint(self, blueprint_create: BlueprintCreate) -> Blueprint:
        """
        Create a new blueprint.

        Args:
            blueprint_create: Blueprint creation data

        Returns:
            Created blueprint

        Raises:
            ValueError: If blueprint with same ID already exists or validation fails
        """
        # Check for duplicate ID
        existing = self._get_blueprint_by_id(blueprint_create.id)
        if existing:
            raise ValueError(f"Blueprint {blueprint_create.id} already exists")

        # Validate referenced templates exist
        self._validate_template_references(
            blueprint_create.required_templates + blueprint_create.optional_templates
        )

        # Create blueprint entity
        blueprint = Blueprint(
            id=blueprint_create.id,
            name=blueprint_create.name,
            description=blueprint_create.description,
            required_templates=blueprint_create.required_templates,
            optional_templates=blueprint_create.optional_templates,
            workflow_requirements=blueprint_create.workflow_requirements,
        )

        # Persist to storage
        self._save_blueprint(blueprint)

        # Commit to git
        file_path = f"{self.blueprint_dir}/{blueprint.id}.json"
        self.git_manager.commit_changes(
            self.project_key,
            f"[BLUEPRINT] Create blueprint: {blueprint.name}",
            [file_path],
        )

        return blueprint

    def get_blueprint(self, blueprint_id: str) -> Optional[Blueprint]:
        """
        Retrieve a blueprint by ID.

        Args:
            blueprint_id: Blueprint ID to retrieve

        Returns:
            Blueprint if found, None otherwise
        """
        return self._get_blueprint_by_id(blueprint_id)

    def list_blueprints(self) -> List[Blueprint]:
        """
        List all blueprints.

        Returns:
            List of all blueprints (empty list if none exist)
        """
        docs_path = Path(self.git_manager.base_path)
        blueprint_path = docs_path / self.blueprint_dir

        if not blueprint_path.exists():
            return []

        blueprints = []
        for file_path in blueprint_path.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    blueprint = Blueprint(**data)
                    blueprints.append(blueprint)
            except (json.JSONDecodeError, ValueError):
                # Skip invalid files
                continue

        return blueprints

    def update_blueprint(
        self, blueprint_id: str, blueprint_update: BlueprintUpdate
    ) -> Blueprint:
        """
        Update an existing blueprint.

        Args:
            blueprint_id: Blueprint ID to update
            blueprint_update: Fields to update

        Returns:
            Updated blueprint

        Raises:
            ValueError: If blueprint not found or validation fails
        """
        # Get existing blueprint
        existing = self._get_blueprint_by_id(blueprint_id)
        if not existing:
            from domain.errors import not_found

            raise ValueError(not_found("Blueprint", blueprint_id))

        # Apply updates
        update_data = blueprint_update.model_dump(exclude_none=True)

        # Validate template references if templates are being updated
        all_templates = []
        if "required_templates" in update_data:
            all_templates.extend(update_data["required_templates"])
        else:
            all_templates.extend(existing.required_templates)

        if "optional_templates" in update_data:
            all_templates.extend(update_data["optional_templates"])
        else:
            all_templates.extend(existing.optional_templates)

        if all_templates:
            self._validate_template_references(all_templates)

        # Create updated blueprint
        blueprint_data = existing.model_dump()
        blueprint_data.update(update_data)
        blueprint = Blueprint(**blueprint_data)

        # Persist to storage
        self._save_blueprint(blueprint)

        # Commit to git
        file_path = f"{self.blueprint_dir}/{blueprint.id}.json"
        self.git_manager.commit_changes(
            self.project_key,
            f"[BLUEPRINT] Update blueprint: {blueprint.name}",
            [file_path],
        )

        return blueprint

    def delete_blueprint(self, blueprint_id: str) -> None:
        """
        Delete a blueprint.

        Args:
            blueprint_id: Blueprint ID to delete

        Raises:
            ValueError: If blueprint not found
        """
        # Check blueprint exists
        existing = self._get_blueprint_by_id(blueprint_id)
        if not existing:
            from domain.errors import not_found

            raise ValueError(not_found("Blueprint", blueprint_id))

        # Delete file
        docs_path = Path(self.git_manager.base_path)
        file_path = docs_path / self.blueprint_dir / f"{blueprint_id}.json"
        file_path.unlink()

        # Commit to git
        relative_path = f"{self.blueprint_dir}/{blueprint_id}.json"
        self.git_manager.commit_changes(
            self.project_key,
            f"[BLUEPRINT] Delete blueprint: {existing.name}",
            [relative_path],
        )

    def _get_blueprint_by_id(self, blueprint_id: str) -> Optional[Blueprint]:
        """Internal helper to retrieve blueprint by ID."""
        docs_path = Path(self.git_manager.base_path)
        file_path = docs_path / self.blueprint_dir / f"{blueprint_id}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return Blueprint(**data)
        except (json.JSONDecodeError, ValueError):
            return None

    def _save_blueprint(self, blueprint: Blueprint) -> None:
        """Internal helper to save blueprint to disk."""
        docs_path = Path(self.git_manager.base_path)
        blueprint_path = docs_path / self.blueprint_dir
        blueprint_path.mkdir(parents=True, exist_ok=True)

        file_path = blueprint_path / f"{blueprint.id}.json"
        with open(file_path, "w") as f:
            json.dump(blueprint.model_dump(), f, indent=2)

    def _validate_template_references(self, template_ids: List[str]) -> None:
        """
        Validate that all referenced templates exist.

        Args:
            template_ids: List of template IDs to validate

        Raises:
            ValueError: If any template doesn't exist
        """
        for template_id in template_ids:
            template = self.template_service.get_template(template_id)
            if not template:
                from domain.errors import reference_not_found

                raise ValueError(reference_not_found("template", template_id))
