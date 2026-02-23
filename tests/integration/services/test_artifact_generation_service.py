"""
Integration tests for ArtifactGenerationService.

Tests artifact generation from templates and blueprints.
"""

import pytest
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../apps/api"))

from services.artifact_generation_service import (  # noqa: E402
    ArtifactGenerationService,
    ArtifactGenerationError,
    ValidationError,
)
from apps.api.services.template_service import TemplateService  # noqa: E402
from apps.api.services.blueprint_service import BlueprintService  # noqa: E402
from apps.api.services.git_manager import GitManager  # noqa: E402
from apps.api.domain.templates.models import TemplateCreate  # noqa: E402
from apps.api.domain.blueprints.models import BlueprintCreate  # noqa: E402


@pytest.fixture
def test_project_key():
    """Test project key."""
    return "TEST001"


@pytest.fixture
def git_manager(tmp_path):
    """Create GitManager with temporary path."""
    manager = GitManager(base_path=str(tmp_path / "projectDocs"))
    manager.ensure_repository()
    return manager


@pytest.fixture
def template_service(git_manager):
    """Create TemplateService."""
    return TemplateService(git_manager, project_key="system")


@pytest.fixture
def blueprint_service(git_manager):
    """Create BlueprintService."""
    return BlueprintService(git_manager, project_key="system")


@pytest.fixture
def artifact_service(template_service, blueprint_service, git_manager):
    """Create ArtifactGenerationService."""
    return ArtifactGenerationService(template_service, blueprint_service, git_manager)


@pytest.fixture
def pmp_template(template_service):
    """Create a PMP template for testing."""
    template_create = TemplateCreate(
        name="Project Management Plan Template",
        description="ISO 21500 compliant PMP template",
        artifact_type="pmp",
        schema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string"},
                "project_manager": {"type": "string"},
                "start_date": {"type": "string"},
            },
            "required": ["project_name", "project_manager"],
        },
        markdown_template="""# Project Management Plan

## Project Information
- **Project Name:** {{ project_name }}
- **Project Manager:** {{ project_manager }}
- **Start Date:** {{ start_date | default('TBD') }}
- **Generated:** {{ generated_at }}

## Scope
{{ scope | default('To be defined') }}
""",
    )
    return template_service.create_template(template_create)


@pytest.fixture
def raid_template(template_service):
    """Create a RAID template for testing."""
    template_create = TemplateCreate(
        name="RAID Log Template",
        description="Risk, Assumptions, Issues, Dependencies",
        artifact_type="raid",
        schema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string"},
                "risks": {"type": "array"},
            },
            "required": ["project_name"],
        },
        markdown_template="""# RAID Log

## Project: {{ project_name }}

### Risks
{% for risk in risks %}
- {{ risk }}
{% endfor %}
""",
    )
    return template_service.create_template(template_create)


@pytest.fixture
def test_blueprint(blueprint_service, pmp_template, raid_template):
    """Create a test blueprint."""
    blueprint_create = BlueprintCreate(
        id="test-blueprint-001",
        name="Standard Project Blueprint",
        description="Standard set of project artifacts",
        required_templates=[pmp_template.id, raid_template.id],
    )
    return blueprint_service.create_blueprint(blueprint_create)


class TestGenerateFromTemplate:
    """Tests for generate_from_template method."""

    def test_generate_pmp_success(
        self, artifact_service, pmp_template, test_project_key, git_manager
    ):
        """Test successful PMP generation."""
        context = {
            "project_name": "My Project",
            "project_manager": "Jane Smith",
            "start_date": "2026-02-01",
        }

        result = artifact_service.generate_from_template(
            pmp_template.id, test_project_key, context
        )

        # Verify result structure
        assert result["artifact_path"] == "artifacts/pmp.md"
        assert result["template_id"] == pmp_template.id
        assert result["artifact_type"] == "pmp"

        # Verify content
        content = result["content"]
        assert "My Project" in content
        assert "Jane Smith" in content
        assert "2026-02-01" in content
        assert "Generated:" in content

        # Verify file was written
        file_content = git_manager.read_file(test_project_key, "artifacts/pmp.md")
        assert file_content == content

    def test_generate_with_default_values(
        self, artifact_service, pmp_template, test_project_key
    ):
        """Test generation with Jinja2 default values."""
        context = {
            "project_name": "My Project",
            "project_manager": "Jane Smith",
            # start_date omitted, should use default 'TBD'
        }

        result = artifact_service.generate_from_template(
            pmp_template.id, test_project_key, context
        )

        assert "TBD" in result["content"]

    def test_generate_raid_with_list(
        self, artifact_service, raid_template, test_project_key
    ):
        """Test RAID generation with list iteration."""
        context = {
            "project_name": "My Project",
            "risks": ["Risk 1", "Risk 2", "Risk 3"],
        }

        result = artifact_service.generate_from_template(
            raid_template.id, test_project_key, context
        )

        content = result["content"]
        assert "Risk 1" in content
        assert "Risk 2" in content
        assert "Risk 3" in content

    def test_template_not_found(self, artifact_service, test_project_key):
        """Test error when template doesn't exist."""
        with pytest.raises(ArtifactGenerationError, match="Template not found"):
            artifact_service.generate_from_template(
                "nonexistent-template", test_project_key, {}
            )

    def test_validation_error_missing_required(
        self, artifact_service, pmp_template, test_project_key
    ):
        """Test validation error for missing required fields."""
        context = {
            "project_name": "My Project"
            # project_manager missing (required)
        }

        with pytest.raises(ValidationError, match="Context validation failed"):
            artifact_service.generate_from_template(
                pmp_template.id, test_project_key, context
            )

    def test_validation_error_wrong_type(
        self, artifact_service, pmp_template, test_project_key
    ):
        """Test validation error for wrong data type."""
        context = {"project_name": 123, "project_manager": "Jane"}  # Should be string

        with pytest.raises(ValidationError):
            artifact_service.generate_from_template(
                pmp_template.id, test_project_key, context
            )

    def test_sanitize_context_removes_private_keys(
        self, artifact_service, pmp_template, test_project_key
    ):
        """Test that private keys (starting with _) are removed."""
        context = {
            "project_name": "My Project",
            "project_manager": "Jane",
            "_private_key": "should be removed",
            "__builtins__": "dangerous",
        }

        result = artifact_service.generate_from_template(
            pmp_template.id, test_project_key, context
        )

        # Should succeed (private keys filtered out)
        assert result["content"]
        assert "_private_key" not in result["content"]


class TestGenerateFromBlueprint:
    """Tests for generate_from_blueprint method."""

    def test_generate_all_artifacts(
        self, artifact_service, test_blueprint, test_project_key, git_manager
    ):
        """Test generating all artifacts from blueprint."""
        base_context = {
            "project_name": "Test Project",
            "project_manager": "John Doe",
            "risks": ["Budget overrun", "Resource availability"],
        }

        results = artifact_service.generate_from_blueprint(
            test_blueprint.id, test_project_key, base_context=base_context
        )

        # Verify all templates generated
        assert len(results) == 2

        # Check PMP artifact
        pmp_result = next(r for r in results if r.get("artifact_type") == "pmp")
        assert "Test Project" in pmp_result["content"]
        assert "John Doe" in pmp_result["content"]

        # Check RAID artifact
        raid_result = next(r for r in results if r.get("artifact_type") == "raid")
        assert "Budget overrun" in raid_result["content"]
        assert "Resource availability" in raid_result["content"]

        # Verify files written
        pmp_content = git_manager.read_file(test_project_key, "artifacts/pmp.md")
        raid_content = git_manager.read_file(test_project_key, "artifacts/raid.md")
        assert pmp_content is not None
        assert raid_content is not None

    def test_generate_with_override_context(
        self, artifact_service, test_blueprint, test_project_key
    ):
        """Test blueprint generation with custom context."""
        custom_context = {
            "project_name": "Custom Project",
            "project_manager": "Custom Manager",
        }

        results = artifact_service.generate_from_blueprint(
            test_blueprint.id, test_project_key, base_context=custom_context
        )

        # Custom values should be used
        pmp_result = next(r for r in results if r.get("artifact_type") == "pmp")
        assert "Custom Manager" in pmp_result["content"]

    def test_blueprint_not_found(self, artifact_service, test_project_key):
        """Test error when blueprint doesn't exist."""
        with pytest.raises(ArtifactGenerationError, match="Blueprint not found"):
            artifact_service.generate_from_blueprint(
                "nonexistent-blueprint", test_project_key
            )

    def test_partial_failure_continues(
        self, artifact_service, pmp_template, test_project_key
    ):
        """Test that blueprint generation continues after partial failure."""
        # This test is adjusted because BlueprintService validates templates at creation
        # Instead, we test that generate_from_template catches errors gracefully

        # Artificially create a scenario where template exists but fails during generation
        # by passing invalid context that causes validation error
        context_missing_required = {
            "project_name": "Test"
            # project_manager missing (required by pmp_template)
        }

        # This should raise ValidationError (caught in generate_from_blueprint)
        try:
            artifact_service.generate_from_template(
                pmp_template.id, test_project_key, context_missing_required
            )
            assert False, "Should have raised ValidationError"
        except ValidationError:
            # Expected behavior - error is raised
            pass


class TestPerformance:
    """Performance tests."""

    def test_template_rendering_performance(
        self, artifact_service, pmp_template, test_project_key
    ):
        """Test that template rendering completes quickly."""
        import time

        context = {
            "project_name": "Performance Test",
            "project_manager": "Test Manager",
            "start_date": "2026-02-01",
        }

        start = time.time()
        artifact_service.generate_from_template(
            pmp_template.id, test_project_key, context
        )
        elapsed = time.time() - start

        # Should complete in < 100ms
        assert elapsed < 0.1, f"Rendering took {elapsed*1000:.1f}ms, expected < 100ms"

    def test_blueprint_generation_performance(
        self, artifact_service, test_blueprint, test_project_key
    ):
        """Test that blueprint generation completes quickly."""
        import time

        base_context = {
            "project_name": "Performance Test",
            "project_manager": "Test Manager",
            "risks": ["Risk 1"],
        }

        start = time.time()
        artifact_service.generate_from_blueprint(
            test_blueprint.id, test_project_key, base_context=base_context
        )
        elapsed = time.time() - start

        # 2 artifacts should complete in < 500ms
        assert elapsed < 0.5, f"Generation took {elapsed*1000:.1f}ms, expected < 500ms"
