"""
Blueprint domain models.

Contains all Pydantic models for project blueprints.
Following DDD principles: domain layer, SRP, no infrastructure dependencies.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class Blueprint(BaseModel):
    """Blueprint domain entity."""

    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(..., description="Unique blueprint identifier")
    name: str = Field(..., description="Human-readable blueprint name")
    description: str = Field(..., description="Blueprint purpose and usage")
    required_templates: List[str] = Field(
        default_factory=list, description="List of required template IDs"
    )
    optional_templates: List[str] = Field(
        default_factory=list, description="List of optional template IDs"
    )
    workflow_requirements: List[str] = Field(
        default_factory=list, description="Required workflow stages"
    )


class BlueprintCreate(BaseModel):
    """Request model for creating a blueprint."""

    model_config = ConfigDict(protected_namespaces=())

    id: str = Field(..., description="Unique blueprint identifier")
    name: str = Field(..., description="Human-readable blueprint name")
    description: str = Field(..., description="Blueprint purpose and usage")
    required_templates: List[str] = Field(
        default_factory=list, description="List of required template IDs"
    )
    optional_templates: List[str] = Field(
        default_factory=list, description="List of optional template IDs"
    )
    workflow_requirements: List[str] = Field(
        default_factory=list, description="Required workflow stages"
    )


class BlueprintUpdate(BaseModel):
    """Request model for updating a blueprint."""

    model_config = ConfigDict(protected_namespaces=())

    name: Optional[str] = Field(None, description="Human-readable blueprint name")
    description: Optional[str] = Field(None, description="Blueprint purpose and usage")
    required_templates: Optional[List[str]] = Field(
        None, description="List of required template IDs"
    )
    optional_templates: Optional[List[str]] = Field(
        None, description="List of optional template IDs"
    )
    workflow_requirements: Optional[List[str]] = Field(
        None, description="Required workflow stages"
    )
