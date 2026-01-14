# AI Agent Cognitive Skills System

## Overview

The AI Agent Framework includes an extensible skills system that provides cognitive capabilities to AI agents. Skills are modular, reusable components that agents can execute to perform specific tasks.

## Core Concepts

### What is a Skill?

A skill is a discrete capability that an agent can execute. Each skill:
- Has a unique name and version
- Defines input and output schemas
- Can be executed with validated inputs
- Returns structured results

### Built-in Skills

The framework includes three foundational cognitive skills:

1. **Memory Skill** - Manages agent memory (short-term and long-term)
2. **Planning Skill** - Generates multi-step plans for goals
3. **Learning Skill** - Records experiences for learning and improvement

## Skill Architecture

### Skill Protocol

All skills implement the `Skill` protocol defined in `apps/api/skills/base.py`:

```python
from typing import Protocol, Any, Dict

class Skill(Protocol):
    # Class-level metadata
    name: str
    version: str
    description: str
    
    def execute(
        self, agent_id: str, params: Dict[str, Any], **kwargs
    ) -> SkillResult:
        """Execute the skill with given parameters."""
        ...
```

### Skill Registry

The `SkillRegistry` manages all available skills:
- Loads built-in skills automatically
- Supports custom skill registration
- Provides skill discovery and lookup
- Ensures skill name uniqueness

### Execution Context

Skills receive kwargs with services:
- `docs_path`: Base path for document storage
- `git_manager`: For git operations (optional)
- `llm_service`: For LLM interactions (optional)

## Built-in Skills Reference

### Memory Skill

**Purpose**: Manage agent short-term and long-term memory.

**Input Parameters**:
```json
{
  "operation": "get" | "set",
  "memory_type": "short_term" | "long_term",
  "data": {...}  // Required for set operation
}
```

**Output Format**:
```json
{
  "success": true,
  "data": {
    "agent_id": "string",
    "short_term": {...},
    "long_term": {...},
    "metadata": {
      "created_at": "ISO timestamp",
      "updated_at": "ISO timestamp"
    }
  },
  "message": "string",
  "timestamp": "ISO timestamp"
}
```

**Storage**: Memory is persisted in `agents/{agent_id}/memory/short_term.json` and `agents/{agent_id}/memory/long_term.json`

**Use Cases**:
- Maintain working memory during task execution
- Store learned facts and knowledge long-term
- Share state across agent interactions

### Planning Skill

**Purpose**: Generate structured multi-step plans from goals.

**Input Schema**:
```json
{
  "goal": "string (required)",
  "constraints": ["string", ...],  // Optional
  "context": {...}                  // Optional
}
```

**Output Schema**:
```json
{
  "agent_id": "string",
  "goal": "string",
  "steps": [
    {
      "step_number": 1,
      "title": "string",
      "description": "string",
      "estimated_duration": "1h 30m",
      "dependencies": [previous_step_numbers],
      "status": "pending" | "in_progress" | "completed"
    }
  ],
  "estimated_total_duration": "4h",
  "created_at": "ISO timestamp"
}
```

**Algorithm**: Phase 1 uses deterministic decomposition. Future versions will integrate LLM-based planning.

**Use Cases**:
- Break down complex goals into actionable steps
- Estimate effort and dependencies
- Track execution progress

### Learning Skill

**Purpose**: Record agent experiences for learning and improvement.

**Input Schema**:
```json
{
  "experience": {
    "input": {...},           // Required: what led to the experience
    "outcome": {...},          // Required: what happened
    "feedback": "string",      // Optional: evaluation
    "context": {...}           // Optional: additional context
  }
}
```

**Output Schema**:
```json
{
  "agent_id": "string",
  "experience_id": "UUID",
  "recorded_at": "ISO timestamp",
  "message": "Experience recorded successfully"
}
```

**Storage**: Experiences are appended to `agents/{agent_id}/learning/experience.ndjson` in NDJSON format.

**Use Cases**:
- Build experience database for pattern recognition
- Track what works and what doesn't
- Enable experience-based decision making

## API Usage

See [Skills API Documentation](../api/skills-api.md) for endpoint details and examples.

## Extending with Custom Skills

See [Extending Skills Guide](extending-skills.md) to learn how to create custom skills.

## Design Principles

1. **Modularity**: Skills are independent, self-contained modules
2. **Extensibility**: New skills can be added without modifying core code
3. **Type Safety**: Pydantic models ensure input/output validation
4. **Persistence**: Skills can persist state using the git-backed storage
5. **Testability**: Skills are easy to unit test in isolation

## Future Enhancements

- LLM-enhanced planning with reasoning
- Memory retrieval and search capabilities
- Learning analytics and pattern recognition
- Skill composition and chaining
- Custom skill hot-loading from configuration
