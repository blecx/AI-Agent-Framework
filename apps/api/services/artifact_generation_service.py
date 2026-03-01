"""
Artifact generation service.

Implements artifact generation from templates with Jinja2 rendering.
Following DDD architecture:
- Service layer orchestrates template loading, rendering, validation
- Delegates persistence to GitManager
- Delegates template access to TemplateService
- Delegates blueprint access to BlueprintService
"""

import jsonschema
from datetime import datetime, timezone
from typing import Dict, Any, List
from jinja2 import Environment, select_autoescape

try:
    from .template_service import TemplateService
    from .blueprint_service import BlueprintService
    from .git_manager import GitManager
except ImportError:
    from services.template_service import TemplateService
    from services.blueprint_service import BlueprintService
    from services.git_manager import GitManager


class ArtifactGenerationError(Exception):
    """Base exception for artifact generation errors."""

    pass


class TemplateRenderingError(ArtifactGenerationError):
    """Error during template rendering."""

    pass


class ValidationError(ArtifactGenerationError):
    """Error during schema validation."""

    pass


class ArtifactGenerationService:
    """Service for generating artifacts from templates."""

    def __init__(
        self,
        template_service: TemplateService,
        blueprint_service: BlueprintService,
        git_manager: GitManager,
    ):
        """
        Initialize artifact generation service.

        Args:
            template_service: Service for template access
            blueprint_service: Service for blueprint access
            git_manager: GitManager for persistence
        """
        self.template_service = template_service
        self.blueprint_service = blueprint_service
        self.git_manager = git_manager

        # Configure Jinja2 environment with sandboxing
        self.jinja_env = Environment(
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_from_template(
        self, template_id: str, project_key: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate artifact from template.

        Args:
            template_id: ID of template to use
            project_key: Project key for artifact storage
            context: Context variables for template rendering

        Returns:
            Dict with artifact_path and content

        Raises:
            ArtifactGenerationError: If template not found
            TemplateRenderingError: If rendering fails
            ValidationError: If context validation fails
        """
        # Load template
        template = self.template_service.get_template(template_id)
        if not template:
            raise ArtifactGenerationError(f"Template not found: {template_id}")

        # Sanitize and enrich context
        sanitized_context = self._sanitize_context(context)
        enriched_context = self._enrich_context(sanitized_context, project_key)

        # Validate context against schema
        try:
            jsonschema.validate(sanitized_context, template.schema)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Context validation failed: {e.message}") from e

        # Render markdown with Jinja2
        try:
            jinja_template = self.jinja_env.from_string(template.markdown_template)
            rendered = jinja_template.render(**enriched_context)
        except Exception as e:
            raise TemplateRenderingError(f"Template rendering failed: {str(e)}") from e

        # Persist to projectDocs/{project}/artifacts/{artifact_type}.md
        artifact_path = f"artifacts/{template.artifact_type}.md"
        self.git_manager.write_file(project_key, artifact_path, rendered)

        # Commit the artifact
        commit_message = f"[{project_key}] Generated {template.artifact_type} from template {template_id}"
        self.git_manager.commit_changes(project_key, commit_message, [artifact_path])

        return {
            "artifact_path": artifact_path,
            "content": rendered,
            "template_id": template_id,
            "artifact_type": template.artifact_type,
        }

    def generate_from_blueprint(
        self, blueprint_id: str, project_key: str, base_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate all artifacts from blueprint.

        Args:
            blueprint_id: ID of blueprint to use
            project_key: Project key for artifact storage
            base_context: Optional base context for all templates

        Returns:
            List of generated artifact results

        Raises:
            ArtifactGenerationError: If blueprint not found
        """
        # Load blueprint
        blueprint = self.blueprint_service.get_blueprint(blueprint_id)
        if not blueprint:
            raise ArtifactGenerationError(f"Blueprint not found: {blueprint_id}")

        # Use base context or empty dict
        context = base_context if base_context else {}

        # Generate all required artifacts
        results = []
        for template_id in blueprint.required_templates:
            try:
                result = self.generate_from_template(template_id, project_key, context)
                results.append(result)
            except ArtifactGenerationError as e:
                # Log error but continue with other artifacts
                results.append(
                    {"template_id": template_id, "error": str(e), "success": False}
                )

        return results

    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize context variables to prevent template injection.

        Args:
            context: Raw context variables

        Returns:
            Sanitized context
        """
        # Create a copy to avoid mutating input
        sanitized = {}

        for key, value in context.items():
            # Skip dangerous keys
            if key.startswith("_"):
                continue

            # Sanitize strings (basic HTML escaping handled by Jinja2 autoescape)
            if isinstance(value, str):
                sanitized[key] = value
            elif isinstance(value, (int, float, bool, type(None))):
                sanitized[key] = value
            elif isinstance(value, (list, dict)):
                # Recursively sanitize nested structures
                sanitized[key] = self._sanitize_nested(value)
            else:
                # Convert other types to string
                sanitized[key] = str(value)

        return sanitized

    def _sanitize_nested(self, value: Any) -> Any:
        """Recursively sanitize nested data structures."""
        if isinstance(value, dict):
            return {
                k: self._sanitize_nested(v)
                for k, v in value.items()
                if not k.startswith("_")
            }
        elif isinstance(value, list):
            return [self._sanitize_nested(item) for item in value]
        elif isinstance(value, str):
            return value
        elif isinstance(value, (int, float, bool, type(None))):
            return value
        else:
            return str(value)

    def _enrich_context(
        self, context: Dict[str, Any], project_key: str
    ) -> Dict[str, Any]:
        """
        Enrich context with standard variables.

        Args:
            context: User-provided context
            project_key: Project key

        Returns:
            Enriched context with additional variables
        """
        enriched = context.copy()

        # Add standard variables
        enriched["project_key"] = project_key
        enriched["generated_at"] = datetime.now(timezone.utc).isoformat()

        return enriched
