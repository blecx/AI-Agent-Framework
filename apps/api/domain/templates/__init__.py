"""
Templates domain.

Core domain models and validation for artifact templates.
"""

from .models import Template, TemplateCreate, TemplateUpdate
from .validators import validate_json_schema, TemplateValidator

__all__ = [
    "Template",
    "TemplateCreate",
    "TemplateUpdate",
    "validate_json_schema",
    "TemplateValidator",
]
