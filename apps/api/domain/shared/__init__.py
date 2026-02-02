"""
Shared domain utilities.

Cross-cutting validation and utility functions used across multiple domains.
"""

from .validators import validate_enum_value, validate_dict_structure

__all__ = [
    "validate_enum_value",
    "validate_dict_structure",
]
