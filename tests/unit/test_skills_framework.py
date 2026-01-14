"""
Unit tests for Skills Framework.
"""
import pytest
from apps.api.skills.base import SkillMetadata
from apps.api.skills.registry import SkillRegistry


class MockSkill:
    """Mock skill for testing."""
    
    def __init__(self, name="mock_skill", version="1.0.0"):
        self.name = name
        self.version = version
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name=self.name,
            version=self.version,
            description="Mock skill for testing",
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
    
    async def execute(self, agent_id: str, input_data: dict, context: dict) -> dict:
        return {"result": "success", "agent_id": agent_id}


class TestSkillRegistry:
    """Test skill registry functionality."""

    def test_register_skill(self):
        """Test registering a skill."""
        registry = SkillRegistry()
        skill = MockSkill("test_skill")
        
        registry.register_skill(skill)
        
        assert registry.has_skill("test_skill")
        retrieved = registry.get_skill("test_skill")
        assert retrieved is not None
        assert retrieved.get_metadata().name == "test_skill"

    def test_register_duplicate_skill_raises_error(self):
        """Test that registering duplicate skill raises error."""
        registry = SkillRegistry()
        skill1 = MockSkill("duplicate")
        skill2 = MockSkill("duplicate")
        
        registry.register_skill(skill1)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register_skill(skill2)

    def test_get_nonexistent_skill_returns_none(self):
        """Test getting a skill that doesn't exist returns None."""
        registry = SkillRegistry()
        
        result = registry.get_skill("nonexistent")
        
        assert result is None

    def test_list_skills(self):
        """Test listing all registered skills."""
        registry = SkillRegistry()
        skill1 = MockSkill("skill1")
        skill2 = MockSkill("skill2")
        
        registry.register_skill(skill1)
        registry.register_skill(skill2)
        
        skills = registry.list_skills()
        
        assert len(skills) == 2
        skill_names = {s.name for s in skills}
        assert skill_names == {"skill1", "skill2"}

    def test_has_skill(self):
        """Test checking if skill exists."""
        registry = SkillRegistry()
        skill = MockSkill("test")
        
        assert not registry.has_skill("test")
        
        registry.register_skill(skill)
        
        assert registry.has_skill("test")

    def test_load_builtin_skills(self):
        """Test loading built-in skills."""
        registry = SkillRegistry()
        registry.load_builtin_skills()
        
        # Check that core skills are registered
        assert registry.has_skill("memory")
        assert registry.has_skill("planning")
        assert registry.has_skill("learning")
        
        # Verify metadata
        memory_skill = registry.get_skill("memory")
        assert memory_skill is not None
        metadata = memory_skill.get_metadata()
        assert metadata.name == "memory"
        assert metadata.version == "1.0.0"


class TestSkillMetadata:
    """Test skill metadata model."""

    def test_skill_metadata_creation(self):
        """Test creating skill metadata."""
        metadata = SkillMetadata(
            name="test_skill",
            version="1.0.0",
            description="Test description",
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object", "properties": {}}
        )
        
        assert metadata.name == "test_skill"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test description"
        assert metadata.input_schema["type"] == "object"
        assert metadata.output_schema["type"] == "object"

    def test_skill_metadata_validation(self):
        """Test that metadata requires all fields."""
        with pytest.raises(Exception):  # Pydantic validation error
            SkillMetadata(name="test")  # Missing required fields
