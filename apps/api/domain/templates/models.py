"""
Template domain models.

Contains all Pydantic models for artifact templates.
Following DDD principles: domain layer, SRP, no infrastructure dependencies.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, Any, Optional


class Template(BaseModel):
    """Template domain entity."""

    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template purpose and usage")
    schema: Dict[str, Any] = Field(..., description="JSON Schema for validation")
    markdown_template: str = Field(..., description="Jinja2 template content")
    artifact_type: str = Field(..., description="Artifact type (pmp, raid, etc.)")
    version: str = Field(default="1.0.0", description="Template version")

    @field_validator("artifact_type")
    @classmethod
    def validate_artifact_type(cls, v: str) -> str:
        """
        Validate artifact_type is one of allowed values.

        Args:
            v: The artifact_type value to validate

        Returns:
            The validated artifact_type

        Raises:
            ValueError: If artifact_type not in allowed set
        """
        allowed_types = {"pmp", "raid", "blueprint", "proposal", "report"}
        if v not in allowed_types:
            from domain.errors import invalid_field

            raise ValueError(
                invalid_field(
                    "artifact_type", f"must be one of {allowed_types}, got '{v}'"
                )
            )
        return v

    @field_validator("schema")
    @classmethod
    def validate_schema_structure(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate schema has basic JSON Schema structure.

        Args:
            v: The schema dictionary to validate

        Returns:
            The validated schema dictionary

        Raises:
            ValueError: If schema is not a dict or missing 'type' field
        """
        if not isinstance(v, dict):
            from domain.errors import invalid_field

            raise ValueError(invalid_field("schema", "must be a dictionary"))
        if "type" not in v:
            from domain.errors import invalid_field

            raise ValueError(invalid_field("schema", "missing required field 'type'"))
        return v


class TemplateCreate(BaseModel):
    """Request model for creating a template."""

    model_config = ConfigDict(protected_namespaces=())

    name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template purpose and usage")
    schema: Dict[str, Any] = Field(..., description="JSON Schema for validation")
    markdown_template: str = Field(..., description="Jinja2 template content")
    artifact_type: str = Field(..., description="Artifact type (pmp, raid, etc.)")
    version: str = Field(default="1.0.0", description="Template version")


class TemplateUpdate(BaseModel):
    """Request model for updating a template."""

    model_config = ConfigDict(protected_namespaces=())

    name: Optional[str] = Field(None, description="Human-readable template name")
    description: Optional[str] = Field(None, description="Template purpose")
    schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema")
    markdown_template: Optional[str] = Field(None, description="Jinja2 template")
    artifact_type: Optional[str] = Field(None, description="Artifact type")
    version: Optional[str] = Field(None, description="Template version")
