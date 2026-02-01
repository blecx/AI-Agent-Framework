# Templates Domain

## Overview

The Templates domain provides foundational data models and validation logic for artifact templates used in ISO 21500 project management.

## Responsibilities

- Define `Template` entity structure
- Validate JSON Schema format for template schemas
- Validate template schemas against artifact-specific requirements
- Provide request/response models for API layer

## Domain Models

### Template (Entity)

Core domain entity representing an artifact template.

**Fields:**
- `id`: Unique identifier
- `name`: Human-readable name
- `description`: Purpose and usage
- `schema`: JSON Schema for artifact validation
- `markdown_template`: Jinja2 template content
- `artifact_type`: Type of artifact (pmp, raid, blueprint, proposal, report)
- `version`: Template version (semver)

**Validation:**
- `artifact_type` must be one of allowed values
- `schema` must be valid JSON Schema structure

### TemplateCreate / TemplateUpdate

Request models for API operations (no ID field for create, optional fields for update).

## Validation

### JSON Schema Validation

`validate_json_schema(schema)` validates a dictionary is valid JSON Schema (draft-07).

### Artifact-Specific Requirements

`TemplateValidator.validate_template_schema()` checks schemas meet artifact type requirements:

**PMP Template Requirements:**
- purpose, scope, deliverables, milestones, roles, communications, change_control

**RAID Template Requirements:**
- type, description, owner, status, impact, due_date

## Design Principles

- **SRP**: Models define structure, validators handle validation logic
- **Domain Layer**: No infrastructure dependencies (no persistence, no API)
- **Type Safety**: Explicit Pydantic models with field validation
- **Immutability**: Templates treated as value objects once created

## Usage Example

```python
from apps.api.domain.templates import Template, TemplateValidator

# Create template
template = Template(
    id="tpl_001",
    name="PMP Template",
    description="Project Management Plan template",
    schema={"type": "object", "properties": {...}},
    markdown_template="# {{project_name}}\\n...",
    artifact_type="pmp",
    version="1.0.0"
)

# Validate schema
TemplateValidator.validate_template_schema(
    template.schema,
    template.artifact_type
)
```

## Dependencies

- `pydantic`: Data validation and modeling
- `jsonschema>=4.20.0`: JSON Schema validation

## Testing

See `tests/unit/domain/templates/` for comprehensive test coverage.
