"""
Template service for managing artifact templates.

Implements CRUD operations following DDD architecture:
- Business logic and validation in service layer
- Persistence delegated to GitManager (repository pattern)
- Storage format: JSON files in .templates/{template_id}.json
"""

import json
import uuid
from typing import List, Optional

from apps.api.domain.templates.models import (
    Template,
    TemplateCreate,
    TemplateUpdate,
)
from services.git_manager import GitManager


class TemplateService:
    """Service for handling artifact template operations."""

    def __init__(self, git_manager: GitManager, project_key: str = "system"):
        """
        Initialize template service.

        Args:
            git_manager: GitManager instance for persistence
            project_key: Project key for storage (default: 'system' for global templates)
        """
        self.git_manager = git_manager
        self.project_key = project_key
        self.template_dir = ".templates"

    def create_template(self, template_create: TemplateCreate) -> Template:
        """
        Create a new template.

        Args:
            template_create: Template creation data

        Returns:
            Created template with generated ID

        Raises:
            ValueError: If template with same ID already exists or validation fails
        """
        # Generate unique ID
        template_id = f"tpl-{str(uuid.uuid4())[:8]}"

        # Check for duplicate (defensive, should not happen with UUID)
        existing = self._get_template_by_id(template_id)
        if existing:
            raise ValueError(f"Template {template_id} already exists")

        # Create template entity
        template = Template(
            id=template_id,
            name=template_create.name,
            description=template_create.description,
            schema=template_create.schema,
            markdown_template=template_create.markdown_template,
            artifact_type=template_create.artifact_type,
            version=template_create.version,
        )

        # Persist to storage
        self._save_template(template)

        # Commit to git
        file_path = f"{self.template_dir}/{template_id}.json"
        self.git_manager.commit_changes(
            self.project_key,
            f"[TEMPLATE] Create template: {template.name}",
            [file_path],
        )

        return template

    def get_template(self, template_id: str) -> Optional[Template]:
        """
        Retrieve a template by ID.

        Args:
            template_id: Template identifier

        Returns:
            Template if found, None otherwise
        """
        return self._get_template_by_id(template_id)

    def list_templates(self, artifact_type: Optional[str] = None) -> List[Template]:
        """
        List all templates, optionally filtered by artifact type.

        Args:
            artifact_type: Optional filter by artifact type

        Returns:
            List of templates
        """
        templates = []
        template_dir_path = (
            self.git_manager.get_project_path(self.project_key) / self.template_dir
        )

        if not template_dir_path.exists():
            return []

        for template_file in template_dir_path.glob("*.json"):
            content = template_file.read_text()
            template_data = json.loads(content)
            template = Template(**template_data)

            # Apply filter if specified
            if artifact_type is None or template.artifact_type == artifact_type:
                templates.append(template)

        return templates

    def update_template(
        self, template_id: str, template_update: TemplateUpdate
    ) -> Optional[Template]:
        """
        Update an existing template.

        Args:
            template_id: Template identifier
            template_update: Fields to update

        Returns:
            Updated template if found, None otherwise
        """
        existing = self._get_template_by_id(template_id)
        if not existing:
            return None

        # Update fields (only non-None values)
        update_data = template_update.model_dump(exclude_unset=True)
        updated_template = existing.model_copy(update=update_data)

        # Persist changes
        self._save_template(updated_template)

        # Commit to git
        file_path = f"{self.template_dir}/{template_id}.json"
        self.git_manager.commit_changes(
            self.project_key,
            f"[TEMPLATE] Update template: {updated_template.name}",
            [file_path],
        )

        return updated_template

    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.

        Args:
            template_id: Template identifier

        Returns:
            True if deleted, False if not found
        """
        # Check if template exists
        existing = self._get_template_by_id(template_id)
        if not existing:
            return False

        # Get path for git commit
        file_path = f"{self.template_dir}/{template_id}.json"
        template_path = self.git_manager.get_project_path(self.project_key) / file_path

        # Delete file from disk
        template_path.unlink()

        # Stage deletion and commit using GitManager's approach
        # Since file is already deleted, we need to use git index directly
        if self.git_manager.repo:
            relative_path = str(template_path.relative_to(self.git_manager.base_path))
            self.git_manager.repo.index.remove([relative_path])
            self.git_manager.repo.index.commit(
                f"[TEMPLATE] Delete template: {existing.name}"
            )

        return True

    # Private helper methods

    def _get_template_by_id(self, template_id: str) -> Optional[Template]:
        """Load template from storage by ID."""
        content = self.git_manager.read_file(
            self.project_key, f"{self.template_dir}/{template_id}.json"
        )
        if content is None:
            return None

        template_data = json.loads(content)
        return Template(**template_data)

    def _save_template(self, template: Template):
        """Save template to storage."""
        content = json.dumps(template.model_dump(), indent=2)
        self.git_manager.write_file(
            self.project_key, f"{self.template_dir}/{template.id}.json", content
        )
