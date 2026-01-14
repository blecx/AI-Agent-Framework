"""
Unit tests for Skill Registry.
"""
from apps.api.skills.registry import SkillRegistry
from apps.api.skills.base import SkillResult
from typing import Dict, Any


class MockSkill:
    """Mock skill for testing."""

    def __init__(self, name: str = "test_skill"):
        self.name = name
        self.version = "1.0.0"
        self.description = "Test skill"

    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        """
        Execute the mock skill.

        Args:
            agent_id: Agent identifier
            params: Skill parameters
            **kwargs: Additional context

        Returns:
            SkillResult with test execution
        """
        return SkillResult(success=True, message="Test execution")


class TestSkillRegistry:
    """Test SkillRegistry functionality."""

    def test_register_skill(self):
        """Test registering a skill."""
        registry = SkillRegistry()
        skill = MockSkill("test1")
        registry.register(skill, enabled=True)

        assert skill.name in registry._skills
        assert skill.name in registry._enabled_skills

    def test_register_disabled_skill(self):
        """Test registering a disabled skill."""
        registry = SkillRegistry()
        skill = MockSkill("test2")
        registry.register(skill, enabled=False)

        assert skill.name in registry._skills
        assert skill.name not in registry._enabled_skills

    def test_unregister_skill(self):
        """Test unregistering a skill."""
        registry = SkillRegistry()
        skill = MockSkill("test3")
        registry.register(skill)
        registry.unregister(skill.name)

        assert skill.name not in registry._skills
        assert skill.name not in registry._enabled_skills

    def test_get_enabled_skill(self):
        """Test getting an enabled skill."""
        registry = SkillRegistry()
        skill = MockSkill("test4")
        registry.register(skill, enabled=True)

        retrieved = registry.get(skill.name)
        assert retrieved is not None
        assert retrieved.name == skill.name

    def test_get_disabled_skill(self):
        """Test getting a disabled skill returns None."""
        registry = SkillRegistry()
        skill = MockSkill("test5")
        registry.register(skill, enabled=False)

        retrieved = registry.get(skill.name)
        assert retrieved is None

    def test_list_available(self):
        """Test listing available skills."""
        registry = SkillRegistry()
        skill1 = MockSkill("test6")
        skill2 = MockSkill("test7")
        registry.register(skill1, enabled=True)
        registry.register(skill2, enabled=False)

        available = registry.list_available()
        assert len(available) == 1
        assert available[0]["name"] == "test6"
        assert available[0]["enabled"] is True

    def test_list_all(self):
        """Test listing all skills."""
        registry = SkillRegistry()
        skill1 = MockSkill("test8")
        skill2 = MockSkill("test9")
        registry.register(skill1, enabled=True)
        registry.register(skill2, enabled=False)

        all_skills = registry.list_all()
        assert len(all_skills) == 2
        names = {s["name"] for s in all_skills}
        assert "test8" in names
        assert "test9" in names

    def test_enable_skill(self):
        """Test enabling a skill."""
        registry = SkillRegistry()
        skill = MockSkill("test10")
        registry.register(skill, enabled=False)

        result = registry.enable(skill.name)
        assert result is True
        assert registry.is_enabled(skill.name)

    def test_enable_nonexistent_skill(self):
        """Test enabling a non-existent skill."""
        registry = SkillRegistry()
        result = registry.enable("nonexistent")
        assert result is False

    def test_disable_skill(self):
        """Test disabling a skill."""
        registry = SkillRegistry()
        skill = MockSkill("test11")
        registry.register(skill, enabled=True)

        result = registry.disable(skill.name)
        assert result is True
        assert not registry.is_enabled(skill.name)

    def test_disable_nonexistent_skill(self):
        """Test disabling a non-existent skill."""
        registry = SkillRegistry()
        result = registry.disable("nonexistent")
        assert result is False

    def test_is_enabled(self):
        """Test checking if a skill is enabled."""
        registry = SkillRegistry()
        skill = MockSkill("test12")
        registry.register(skill, enabled=True)

        assert registry.is_enabled(skill.name)

    def test_is_enabled_false(self):
        """Test checking if a disabled skill is enabled."""
        registry = SkillRegistry()
        skill = MockSkill("test13")
        registry.register(skill, enabled=False)

        assert not registry.is_enabled(skill.name)

    def test_is_enabled_nonexistent(self):
        """Test checking if a non-existent skill is enabled."""
        registry = SkillRegistry()
        assert not registry.is_enabled("nonexistent")
