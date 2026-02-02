"""
Shared validation utilities.

Reusable validation functions following DRY principle.
These validators can be used across all domain models.
"""

from typing import Any, Set, List, Optional


def validate_enum_value(value: Any, allowed_values: Set[str], field_name: str) -> None:
    """
    Validate that a value is one of allowed enum values.

    Args:
        value: The value to validate
        allowed_values: Set of allowed values
        field_name: Name of the field being validated (for error messages)

    Raises:
        ValueError: If value not in allowed_values
    """
    if value not in allowed_values:
        from domain.errors import invalid_field

        raise ValueError(
            invalid_field(
                field_name,
                f"must be one of {allowed_values}, got '{value}'",
            )
        )


def validate_dict_structure(
    value: Any,
    required_keys: Optional[List[str]] = None,
    field_name: str = "field",
) -> None:
    """
    Validate that a value is a dict with required keys.

    Args:
        value: The value to validate
        required_keys: Optional list of required keys
        field_name: Name of the field being validated (for error messages)

    Raises:
        ValueError: If value is not a dict or missing required keys
    """
    if not isinstance(value, dict):
        from domain.errors import invalid_field

        raise ValueError(invalid_field(field_name, "must be a dictionary"))

    if required_keys:
        missing = [key for key in required_keys if key not in value]
        if missing:
            from domain.errors import invalid_field

            raise ValueError(
                invalid_field(
                    field_name,
                    f"missing required key(s): {', '.join(missing)}",
                )
            )
