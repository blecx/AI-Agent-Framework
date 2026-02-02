"""Integration tests for BlueprintService."""

import pytest
import tempfile
import shutil
from pathlib import Path

from apps.api.domain.blueprints.models import BlueprintCreate, BlueprintUpdate
from apps.api.domain.templates.models import TemplateCreate
from apps.api.services.blueprint_service import BlueprintService
from apps.api.services.template_service import TemplateService
from apps.api.services.git_manager import GitManager


@pytest.fixture
def temp_project_docs():
    """Create temporary project docs directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def git_manager(temp_project_docs):
    """Create GitManager with temporary directory."""
    return GitManager(temp_project_docs)


@pytest.fixture
def blueprint_service(git_manager):
    """Create BlueprintService instance."""
    git_manager.ensure_repository()
    return BlueprintService(git_manager=git_manager, project_key="system")


@pytest.fixture
def template_service(git_manager):
    """Create TemplateService instance."""
    return TemplateService(git_manager=git_manager, project_key="system")


class TestBlueprintServiceCRUD:
    """Test BlueprintService CRUD operations."""

    def test_create_blueprint_success(self, blueprint_service):
        """Test creating a blueprint successfully."""
        blueprint_create = BlueprintCreate(
            id="test-bp",
            name="Test Blueprint",
            description="A test blueprint",
            required_templates=[],
            optional_templates=[],
            workflow_requirements=["initiating"],
        )

        blueprint = blueprint_service.create_blueprint(blueprint_create)

        assert blueprint.id == "test-bp"
        assert blueprint.name == "Test Blueprint"
        assert blueprint.workflow_requirements == ["initiating"]

    def test_create_blueprint_duplicate_id(self, blueprint_service):
        """Test creating blueprint with duplicate ID fails."""
        blueprint_create = BlueprintCreate(
            id="test-bp", name="Test Blueprint", description="First blueprint"
        )

        blueprint_service.create_blueprint(blueprint_create)

        # Try to create duplicate
        duplicate = BlueprintCreate(
            id="test-bp", name="Duplicate Blueprint", description="Should fail"
        )

        with pytest.raises(ValueError) as exc_info:
            blueprint_service.create_blueprint(duplicate)

        assert "already exists" in str(exc_info.value)

    def test_create_blueprint_invalid_template_reference(
        self, blueprint_service, template_service
    ):
        """Test creating blueprint with non-existent template fails."""
        blueprint_create = BlueprintCreate(
            id="test-bp",
            name="Test Blueprint",
            description="Blueprint with invalid template",
            required_templates=["non-existent-template"],
        )

        with pytest.raises(ValueError) as exc_info:
            blueprint_service.create_blueprint(blueprint_create)

        assert "does not exist" in str(exc_info.value)

    def test_create_blueprint_valid_template_reference(
        self, blueprint_service, template_service
    ):
        """Test creating blueprint with valid template reference."""
        # First create a template
        template_create = TemplateCreate(
            name="Test Template",
            description="A test template",
            schema={"type": "object"},
            markdown_template="# Test",
            artifact_type="pmp",
            version="1.0.0",
        )
        template = template_service.create_template(template_create)

        # Now create blueprint referencing it
        blueprint_create = BlueprintCreate(
            id="test-bp",
            name="Test Blueprint",
            description="Blueprint with valid template",
            required_templates=[template.id],
        )

        blueprint = blueprint_service.create_blueprint(blueprint_create)
        assert template.id in blueprint.required_templates

    def test_get_blueprint_success(self, blueprint_service):
        """Test retrieving a blueprint by ID."""
        blueprint_create = BlueprintCreate(
            id="test-bp", name="Test Blueprint", description="A test blueprint"
        )

        blueprint_service.create_blueprint(blueprint_create)
        retrieved = blueprint_service.get_blueprint("test-bp")

        assert retrieved is not None
        assert retrieved.id == "test-bp"
        assert retrieved.name == "Test Blueprint"

    def test_get_blueprint_not_found(self, blueprint_service):
        """Test retrieving non-existent blueprint returns None."""
        blueprint = blueprint_service.get_blueprint("non-existent")
        assert blueprint is None

    def test_list_blueprints_empty(self, blueprint_service):
        """Test listing blueprints when none exist."""
        blueprints = blueprint_service.list_blueprints()
        assert blueprints == []

    def test_list_blueprints_multiple(self, blueprint_service):
        """Test listing multiple blueprints."""
        # Create multiple blueprints
        for i in range(3):
            blueprint_create = BlueprintCreate(
                id=f"bp-{i}", name=f"Blueprint {i}", description=f"Blueprint number {i}"
            )
            blueprint_service.create_blueprint(blueprint_create)

        blueprints = blueprint_service.list_blueprints()
        assert len(blueprints) == 3
        assert all(bp.id.startswith("bp-") for bp in blueprints)

    def test_update_blueprint_success(self, blueprint_service):
        """Test updating a blueprint."""
        # Create blueprint
        blueprint_create = BlueprintCreate(
            id="test-bp", name="Original Name", description="Original description"
        )
        blueprint_service.create_blueprint(blueprint_create)

        # Update it
        blueprint_update = BlueprintUpdate(
            name="Updated Name", description="Updated description"
        )
        updated = blueprint_service.update_blueprint("test-bp", blueprint_update)

        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"

    def test_update_blueprint_not_found(self, blueprint_service):
        """Test updating non-existent blueprint fails."""
        blueprint_update = BlueprintUpdate(name="New Name")

        with pytest.raises(ValueError) as exc_info:
            blueprint_service.update_blueprint("non-existent", blueprint_update)

        assert "not found" in str(exc_info.value)

    def test_update_blueprint_templates(self, blueprint_service, template_service):
        """Test updating blueprint templates."""
        # Create template
        template_create = TemplateCreate(
            name="Test Template",
            description="A test template",
            schema={"type": "object"},
            markdown_template="# Test",
            artifact_type="pmp",
            version="1.0.0",
        )
        template = template_service.create_template(template_create)

        # Create blueprint
        blueprint_create = BlueprintCreate(
            id="test-bp", name="Test Blueprint", description="Test"
        )
        blueprint_service.create_blueprint(blueprint_create)

        # Update with template reference
        blueprint_update = BlueprintUpdate(required_templates=[template.id])
        updated = blueprint_service.update_blueprint("test-bp", blueprint_update)

        assert template.id in updated.required_templates

    def test_delete_blueprint_success(self, blueprint_service):
        """Test deleting a blueprint."""
        # Create blueprint
        blueprint_create = BlueprintCreate(
            id="test-bp", name="Test Blueprint", description="To be deleted"
        )
        blueprint_service.create_blueprint(blueprint_create)

        # Delete it
        blueprint_service.delete_blueprint("test-bp")

        # Verify it's gone
        blueprint = blueprint_service.get_blueprint("test-bp")
        assert blueprint is None

    def test_delete_blueprint_not_found(self, blueprint_service):
        """Test deleting non-existent blueprint fails."""
        with pytest.raises(ValueError) as exc_info:
            blueprint_service.delete_blueprint("non-existent")

        assert "not found" in str(exc_info.value)
