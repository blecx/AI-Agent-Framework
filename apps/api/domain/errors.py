"""
Error Message Style Guide and Templates

This module defines standardized error message formats for consistent
error reporting across all API services.

## Style Guide

### Not Found Errors
Format: `{EntityType} {identifier} not found`
Examples:
- "Project TEST-123 not found"
- "Template template-001 not found"
- "Blueprint blueprint-v2 not found"
- "Proposal proposal-456 not found"
- "RAID item R-001 not found"

### Validation Errors
Format: `Invalid {field_name}: {reason}`
Examples:
- "Invalid artifact_type: must be one of ['charter', 'plan'], got 'unknown'"
- "Invalid schema: must be a dictionary"
- "Invalid schema: missing required field 'type'"

### State Errors
Format: `{EntityType} {identifier} is {state}: {reason}`
Examples:
- "Proposal proposal-123 is already applied: cannot apply twice"
- "Proposal proposal-456 is rejected: cannot apply rejected proposals"

### Reference Errors
Format: `Referenced {entity_type} {identifier} does not exist`
Examples:
- "Referenced template template-001 does not exist"
- "Referenced project TEST-999 does not exist"

## Error Message Catalog

### Projects
- Project not found: "Project {project_key} not found"
- Unknown command: "Unknown command: {command_name}"

### Templates
- Template exists: "Template {template_id} already exists"
- Template not found: "Template {template_id} not found"

### Blueprints
- Blueprint exists: "Blueprint {blueprint_id} already exists"
- Blueprint not found: "Blueprint {blueprint_id} not found"
- Referenced template: "Referenced template {template_id} does not exist"

### Proposals
- Proposal not found: "Proposal {proposal_id} not found"
- Proposal already applied: "Proposal {proposal_id} is already applied"
- Target artifact not found: "Target artifact {artifact_path} not found"

### RAID
- RAID item not found: "RAID item {raid_id} not found"

### Governance
- Governance not found: "Governance metadata not found for project {project_key}"

### Workflows
- Workflow not found: "Workflow not found for project {project_key}"
"""


def not_found(entity_type: str, identifier: str) -> str:
    """
    Generate standardized 'not found' error message.

    Args:
        entity_type: Type of entity (e.g., "Project", "Template")
        identifier: Entity identifier (e.g., "TEST-123", "template-001")

    Returns:
        Formatted error message

    Example:
        >>> not_found("Project", "TEST-123")
        'Project TEST-123 not found'
    """
    return f"{entity_type} {identifier} not found"


def invalid_field(field_name: str, reason: str) -> str:
    """
    Generate standardized validation error message.

    Args:
        field_name: Name of the invalid field
        reason: Explanation of why the field is invalid

    Returns:
        Formatted error message

    Example:
        >>> invalid_field("artifact_type", "must be one of ['charter', 'plan']")
        "Invalid artifact_type: must be one of ['charter', 'plan']"
    """
    return f"Invalid {field_name}: {reason}"


def entity_state_error(
    entity_type: str, identifier: str, state: str, reason: str
) -> str:
    """
    Generate standardized state error message.

    Args:
        entity_type: Type of entity (e.g., "Proposal")
        identifier: Entity identifier
        state: Current state that prevents the operation
        reason: Explanation of the constraint

    Returns:
        Formatted error message

    Example:
        >>> entity_state_error("Proposal", "prop-123", "already applied", "cannot apply twice")
        'Proposal prop-123 is already applied: cannot apply twice'
    """
    return f"{entity_type} {identifier} is {state}: {reason}"


def reference_not_found(entity_type: str, identifier: str) -> str:
    """
    Generate standardized reference error message.

    Args:
        entity_type: Type of referenced entity
        identifier: Entity identifier

    Returns:
        Formatted error message

    Example:
        >>> reference_not_found("template", "template-001")
        'Referenced template template-001 does not exist'
    """
    return f"Referenced {entity_type} {identifier} does not exist"
