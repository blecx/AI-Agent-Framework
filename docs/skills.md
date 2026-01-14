# AI Agent Cognitive Skills

This document describes the AI Agent cognitive skills framework introduced in Phase 1, including memory, planning, and learning capabilities.

## Overview

The cognitive skills framework provides extensible AI agent capabilities through a plugin-based system. Skills are managed through a registry and can be enabled/disabled via environment variables or configuration.

### Core Components

1. **Skill Interface** - Base protocol defining skill contracts
2. **Skill Registry** - Manages skill lifecycle and availability
3. **Built-in Skills** - Memory, Planning, and Learning skills
4. **API Endpoints** - REST API for skill interactions

## Architecture

### Storage Layout

Agent data is stored under `PROJECT_DOCS_PATH/agents/{agent_id}/`:

```
PROJECT_DOCS_PATH/
└── agents/
    └── {agent_id}/
        ├── memory/
        │   ├── short_term.json
        │   └── long_term.json
        ├── plans/
        │   └── {plan_id}.json
        └── learning/
            └── experience.ndjson
```

### Agent Identity

- `agent_id` is a first-class identifier that scopes all agent data
- Agent storage is separate from project storage
- Multiple agents can operate independently with isolated data

## Built-in Skills

### 1. Memory Skill

**Purpose**: Manage short-term and long-term memory for agents.

**Storage**: `agents/{agent_id}/memory/`

**Operations**:
- `get` - Retrieve memory state
- `set` - Update memory state

**Memory Types**:
- `short_term` - Volatile, session-scoped data
- `long_term` - Persistent knowledge and facts

**Example**:
```python
# Set short-term memory
memory = {
    "current_task": "Implement feature X",
    "context": {
        "files_modified": ["file1.py", "file2.py"],
        "next_steps": ["test", "commit"]
    }
}
```

### 2. Planning Skill

**Purpose**: Generate multi-step plans for goal achievement.

**Storage**: `agents/{agent_id}/plans/{plan_id}.json`

**Features**:
- Deterministic algorithmic planner (MVP)
- Goal decomposition based on keywords
- Dependency tracking between steps
- Constraint awareness

**Plan Structure**:
```json
{
  "plan_id": "uuid",
  "goal": "Complete project deliverable",
  "constraints": ["Limited time", "Budget constraint"],
  "context": {"priority": "high"},
  "steps": [
    {
      "step": 1,
      "action": "analyze",
      "description": "Analyze requirements for: Complete project deliverable",
      "status": "pending",
      "dependencies": []
    },
    {
      "step": 2,
      "action": "design",
      "description": "Design solution architecture",
      "status": "pending",
      "dependencies": [1]
    }
  ],
  "created_at": "2026-01-14T20:00:00Z",
  "status": "pending"
}
```

### 3. Learning Skill

**Purpose**: Capture and learn from experience events.

**Storage**: `agents/{agent_id}/learning/experience.ndjson`

**Operations**:
- `log` - Log an experience event
- `summary` - Get summary of logged experiences

**Experience Format**:
```json
{
  "timestamp": "2026-01-14T20:00:00Z",
  "context": "Working on authentication feature",
  "action": "Implemented OAuth2",
  "outcome": "Successful authentication flow",
  "feedback": "Works well with the existing system",
  "tags": ["authentication", "oauth2"]
}
```

## API Usage

### Base URL

**Versioned (recommended)**: `/api/v1/agents/{agent_id}/skills`

**Deprecated**: `/agents/{agent_id}/skills`

### List Available Skills

```http
GET /api/v1/agents/{agent_id}/skills
```

**Response**:
```json
{
  "skills": [
    {
      "name": "memory",
      "version": "1.0.0",
      "description": "Manage agent short-term and long-term memory",
      "enabled": true
    },
    {
      "name": "planning",
      "version": "1.0.0",
      "description": "Generate and manage multi-step plans for goal achievement",
      "enabled": true
    },
    {
      "name": "learning",
      "version": "1.0.0",
      "description": "Capture and learn from experience events",
      "enabled": true
    }
  ],
  "total": 3
}
```

### Memory Operations

#### Get Memory

```http
GET /api/v1/agents/{agent_id}/skills/memory?memory_type=short_term
```

**Response**:
```json
{
  "success": true,
  "data": {
    "data": {"key": "value"},
    "timestamp": "2026-01-14T20:00:00Z",
    "updated_at": "2026-01-14T20:00:00Z"
  },
  "message": "short_term memory retrieved",
  "timestamp": "2026-01-14T20:00:00Z"
}
```

#### Set Memory

```http
POST /api/v1/agents/{agent_id}/skills/memory
Content-Type: application/json

{
  "memory_type": "short_term",
  "data": {
    "current_task": "Implement feature",
    "context": {"priority": "high"}
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "data": {"current_task": "Implement feature", "context": {"priority": "high"}},
    "timestamp": "2026-01-14T20:00:00Z",
    "updated_at": "2026-01-14T20:00:00Z"
  },
  "message": "short_term memory updated",
  "timestamp": "2026-01-14T20:00:00Z"
}
```

### Planning Operations

#### Create Plan

```http
POST /api/v1/agents/{agent_id}/skills/plan
Content-Type: application/json

{
  "goal": "Implement authentication feature",
  "constraints": ["Security requirements", "Time constraint"],
  "context": {"priority": "high", "tech_stack": "OAuth2"}
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "goal": "Implement authentication feature",
    "constraints": ["Security requirements", "Time constraint"],
    "context": {"priority": "high", "tech_stack": "OAuth2"},
    "steps": [
      {
        "step": 1,
        "action": "analyze",
        "description": "Analyze requirements for: Implement authentication feature",
        "status": "pending",
        "dependencies": []
      }
    ],
    "created_at": "2026-01-14T20:00:00Z",
    "status": "pending"
  },
  "message": "Plan generated with 5 steps",
  "timestamp": "2026-01-14T20:00:00Z",
  "metadata": {
    "plan_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Learning Operations

#### Log Experience

```http
POST /api/v1/agents/{agent_id}/skills/learn
Content-Type: application/json

{
  "context": "Working on authentication feature",
  "action": "Implemented JWT tokens",
  "outcome": "Authentication works correctly",
  "feedback": "Good approach, meets security requirements",
  "tags": ["authentication", "security", "jwt"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-01-14T20:00:00Z",
    "context": "Working on authentication feature",
    "action": "Implemented JWT tokens",
    "outcome": "Authentication works correctly",
    "feedback": "Good approach, meets security requirements",
    "tags": ["authentication", "security", "jwt"]
  },
  "message": "Experience logged successfully",
  "timestamp": "2026-01-14T20:00:00Z"
}
```

#### Get Learning Summary

```http
GET /api/v1/agents/{agent_id}/skills/learn/summary
```

**Response**:
```json
{
  "success": true,
  "data": {
    "total_experiences": 15,
    "tags": [
      {"tag": "authentication", "count": 5},
      {"tag": "security", "count": 3},
      {"tag": "testing", "count": 2}
    ],
    "recent_experiences": [
      {
        "timestamp": "2026-01-14T20:00:00Z",
        "context": "...",
        "action": "...",
        "outcome": "...",
        "tags": []
      }
    ]
  },
  "message": "Summary of 15 experiences",
  "timestamp": "2026-01-14T20:00:00Z"
}
```

## Extending the Framework

### Creating a Custom Skill

1. **Implement the Skill Protocol**:

```python
from apps.api.skills.base import SkillResult
from typing import Dict, Any

class CustomSkill:
    """Custom skill implementation."""
    
    name = "custom"
    version = "1.0.0"
    description = "Custom skill description"
    
    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        """Execute the skill."""
        # Your skill logic here
        return SkillResult(
            success=True,
            data={"result": "success"},
            message="Custom skill executed"
        )
```

2. **Register the Skill**:

```python
from apps.api.skills.registry import get_global_registry

# Get registry
registry = get_global_registry()

# Register skill
skill = CustomSkill()
registry.register(skill, enabled=True)
```

3. **Use Environment Variables** (optional):

```bash
export SKILL_CUSTOM_ENABLED=true
```

Then modify `apps/api/skills/registry.py` to check the environment variable during registration.

### Skill Interface

All skills must implement the `Skill` protocol:

```python
from typing import Protocol, Dict, Any
from apps.api.skills.base import SkillResult

class Skill(Protocol):
    """Protocol defining the interface for cognitive skills."""
    
    name: str  # Unique skill identifier
    version: str  # Semantic version
    description: str  # Human-readable description
    
    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        """
        Execute the skill with given parameters.
        
        Args:
            agent_id: Unique identifier for the agent
            params: Skill-specific parameters
            **kwargs: Additional context (e.g., docs_path, git_manager)
            
        Returns:
            SkillResult with execution outcome
        """
        ...
```

### SkillResult Structure

```python
class SkillResult(BaseModel):
    """Standardized skill execution result."""
    
    success: bool  # Whether execution succeeded
    data: Optional[Any] = None  # Result data
    message: str = ""  # Human-readable message
    timestamp: str  # ISO 8601 timestamp
    metadata: Dict[str, Any] = {}  # Additional metadata
```

## Configuration

### Environment Variables

- `SKILL_MEMORY_ENABLED` - Enable/disable memory skill (default: `true`)
- `SKILL_PLANNING_ENABLED` - Enable/disable planning skill (default: `true`)
- `SKILL_LEARNING_ENABLED` - Enable/disable learning skill (default: `true`)
- `PROJECT_DOCS_PATH` - Base path for document storage (default: `/projectDocs`)

### Registry Management

```python
from apps.api.skills.registry import get_global_registry

registry = get_global_registry()

# Enable/disable skills dynamically
registry.enable("memory")
registry.disable("planning")

# Check status
is_enabled = registry.is_enabled("learning")

# List all skills
all_skills = registry.list_all()
available_skills = registry.list_available()
```

## Testing

### Running Tests

```bash
# Unit tests
pytest tests/unit/test_skill_registry.py
pytest tests/unit/test_memory_skill.py
pytest tests/unit/test_planning_skill.py
pytest tests/unit/test_learning_skill.py

# Integration tests
pytest tests/integration/test_skills_api.py

# All skill tests
pytest tests/unit/test_*_skill*.py tests/integration/test_skills_api.py
```

### Test Coverage

- **Unit Tests**: 45 tests covering all skill logic
- **Integration Tests**: 14 tests covering API endpoints
- **Coverage**: >90% for skill modules

## Future Enhancements (Phase 2/3)

1. **LLM Integration**: Replace deterministic planner with LLM-based planning
2. **Advanced Memory**: Semantic search, memory consolidation, forgetting mechanisms
3. **Learning Analytics**: Pattern recognition, success rate tracking, recommendations
4. **Skill Composition**: Chain multiple skills together
5. **Skill Marketplace**: Community-contributed skills
6. **Skill Versioning**: Side-by-side skill versions
7. **Skill Dependencies**: Express dependencies between skills

## Troubleshooting

### Common Issues

**Issue**: Skill not available in API
- Check if skill is enabled: `GET /api/v1/agents/{agent_id}/skills`
- Verify environment variable: `SKILL_<NAME>_ENABLED=true`

**Issue**: Storage path errors
- Ensure `PROJECT_DOCS_PATH` is set correctly
- Verify directory permissions for writing

**Issue**: Invalid agent_id
- Agent IDs must be URL-safe
- Avoid special characters except `-` and `_`

## Support

For questions or issues:
1. Check API documentation at `/docs` endpoint
2. Review test examples in `tests/integration/test_skills_api.py`
3. Create an issue in the GitHub repository with label `skills`
