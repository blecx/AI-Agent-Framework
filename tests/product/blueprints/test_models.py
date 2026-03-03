"""Unit tests for Blueprint domain models."""

import pytest
from pydantic import ValidationError

from apps.api.domain.blueprints.models import (
    Blueprint,
    BlueprintCreate,
    BlueprintUpdate,
)


class TestBlueprintModel:
    """Test Blueprint domain entity."""

    def test_blueprint_creation_minimal(self):
        """Test creating a blueprint with minimal fields."""
        blueprint = Blueprint(
            id="test-bp", name="Test Blueprint", description="A test blueprint"
        )

        assert blueprint.id == "test-bp"
        assert blueprint.name == "Test Blueprint"
        assert blueprint.description == "A test blueprint"
        assert blueprint.required_templates == []
        assert blueprint.optional_templates == []
        assert blueprint.workflow_requirements == []

    def test_blueprint_creation_full(self):
        """Test creating a blueprint with all fields."""
        blueprint = Blueprint(
            id="iso21500-minimal",
            name="ISO 21500 Minimal",
            description="Minimal ISO 21500 artifact set",
            required_templates=["pmp-v1", "raid-v1"],
            optional_templates=["schedule-v1"],
            workflow_requirements=["initiating", "planning", "executing"],
        )

        assert blueprint.id == "iso21500-minimal"
        assert blueprint.name == "ISO 21500 Minimal"
        assert len(blueprint.required_templates) == 2
        assert "pmp-v1" in blueprint.required_templates
        assert len(blueprint.optional_templates) == 1
        assert len(blueprint.workflow_requirements) == 3

    def test_blueprint_missing_required_fields(self):
        """Test blueprint creation fails with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            Blueprint(name="Missing ID")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("id",) for e in errors)


class TestBlueprintCreateModel:
    """Test BlueprintCreate request model."""

    def test_blueprint_create_minimal(self):
        """Test creating blueprint request with minimal fields."""
        blueprint_create = BlueprintCreate(
            id="test-bp", name="Test Blueprint", description="A test blueprint"
        )

        assert blueprint_create.id == "test-bp"
        assert blueprint_create.name == "Test Blueprint"
        assert blueprint_create.required_templates == []

    def test_blueprint_create_full(self):
        """Test creating blueprint request with all fields."""
        blueprint_create = BlueprintCreate(
            id="iso21500-minimal",
            name="ISO 21500 Minimal",
            description="Minimal ISO 21500 artifact set",
            required_templates=["pmp-v1", "raid-v1"],
            optional_templates=["schedule-v1"],
            workflow_requirements=["initiating", "planning"],
        )

        assert len(blueprint_create.required_templates) == 2
        assert len(blueprint_create.optional_templates) == 1
        assert len(blueprint_create.workflow_requirements) == 2


class TestBlueprintUpdateModel:
    """Test BlueprintUpdate request model."""

    def test_blueprint_update_partial(self):
        """Test updating blueprint with partial fields."""
        blueprint_update = BlueprintUpdate(name="Updated Name")

        assert blueprint_update.name == "Updated Name"
        assert blueprint_update.description is None
        assert blueprint_update.required_templates is None

    def test_blueprint_update_templates(self):
        """Test updating only templates."""
        blueprint_update = BlueprintUpdate(
            required_templates=["new-tpl-1", "new-tpl-2"]
        )

        assert blueprint_update.name is None
        assert len(blueprint_update.required_templates) == 2

    def test_blueprint_update_empty(self):
        """Test creating empty update (all None)."""
        blueprint_update = BlueprintUpdate()

        assert blueprint_update.name is None
        assert blueprint_update.description is None
        assert blueprint_update.required_templates is None
