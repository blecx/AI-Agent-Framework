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
from .base import SkillMetadata


class MyCustomSkill:
    """Custom skill that does something useful."""
    
    def get_metadata(self) -> SkillMetadata:
        """Define skill metadata and schemas."""
        return SkillMetadata(
            name="my_custom_skill",
            version="1.0.0",
            description="Does something useful",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter"
                    },
                    "param2": {
                        "type": "number",
                        "description": "Second parameter"
                    }
                },
                "required": ["param1"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "string"},
                    "computed_value": {"type": "number"}
                }
            }
        )
    
    async def execute(
        self, agent_id: str, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the skill logic."""
        # Validate inputs
        param1 = input_data.get("param1")
        if not param1:
            raise ValueError("param1 is required")
        
        param2 = input_data.get("param2", 0)
        
        # Access services from context if needed
        git_manager = context.get("git_manager")
        llm_service = context.get("llm_service")
        
        # Implement your skill logic here
        result = f"Processed {param1}"
        computed_value = param2 * 2
        
        # Return structured results
        return {
            "result": result,
            "computed_value": computed_value
        }
```

## Step 2: Register the Skill

### Option A: Register in the Global Registry (Recommended for built-in skills)

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

### Option B: Register Dynamically (For contributor/plugin skills)

You can register skills at runtime:

```python
from skills.registry import get_registry
from skills.my_custom_skill import MyCustomSkill

registry = get_registry()
registry.register_skill(MyCustomSkill())
```

## Step 3: Add API Endpoints (Optional)

If you want dedicated API endpoints, add them to `apps/api/routers/skills.py`:

```python
@router.post("/{agent_id}/skills/my-custom", response_model=MyCustomResponse)
async def execute_my_custom_skill(
    agent_id: str, request: MyCustomRequest, app_request: Request
):
    """Execute my custom skill."""
    registry = get_registry()
    skill = registry.get_skill("my_custom_skill")
    
    if not skill:
        raise HTTPException(status_code=500, detail="Skill not available")
    
    git_manager = app_request.app.state.git_manager
    llm_service = app_request.app.state.llm_service
    
    try:
        result = await skill.execute(
            agent_id=agent_id,
            input_data=request.dict(),
            context={
                "git_manager": git_manager,
                "llm_service": llm_service
            }
        )
        return MyCustomResponse(**result)
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

- Use `git_manager.base_path` for file storage
- Create subdirectories: `_agents/{skill_name}/`
- Use JSON for structured data
- Use NDJSON for append-only logs

### Async Operations

- Skills must be async (use `async def execute`)
- Use `await` for async operations
- Don't block the event loop

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
        metadata = skill.get_metadata()
        assert metadata.name == "my_custom_skill"
        assert metadata.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_execute(self, skill):
        result = await skill.execute(
            agent_id="test",
            input_data={"param1": "test", "param2": 5},
            context={}
        )
        assert result["result"] == "Processed test"
        assert result["computed_value"] == 10
```

## Examples

### File I/O Skill

```python
import os
import json

class FileIOSkill:
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="file_io",
            version="1.0.0",
            description="Read and write agent files",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["read", "write"]},
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["operation", "filename"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "content": {"type": "string"}
                }
            }
        )
    
    async def execute(self, agent_id: str, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        git_manager = context.get("git_manager")
        if not git_manager:
            raise ValueError("git_manager required")
        
        operation = input_data["operation"]
        filename = input_data["filename"]
        
        agent_dir = os.path.join(str(git_manager.base_path), "_agents", agent_id)
        os.makedirs(agent_dir, exist_ok=True)
        filepath = os.path.join(agent_dir, filename)
        
        if operation == "read":
            if not os.path.exists(filepath):
                return {"success": False, "content": ""}
            with open(filepath, 'r') as f:
                content = f.read()
            return {"success": True, "content": content}
        else:  # write
            content = input_data.get("content", "")
            with open(filepath, 'w') as f:
                f.write(content)
            return {"success": True, "content": content}
```

### LLM Integration Skill

```python
class ReasoningSkill:
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="reasoning",
            version="1.0.0",
            description="Use LLM for reasoning tasks",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "context": {"type": "object"}
                },
                "required": ["prompt"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "response": {"type": "string"},
                    "reasoning": {"type": "string"}
                }
            }
        )
    
    async def execute(self, agent_id: str, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        llm_service = context.get("llm_service")
        if not llm_service:
            return {"response": "LLM not available", "reasoning": "Fallback response"}
        
        prompt = input_data["prompt"]
        
        try:
            response = await llm_service.chat_completion(
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "response": response.get("content", ""),
                "reasoning": "LLM-generated response"
            }
        except Exception:
            return {"response": "Error", "reasoning": "LLM call failed"}
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
