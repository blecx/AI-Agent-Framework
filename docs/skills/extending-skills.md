# Extending Skills: Creating Custom Agent Skills

This guide explains how to create custom skills for the AI Agent Framework.

## Quick Start

Creating a custom skill involves three steps:

1. Implement the `Skill` protocol
2. Register the skill in the registry
3. (Optional) Add API endpoints

## Step 1: Implement a Custom Skill

Create a new file in `apps/api/skills/` (e.g., `my_custom_skill.py`):

```python
"""
My custom skill implementation.
"""

from typing import Dict, Any
from .base import SkillResult


class MyCustomSkill:
    """Custom skill that does something useful."""
    
    # Required skill metadata (class attributes)
    name: str = "my_custom_skill"
    version: str = "1.0.0"
    description: str = "Does something useful"
    
    def execute(
        self, agent_id: str, params: Dict[str, Any], **kwargs
    ) -> SkillResult:
        """Execute the skill logic."""
        # Validate inputs
        param1 = params.get("param1")
        if not param1:
            raise ValueError("param1 is required")
        
        param2 = params.get("param2", 0)
        
        # Access services from kwargs if needed
        docs_path = kwargs.get("docs_path")
        git_manager = kwargs.get("git_manager")
        llm_service = kwargs.get("llm_service")
        
        # Implement your skill logic here
        result = f"Processed {param1}"
        computed_value = param2 * 2
        
        # Return structured results
        return SkillResult(
            success=True,
            data={
                "result": result,
                "computed_value": computed_value
            },
            message="Skill executed successfully"
        )
```

## Step 2: Register the Skill

### Option A: For Core Framework Skills Only

**Note**: This option is for skills that will be part of the core framework. For custom/third-party skills, use Option B.

Edit `apps/api/skills/registry.py` and add your skill to `load_builtin_skills()`:

```python
def load_builtin_skills(self) -> None:
    """Load all built-in skills."""
    from .memory_skill import MemorySkill
    from .planning_skill import PlanningSkill
    from .learning_skill import LearningSkill
    from .my_custom_skill import MyCustomSkill  # Add this
    
    self.register_skill(MemorySkill())
    self.register_skill(PlanningSkill())
    self.register_skill(LearningSkill())
    self.register_skill(MyCustomSkill())  # Add this
```

### Option B: Dynamic Registration (Recommended for Custom Skills)

For custom or third-party skills, register them dynamically at application startup or runtime:

```python
from apps.api.skills.registry import get_global_registry
from apps.api.skills.my_custom_skill import MyCustomSkill

registry = get_global_registry()
registry.register(MyCustomSkill())
```

You can create a custom initialization file or plugin loader:

```python
from fastapi import FastAPI
from apps.api.skills.registry import get_global_registry
from apps.api.skills.my_custom_skill import MyCustomSkill

app = FastAPI()

@app.on_event("startup")
async def load_custom_skills() -> None:
    registry = get_global_registry()
    registry.register(MyCustomSkill())
```

## Step 3: Add API Endpoints (Optional)

If you want dedicated API endpoints, add them to `apps/api/routers/skills.py`:

```python
@router.post("/{agent_id}/skills/my-custom", response_model=MyCustomResponse)
async def execute_my_custom_skill(
    agent_id: str, request: MyCustomRequest, app_request: Request
):
    """Execute my custom skill."""
    registry = get_global_registry()
    skill = registry.get("my_custom_skill")
    
    if not skill:
        raise HTTPException(status_code=500, detail="Skill not available")
    
    docs_path = get_docs_path(app_request)
    
    try:
        result = skill.execute(
            agent_id=agent_id,
            params=request.dict(),
            docs_path=docs_path
        )
        return MyCustomResponse(**result.data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

Don't forget to add request/response models to `apps/api/models.py`.

## Best Practices

### Input Validation

- Define clear JSON schemas in metadata
- Validate required parameters early
- Provide helpful error messages
- Use Pydantic models for complex inputs

### Error Handling

- Raise `ValueError` for invalid inputs
- Raise other exceptions for unexpected errors
- Include context in error messages

### State Management

- Use `docs_path` from kwargs for file storage
- Create subdirectories: `agents/{skill_name}/`
- Use JSON for structured data
- Use NDJSON for append-only logs

### Synchronous Execution

- Skills use synchronous `execute()` methods
- Return `SkillResult` objects
- Use standard Python file I/O and operations

### Testing

Create unit tests in `tests/unit/test_my_custom_skill.py`:

```python
import pytest
from apps.api.skills.my_custom_skill import MyCustomSkill


@pytest.fixture
def skill():
    return MyCustomSkill()


class TestMyCustomSkill:
    def test_metadata(self, skill):
        assert skill.name == "my_custom_skill"
        assert skill.version == "1.0.0"
        assert skill.description == "Does something useful"
    
    def test_execute(self, skill):
        result = skill.execute(
            agent_id="test",
            params={"param1": "test", "param2": 5}
        )
        assert result.success is True
        assert result.data["result"] == "Processed test"
        assert result.data["computed_value"] == 10
```

## Examples

### File I/O Skill

```python
import os
import json
from .base import SkillResult

class FileIOSkill:
    name = "file_io"
    version = "1.0.0"
    description = "Read and write agent files"
    
    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        docs_path = kwargs.get("docs_path")
        if not docs_path:
            return SkillResult(success=False, message="docs_path required")
        
        operation = params.get("operation")
        filename = params.get("filename")
        
        if not operation or not filename:
            return SkillResult(success=False, message="operation and filename required")
        
        agent_dir = os.path.join(docs_path, "agents", agent_id)
        os.makedirs(agent_dir, exist_ok=True)
        filepath = os.path.join(agent_dir, filename)
        
        if operation == "read":
            if not os.path.exists(filepath):
                return SkillResult(success=False, data={"content": ""})
            with open(filepath, 'r') as f:
                content = f.read()
            return SkillResult(success=True, data={"content": content})
        elif operation == "write":
            content = params.get("content", "")
            with open(filepath, 'w') as f:
                f.write(content)
            return SkillResult(success=True, data={"content": content}, message="File written successfully")
        else:
            return SkillResult(success=False, message=f"Invalid operation: {operation}")
```

### LLM Integration Skill

```python
from .base import SkillResult

class ReasoningSkill:
    name = "reasoning"
    version = "1.0.0"
    description = "Use LLM for reasoning tasks"
    
    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        llm_service = kwargs.get("llm_service")
        if not llm_service:
            return SkillResult(
                success=False, 
                message="LLM service not available",
                data={"response": "Fallback response"}
            )
        
        prompt = params.get("prompt")
        if not prompt:
            return SkillResult(success=False, message="prompt is required")
        
        try:
            response = llm_service.chat_completion(
                messages=[{"role": "user", "content": prompt}]
            )
            return SkillResult(
                success=True,
                data={
                    "response": response.get("content", ""),
                    "reasoning": "LLM-generated response"
                }
            )
        except Exception as e:
            return SkillResult(
                success=False,
                message=f"LLM call failed: {str(e)}",
                data={"response": "Error"}
            )
```

## Configuration

Future versions will support configuration-based skill loading:

```yaml
# config/skills.yml
custom_skills:
  - name: my_custom_skill
    module: skills.my_custom_skill
    class: MyCustomSkill
    enabled: true
```

## Troubleshooting

### Skill not registered

- Check that `load_builtin_skills()` includes your skill
- Verify the skill class is imported correctly
- Ensure no duplicate skill names

### Schema validation errors

- Double-check JSON schema syntax
- Test schemas with example inputs
- Use online JSON schema validators

### Import errors

- Verify file location in `apps/api/skills/`
- Check for circular imports
- Ensure all dependencies are installed

## Resources

- [Skills API Documentation](../api/skills-api.md)
- [Skills System Overview](README.md)
- [JSON Schema Documentation](https://json-schema.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
