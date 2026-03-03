"""
Unit tests for Template validators.
"""

import pytest
from apps.api.domain.templates.validators import (
    validate_json_schema,
    TemplateValidator,
    TemplateValidationError,
)


class TestValidateJsonSchema:
    """Test JSON Schema validation function."""

    def test_valid_json_schema(self):
        """Test validating a valid JSON Schema."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name"],
        }

        # Should not raise any exception
        validate_json_schema(schema)

    def test_valid_complex_schema(self):
        """Test validating a complex valid JSON Schema."""
        schema = {
            "type": "object",
            "properties": {
                "project": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "team": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "budget": {"type": "number", "minimum": 0},
            },
            "required": ["project"],
        }

        validate_json_schema(schema)

    def test_invalid_json_schema_wrong_type(self):
        """Test validating an invalid JSON Schema with wrong type."""
        schema = {
            "type": "invalid_type",  # Invalid type
            "properties": {},
        }

        with pytest.raises(TemplateValidationError) as exc_info:
            validate_json_schema(schema)

        assert "Invalid JSON Schema" in str(exc_info.value)

    def test_invalid_json_schema_malformed(self):
        """Test validating a malformed JSON Schema."""
        schema = {
            "properties": {
                "field": {
                    "type": "string",
                    "minimum": "not a number",  # Invalid: minimum on string type
                }
            }
        }

        with pytest.raises(TemplateValidationError) as exc_info:
            validate_json_schema(schema)

        assert "Invalid JSON Schema" in str(exc_info.value)

    def test_empty_schema(self):
        """Test validating an empty schema (valid, matches anything)."""
        schema = {}
        validate_json_schema(schema)

    def test_schema_with_definitions(self):
        """Test validating schema with definitions."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "definitions": {
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                    },
                }
            },
            "type": "object",
            "properties": {"home": {"$ref": "#/definitions/address"}},
        }

        validate_json_schema(schema)


class TestTemplateValidatorPMP:
    """Test TemplateValidator for PMP templates."""

    def test_valid_pmp_template_schema(self):
        """Test validating a valid PMP template schema."""
        schema = {
            "type": "object",
            "properties": {
                "purpose": {"type": "string"},
                "scope": {"type": "string"},
                "deliverables": {"type": "array", "items": {"type": "string"}},
                "milestones": {"type": "array"},
                "roles": {"type": "object"},
                "communications": {"type": "string"},
                "change_control": {"type": "string"},
            },
            "required": [
                "purpose",
                "scope",
                "deliverables",
                "milestones",
                "roles",
                "communications",
                "change_control",
            ],
        }

        # Should not raise any exception
        TemplateValidator.validate_template_schema(schema, "pmp")

    def test_pmp_template_missing_purpose(self):
        """Test PMP template missing 'purpose' field."""
        schema = {
            "type": "object",
            "properties": {
                # Missing: purpose
                "scope": {"type": "string"},
                "deliverables": {"type": "array"},
                "milestones": {"type": "array"},
                "roles": {"type": "object"},
                "communications": {"type": "string"},
                "change_control": {"type": "string"},
            },
        }

        with pytest.raises(TemplateValidationError) as exc_info:
            TemplateValidator.validate_template_schema(schema, "pmp")

        error_msg = str(exc_info.value)
        assert "missing required fields" in error_msg
        assert "purpose" in error_msg

    def test_pmp_template_missing_multiple_fields(self):
        """Test PMP template missing multiple required fields."""
        schema = {
            "type": "object",
            "properties": {
                "purpose": {"type": "string"},
                "scope": {"type": "string"},
                # Missing: deliverables, milestones, roles, communications, change_control
            },
        }

        with pytest.raises(TemplateValidationError) as exc_info:
            TemplateValidator.validate_template_schema(schema, "pmp")

        error_msg = str(exc_info.value)
        assert "deliverables" in error_msg
        assert "milestones" in error_msg
        assert "roles" in error_msg
        assert "communications" in error_msg
        assert "change_control" in error_msg


class TestTemplateValidatorRAID:
    """Test TemplateValidator for RAID templates."""

    def test_valid_raid_template_schema(self):
        """Test validating a valid RAID template schema."""
        schema = {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["risk", "assumption", "issue", "dependency"],
                },
                "description": {"type": "string"},
                "owner": {"type": "string"},
                "status": {"type": "string"},
                "impact": {"type": "string"},
                "due_date": {"type": "string", "format": "date"},
            },
            "required": [
                "type",
                "description",
                "owner",
                "status",
                "impact",
                "due_date",
            ],
        }

        # Should not raise any exception
        TemplateValidator.validate_template_schema(schema, "raid")

    def test_raid_template_missing_type(self):
        """Test RAID template missing 'type' field."""
        schema = {
            "type": "object",
            "properties": {
                # Missing: type
                "description": {"type": "string"},
                "owner": {"type": "string"},
                "status": {"type": "string"},
                "impact": {"type": "string"},
                "due_date": {"type": "string"},
            },
        }

        with pytest.raises(TemplateValidationError) as exc_info:
            TemplateValidator.validate_template_schema(schema, "raid")

        error_msg = str(exc_info.value)
        assert "missing required fields" in error_msg
        assert "type" in error_msg

    def test_raid_template_missing_multiple_fields(self):
        """Test RAID template missing multiple required fields."""
        schema = {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "description": {"type": "string"},
                # Missing: owner, status, impact, due_date
            },
        }

        with pytest.raises(TemplateValidationError) as exc_info:
            TemplateValidator.validate_template_schema(schema, "raid")

        error_msg = str(exc_info.value)
        assert "owner" in error_msg
        assert "status" in error_msg
        assert "impact" in error_msg
        assert "due_date" in error_msg


class TestTemplateValidatorOtherTypes:
    """Test TemplateValidator for other artifact types."""

    def test_unknown_artifact_type_no_requirements(self):
        """Test artifact type with no specific requirements."""
        schema = {
            "type": "object",
            "properties": {"custom_field": {"type": "string"}},
        }

        # Should not raise - no specific requirements for 'blueprint'
        TemplateValidator.validate_template_schema(schema, "blueprint")

    def test_invalid_json_schema_detected(self):
        """Test that invalid JSON Schema is detected before artifact checks."""
        schema = {
            "type": "invalid_type",  # Invalid
            "properties": {
                "purpose": {"type": "string"},
                "scope": {"type": "string"},
            },
        }

        with pytest.raises(TemplateValidationError) as exc_info:
            TemplateValidator.validate_template_schema(schema, "pmp")

        assert "Invalid JSON Schema" in str(exc_info.value)


class TestValidateDataAgainstSchema:
    """Test data validation against JSON Schema."""

    def test_valid_data_against_schema(self):
        """Test validating valid data against schema."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name"],
        }
        data = {"name": "John Doe", "age": 30}

        error = TemplateValidator.validate_data_against_schema(data, schema)

        assert error is None

    def test_invalid_data_missing_required_field(self):
        """Test validating data missing required field."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        data = {}  # Missing required 'name'

        error = TemplateValidator.validate_data_against_schema(data, schema)

        assert error is not None
        assert "required" in error.lower() or "name" in error.lower()

    def test_invalid_data_wrong_type(self):
        """Test validating data with wrong type."""
        schema = {
            "type": "object",
            "properties": {"age": {"type": "integer"}},
        }
        data = {"age": "not an integer"}

        error = TemplateValidator.validate_data_against_schema(data, schema)

        assert error is not None
        assert "integer" in error.lower() or "type" in error.lower()

    def test_valid_data_extra_fields_allowed(self):
        """Test that extra fields are allowed by default."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        data = {"name": "Jane", "extra_field": "allowed"}

        error = TemplateValidator.validate_data_against_schema(data, schema)

        assert error is None

    def test_invalid_data_array_type_mismatch(self):
        """Test validating array data with type mismatch."""
        schema = {
            "type": "object",
            "properties": {"tags": {"type": "array", "items": {"type": "string"}}},
        }
        data = {"tags": ["valid", 123, "another"]}  # 123 is not a string

        error = TemplateValidator.validate_data_against_schema(data, schema)

        assert error is not None
