# Projects Domain

## Overview

The Projects domain defines core project entity and state aggregation for ISO 21500-aligned project management.

## Responsibilities

- Define `ProjectInfo` entity structure
- Manage project metadata (key, name, methodology)
- Aggregate project state (info + artifacts + commits)
- Provide request/response models for API layer

## Domain Models

### ProjectInfo (Entity)

Core project metadata.

**Fields:**

- `key`: Unique project identifier (alphanumeric, dash, underscore only)
- `name`: Human-readable project name
- `methodology`: Project management methodology (default: "ISO21500")
- `created_at`: Creation timestamp (ISO format)
- `updated_at`: Last update timestamp (ISO format)

**Validation:**

- `key` must match pattern `^[a-zA-Z0-9_-]+$`
- `key` must be unique across all projects
- `name` must be non-empty

### ProjectCreate

Request model for creating a new project.

**Fields:**

- `key`: Unique project key (required, pattern validated)
- `name`: Project name (required)

**Usage:**

```python
from apps.api.domain.projects.models import ProjectCreate

project = ProjectCreate(
    key="ONBOARD-2025",
    name="Customer Onboarding Portal"
)
```

### ProjectUpdate

Request model for updating project metadata.

**Fields:**

- `name`: New project name (optional, min length 1)
- `methodology`: New methodology (optional)

**Usage:**

```python
from apps.api.domain.projects.models import ProjectUpdate

update = ProjectUpdate(
    name="Customer Onboarding Portal v2"
)
```

### ProjectState

Aggregated project state including artifacts and git history.

**Fields:**

- `project_info`: ProjectInfo entity
- `artifacts`: List of artifact metadata (path, type, timestamps)
- `last_commit`: Most recent git commit metadata (hash, message, author, timestamp)

**Usage:**

```python
from apps.api.domain.projects.models import ProjectState

# Service layer returns aggregated state:
state = ProjectState(
    project_info=ProjectInfo(
        key="ONBOARD-2025",
        name="Customer Onboarding Portal",
        methodology="ISO21500",
        created_at="2025-02-01T10:00:00Z",
        updated_at="2025-02-10T15:30:00Z"
    ),
    artifacts=[
        {"path": "artifacts/pmp.md", "type": "pmp", "created_at": "2025-02-01T10:05:00Z"},
        {"path": "artifacts/raid.md", "type": "raid", "created_at": "2025-02-01T10:10:00Z"}
    ],
    last_commit={
        "hash": "abc123",
        "message": "[ONBOARD-2025] Updated RAID register",
        "author": "john.doe@example.com",
        "timestamp": "2025-02-10T15:30:00Z"
    }
)
```

### ArtifactInfo

Metadata for individual artifacts within a project.

**Fields:**

- `path`: Relative path within project docs
- `type`: Artifact type (pmp, raid, blueprint, etc.)
- `created_at`: Creation timestamp (ISO format)
- `updated_at`: Last update timestamp (ISO format, optional)

## Storage Model

Projects are stored in `projectDocs/<PROJECT_KEY>/` directories with git-based versioning:

```text
projectDocs/
└── ONBOARD-2025/
    ├── .git/                    # Git repository for versioning
    ├── project.json             # ProjectInfo metadata
    ├── artifacts/
    │   ├── pmp.md               # Project Management Plan
    │   ├── raid.md              # RAID Register
    │   └── blueprint.json       # Blueprint configuration
    ├── workflow/
    │   └── state.json           # Workflow state
    ├── governance/
    │   ├── metadata.json        # Governance structure
    │   └── decisions.ndjson     # Decision log
    └── audit/
        └── events.ndjson        # Audit events
```

## Usage

### Creating a Project

```python
from apps.api.domain.projects.models import ProjectCreate

project_req = ProjectCreate(
    key="MYPROJ-2025",
    name="My New Project"
)

# Service layer:
# 1. Validates key uniqueness
# 2. Creates projectDocs/MYPROJ-2025/ directory
# 3. Initializes git repository
# 4. Creates project.json with metadata
# 5. Creates initial artifacts/ directory
```

### Updating Project

```python
from apps.api.domain.projects.models import ProjectUpdate

update = ProjectUpdate(
    name="My Updated Project Name",
    methodology="Agile"
)

# Service layer updates project.json and commits change
```

### Querying Project State

```python
# Service layer aggregates:
# - ProjectInfo from project.json
# - Artifacts from filesystem scan
# - Last commit from git log

state = get_project_state("MYPROJ-2025")
print(f"Project: {state.project_info.name}")
print(f"Artifacts: {len(state.artifacts)}")
print(f"Last change: {state.last_commit['message']}")
```

## Design Notes

- **SRP Compliance**: Projects domain focuses ONLY on project entity and metadata, not artifact content
- **Git-Based Storage**: Each project is a git repository for versioning and audit trails
- **ISO 21500 Alignment**: Methodology field supports ISO 21500 by default
- **Key Immutability**: Project key cannot change after creation (used as directory name)
- **State Aggregation**: ProjectState provides unified view of project for dashboards
- **No Infrastructure Dependencies**: Pure domain models, storage handled by service layer
