"""
Template validation logic.

JSON Schema validation for template schemas.
Following DDD principles: validation layer, SRP, no infrastructure dependencies.
"""

import jsonschema
from typing import Dict, Any, Optional


class TemplateValidationError(Exception):
    """Raised when template validation fails."""

    pass


def validate_json_schema(schema: Dict[str, Any]) -> None:
    """
    Validate that a dictionary is a valid JSON Schema.

    Args:
        schema: Dictionary to validate as JSON Schema

    Raises:
        TemplateValidationError: If schema is invalid
    """
    try:
        # Validate against JSON Schema meta-schema (draft-07)
        validator = jsonschema.Draft7Validator
        validator.check_schema(schema)
    except jsonschema.SchemaError as e:
        raise TemplateValidationError(f"Invalid JSON Schema: {e.message}") from e


class TemplateValidator:
    """Validator for template schemas against specific artifact requirements."""

    # Required fields for each artifact type
    REQUIRED_FIELDS_BY_TYPE = {
        "pmp": [
            "purpose",
            "scope",
            "deliverables",
            "milestones",
            "roles",
            "communications",
            "change_control",
        ],
        "raid": ["type", "description", "owner", "status", "impact", "due_date"],
    }

    @classmethod
    def validate_template_schema(
        cls, schema: Dict[str, Any], artifact_type: str
    ) -> None:
        """
        Validate template schema has required fields for artifact type.

        Args:
            schema: JSON Schema to validate
            artifact_type: Artifact type (pmp, raid, etc.)

        Raises:
            TemplateValidationError: If schema is missing required fields
        """
        # First validate it's a valid JSON Schema
        validate_json_schema(schema)

        # Then check artifact-specific requirements
        required_fields = cls.REQUIRED_FIELDS_BY_TYPE.get(artifact_type)
        if not required_fields:
            # No specific requirements for this artifact type
            return

        # Check schema has properties for all required fields
        properties = schema.get("properties", {})
        missing_fields = [f for f in required_fields if f not in properties]

        if missing_fields:
            raise TemplateValidationError(
                f"Template schema for {artifact_type} missing required fields: "
                f"{', '.join(missing_fields)}"
            )

    @classmethod
    def validate_data_against_schema(
        cls, data: Dict[str, Any], schema: Dict[str, Any]
    ) -> Optional[str]:
        """
        Validate data against a JSON Schema.

        Args:
            data: Data to validate
            schema: JSON Schema to validate against

        Returns:
            Error message if validation fails, None if successful
        """
        try:
            jsonschema.validate(instance=data, schema=schema)
            return None
        except jsonschema.ValidationError as e:
            return str(e.message)
