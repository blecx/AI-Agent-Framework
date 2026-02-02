"""
Unit tests for Template domain models.
"""

import pytest
from pydantic import ValidationError
from apps.api.domain.templates.models import Template, TemplateCreate, TemplateUpdate


class TestTemplateModel:
    """Test Template domain entity."""

    def test_create_valid_template(self):
        """Test creating a valid Template."""
        template = Template(
            id="tpl_001",
            name="PMP Template",
            description="Project Management Plan template",
            schema={"type": "object", "properties": {"name": {"type": "string"}}},
            markdown_template="# {{project_name}}",
            artifact_type="pmp",
            version="1.0.0",
        )

        assert template.id == "tpl_001"
        assert template.name == "PMP Template"
        assert template.description == "Project Management Plan template"
        assert template.schema["type"] == "object"
        assert template.markdown_template == "# {{project_name}}"
        assert template.artifact_type == "pmp"
        assert template.version == "1.0.0"

    def test_template_default_version(self):
        """Test Template uses default version when not specified."""
        template = Template(
            id="tpl_002",
            name="Test Template",
            description="Test",
            schema={"type": "object"},
            markdown_template="# Test",
            artifact_type="raid",
        )

        assert template.version == "1.0.0"

    def test_template_invalid_artifact_type(self):
        """Test Template rejects invalid artifact_type."""
        with pytest.raises(ValidationError) as exc_info:
            Template(
                id="tpl_003",
                name="Invalid Template",
                description="Test",
                schema={"type": "object"},
                markdown_template="# Test",
                artifact_type="invalid_type",
            )

        error = exc_info.value.errors()[0]
        assert "artifact_type must be one of" in str(error["ctx"]["error"])
        assert "invalid_type" in str(error["ctx"]["error"])

    def test_template_allowed_artifact_types(self):
        """Test all allowed artifact types are accepted."""
        allowed_types = ["pmp", "raid", "blueprint", "proposal", "report"]

        for artifact_type in allowed_types:
            template = Template(
                id=f"tpl_{artifact_type}",
                name=f"{artifact_type} Template",
                description="Test",
                schema={"type": "object"},
                markdown_template="# Test",
                artifact_type=artifact_type,
            )
            assert template.artifact_type == artifact_type

    def test_template_missing_required_fields(self):
        """Test Template raises ValidationError when required fields missing."""
        with pytest.raises(ValidationError) as exc_info:
            Template(
                id="tpl_004",
                name="Incomplete Template",
                # Missing: description, schema, markdown_template, artifact_type
            )

        errors = exc_info.value.errors()
        missing_fields = {e["loc"][0] for e in errors}
        assert "description" in missing_fields
        assert "schema" in missing_fields
        assert "markdown_template" in missing_fields
        assert "artifact_type" in missing_fields

    def test_template_schema_must_be_dict(self):
        """Test Template rejects non-dict schema."""
        with pytest.raises(ValidationError) as exc_info:
            Template(
                id="tpl_005",
                name="Bad Schema Template",
                description="Test",
                schema="not a dict",  # Invalid
                markdown_template="# Test",
                artifact_type="pmp",
            )

        errors = exc_info.value.errors()
        # Pydantic validation error for wrong type
        assert len(errors) > 0
        assert errors[0]["loc"][0] == "schema"

    def test_template_schema_must_have_type(self):
        """Test Template rejects schema without 'type' field."""
        with pytest.raises(ValidationError) as exc_info:
            Template(
                id="tpl_006",
                name="Missing Type Template",
                description="Test",
                schema={"properties": {}},  # Missing 'type'
                markdown_template="# Test",
                artifact_type="raid",
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert errors[0]["loc"][0] == "schema"


class TestTemplateCreateModel:
    """Test TemplateCreate request model."""

    def test_create_valid_template_create(self):
        """Test creating a valid TemplateCreate."""
        template_create = TemplateCreate(
            name="New Template",
            description="New template description",
            schema={"type": "object"},
            markdown_template="# {{title}}",
            artifact_type="blueprint",
            version="2.0.0",
        )

        assert template_create.name == "New Template"
        assert template_create.description == "New template description"
        assert template_create.artifact_type == "blueprint"
        assert template_create.version == "2.0.0"

    def test_template_create_default_version(self):
        """Test TemplateCreate uses default version."""
        template_create = TemplateCreate(
            name="New Template",
            description="Test",
            schema={"type": "object"},
            markdown_template="# Test",
            artifact_type="report",
        )

        assert template_create.version == "1.0.0"


class TestTemplateUpdateModel:
    """Test TemplateUpdate request model."""

    def test_create_valid_template_update(self):
        """Test creating a valid TemplateUpdate with all fields."""
        template_update = TemplateUpdate(
            name="Updated Name",
            description="Updated description",
            schema={"type": "object", "properties": {}},
            markdown_template="# Updated",
            artifact_type="pmp",
            version="1.1.0",
        )

        assert template_update.name == "Updated Name"
        assert template_update.version == "1.1.0"

    def test_template_update_partial_fields(self):
        """Test TemplateUpdate allows partial updates."""
        template_update = TemplateUpdate(
            name="New Name Only",
        )

        assert template_update.name == "New Name Only"
        assert template_update.description is None
        assert template_update.schema is None
        assert template_update.markdown_template is None
        assert template_update.artifact_type is None
        assert template_update.version is None

    def test_template_update_all_none(self):
        """Test TemplateUpdate allows all fields to be None."""
        template_update = TemplateUpdate()

        assert template_update.name is None
        assert template_update.description is None
        assert template_update.schema is None
        assert template_update.markdown_template is None
        assert template_update.artifact_type is None
        assert template_update.version is None
