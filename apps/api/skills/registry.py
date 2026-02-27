"""
Skill registry for managing and configuring cognitive skills.
"""

from typing import Dict, List, Optional
from .base import Skill
import os


class SkillRegistry:
    """Registry for managing cognitive skills with enable/disable support."""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._enabled_skills: set = set()

    def register(self, skill: Skill, enabled: bool = True) -> None:
        """
        Register a skill in the registry.

        Args:
            skill: The skill instance to register
            enabled: Whether the skill is enabled by default
        """
        self._skills[skill.name] = skill
        if enabled:
            self._enabled_skills.add(skill.name)

    def unregister(self, skill_name: str) -> None:
        """
        Unregister a skill from the registry.

        Args:
            skill_name: Name of the skill to unregister
        """
        if skill_name in self._skills:
            del self._skills[skill_name]
            self._enabled_skills.discard(skill_name)

    def get(self, skill_name: str) -> Optional[Skill]:
        """
        Get a skill by name.

        Args:
            skill_name: Name of the skill

        Returns:
            Skill instance if found and enabled, None otherwise
        """
        if skill_name in self._enabled_skills:
            return self._skills.get(skill_name)
        return None

    def list_available(self) -> List[Dict[str, str]]:
        """
        List all available (enabled) skills.

        Returns:
            List of skill metadata dictionaries
        """
        return [
            {
                "name": skill.name,
                "version": skill.version,
                "description": skill.description,
                "enabled": skill.name in self._enabled_skills,
            }
            for skill in self._skills.values()
            if skill.name in self._enabled_skills
        ]

    def list_all(self) -> List[Dict[str, str]]:
        """
        List all registered skills regardless of enabled status.

        Returns:
            List of skill metadata dictionaries
        """
        return [
            {
                "name": skill.name,
                "version": skill.version,
                "description": skill.description,
                "enabled": skill.name in self._enabled_skills,
            }
            for skill in self._skills.values()
        ]

    def enable(self, skill_name: str) -> bool:
        """
        Enable a skill.

        Args:
            skill_name: Name of the skill to enable

        Returns:
            True if enabled successfully, False if skill not found
        """
        if skill_name in self._skills:
            self._enabled_skills.add(skill_name)
            return True
        return False

    def disable(self, skill_name: str) -> bool:
        """
        Disable a skill.

        Args:
            skill_name: Name of the skill to disable

        Returns:
            True if disabled successfully, False if skill not found
        """
        if skill_name in self._skills:
            self._enabled_skills.discard(skill_name)
            return True
        return False

    def is_enabled(self, skill_name: str) -> bool:
        """
        Check if a skill is enabled.

        Args:
            skill_name: Name of the skill

        Returns:
            True if skill exists and is enabled
        """
        return skill_name in self._enabled_skills


# Global skill registry instance
_global_registry: Optional[SkillRegistry] = None


def get_global_registry() -> SkillRegistry:
    """
    Get the global skill registry instance.

    Returns:
        Global SkillRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = SkillRegistry()
        _register_builtin_skills(_global_registry)
    return _global_registry


def _register_builtin_skills(registry: SkillRegistry) -> None:
    """
    Register built-in skills in the registry.

    Args:
        registry: SkillRegistry to register skills in
    """
    from .memory_skill import MemorySkill
    from .planning_skill import PlanningSkill
    from .learning_skill import LearningSkill
    from .design_guidelines_skill import DesignGuidelinesSkill
    from .coder_change_plan_skill import CoderChangePlanSkill

    # Check environment variables for skill enablement
    memory_enabled = os.getenv("SKILL_MEMORY_ENABLED", "true").lower() == "true"
    planning_enabled = os.getenv("SKILL_PLANNING_ENABLED", "true").lower() == "true"
    learning_enabled = os.getenv("SKILL_LEARNING_ENABLED", "true").lower() == "true"

    design_guidelines_enabled = (
        os.getenv("SKILL_DESIGN_GUIDELINES_ENABLED", "true").lower() == "true"
    )
    coder_change_plan_enabled = (
        os.getenv("SKILL_CODER_CHANGE_PLAN_ENABLED", "true").lower() == "true"
    )

    # Register built-in skills
    registry.register(MemorySkill(), enabled=memory_enabled)
    registry.register(PlanningSkill(), enabled=planning_enabled)
    registry.register(LearningSkill(), enabled=learning_enabled)
    registry.register(DesignGuidelinesSkill(), enabled=design_guidelines_enabled)
    registry.register(CoderChangePlanSkill(), enabled=coder_change_plan_enabled)
