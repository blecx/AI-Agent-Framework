# Skills Domain

## Overview

The Skills domain defines cognitive skills interfaces for AI agents including memory management, planning, learning, and agent interaction capabilities.

## Responsibilities

- Define skill metadata structure
- Manage agent memory (short-term, long-term)
- Provide skill registration and discovery
- Support agent cognitive capabilities API

## Domain Models

### SkillInfo (Entity)

Metadata about a cognitive skill.

**Fields:**

- `name`: Skill name (e.g., "memory", "planning", "learning")
- `version`: Skill version (semver format)
- `description`: Skill purpose and capabilities
- `enabled`: Whether skill is currently active

**Validation:**

- `name` must be non-empty
- `version` should follow semver pattern
- `enabled` boolean flag

### SkillListResponse

Response model for listing available skills.

**Fields:**

- `skills`: List of SkillInfo objects
- `total`: Total count of skills

**Usage:**

```python
from apps.api.domain.skills.models import SkillListResponse, SkillInfo

response = SkillListResponse(
    skills=[
        SkillInfo(name="memory", version="1.0.0", description="Agent memory management", enabled=True),
        SkillInfo(name="planning", version="1.0.0", description="Task planning and decomposition", enabled=True),
        SkillInfo(name="learning", version="0.9.0", description="Experience-based learning", enabled=False)
    ],
    total=3
)
```

### MemoryGetRequest

Request model for retrieving memory.

**Fields:**

- `memory_type`: Type of memory ("short_term" or "long_term")

**Usage:**

```python
from apps.api.domain.skills.models import MemoryGetRequest

request = MemoryGetRequest(memory_type="short_term")
```

### MemorySetRequest

Request model for storing memory.

**Fields:**

- `memory_type`: Type of memory ("short_term" or "long_term")
- `data`: Memory data to store (arbitrary dict)

**Usage:**

```python
from apps.api.domain.skills.models import MemorySetRequest

request = MemorySetRequest(
    memory_type="long_term",
    data={
        "last_project_key": "PROJ-001",
        "known_templates": ["pmp", "raid", "blueprint"],
        "user_preferences": {"theme": "dark", "auto_save": True}
    }
)
```

### MemoryResponse

Response model for memory operations.

**Fields:**

- `success`: Whether operation succeeded
- `data`: Retrieved memory data (for GET operations)
- `message`: Human-readable status message
- `timestamp`: Operation timestamp (ISO format)

**Usage:**

```python
from apps.api.domain.skills.models import MemoryResponse

# Successful retrieval
response = MemoryResponse(
    success=True,
    data={"last_project_key": "PROJ-001"},
    message="Memory retrieved successfully",
    timestamp="2025-02-10T15:30:00Z"
)

# Failed operation
response = MemoryResponse(
    success=False,
    data=None,
    message="Memory type 'invalid' not supported",
    timestamp="2025-02-10T15:30:00Z"
)
```

## Cognitive Architecture

The Skills domain supports these cognitive capabilities:

### Memory

- **Short-term memory**: Conversation context, current task state
- **Long-term memory**: User preferences, project history, learned patterns

### Planning

- Task decomposition
- Dependency analysis
- Resource estimation

### Learning

- Experience logging
- Pattern recognition
- Skill improvement tracking

## Storage Model

Skills data is stored per agent:

```text
projectDocs/<PROJECT_KEY>/agents/<AGENT_ID>/
├── memory/
│   ├── short_term.json        # Ephemeral context
│   └── long_term.json         # Persistent preferences
├── learning/
│   └── experience.ndjson      # Learning history
└── plans/
    └── <plan_id>.json         # Task plans
```

## Usage

### Checking Available Skills

```python
from apps.api.domain.skills.models import SkillListResponse

# Service layer returns:
skills = SkillListResponse(
    skills=[
        SkillInfo(name="memory", version="1.0.0", description="Memory management", enabled=True),
        SkillInfo(name="planning", version="1.0.0", description="Task planning", enabled=True)
    ],
    total=2
)

for skill in skills.skills:
    print(f"{skill.name} v{skill.version}: {skill.description} (enabled={skill.enabled})")
```

### Using Memory Skill

```python
# Store memory
set_req = MemorySetRequest(
    memory_type="short_term",
    data={"current_task": "update_raid_register", "progress": 0.75}
)

# Retrieve memory
get_req = MemoryGetRequest(memory_type="short_term")
response = memory_service.get_memory(get_req)

if response.success:
    print(f"Current task: {response.data['current_task']}")
```

## Design Notes

- **SRP Compliance**: Skills domain focuses ONLY on skill interfaces, not implementation
- **Cognitive Architecture**: Supports agent memory, planning, and learning capabilities
- **Extensibility**: New skills can be added without changing core domain models
- **Memory Types**: Distinguish short-term (ephemeral) and long-term (persistent) memory
- **No Infrastructure Dependencies**: Pure domain models, storage handled by service layer
- **Agent-Centric**: Skills operate within agent context (per project, per agent)
