# Blueprints Domain

## Overview

The Blueprints domain defines project blueprint entities that specify required and optional templates for structured project initialization.

## Responsibilities

- Define `Blueprint` entity structure
- Specify template requirements (required/optional)
- Define workflow stage requirements
- Provide request/response models for API layer

## Domain Models

### Blueprint (Entity)

Core domain entity representing a project blueprint.

**Fields:**
- `id`: Unique blueprint identifier
- `name`: Human-readable blueprint name
- `description`: Blueprint purpose and usage
- `required_templates`: List of template IDs that MUST be present
- `optional_templates`: List of template IDs that MAY be present
- `workflow_requirements`: Required workflow stages

**Validation:**
- `id` must be unique
- `name` must be non-empty
- Template IDs reference valid templates

### BlueprintCreate / BlueprintUpdate

Request models for API operations (BlueprintUpdate has optional fields for partial updates).

## Usage

### Creating a Blueprint

```python
from apps.api.domain.blueprints.models import BlueprintCreate

blueprint = BlueprintCreate(
    id="agile-sprint",
    name="Agile Sprint Project",
    description="Standard Agile sprint with planning, backlog, retrospective",
    required_templates=["sprint-plan", "backlog"],
    optional_templates=["retrospective", "burndown"],
    workflow_requirements=["planning", "execution", "review"]
)
```

### Updating a Blueprint

```python
from apps.api.domain.blueprints.models import BlueprintUpdate

update = BlueprintUpdate(
    description="Updated description",
    optional_templates=["retrospective", "burndown", "velocity-chart"]
)
```

## Design Notes

- **SRP Compliance**: Blueprints focus ONLY on template and workflow composition
- **No Infrastructure Dependencies**: Pure domain logic, no database/HTTP concerns
- **Immutability**: Blueprint ID is immutable after creation (only name/description/templates can change)
