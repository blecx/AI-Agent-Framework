"""
Skill registry for managing and loading AI agent skills.
"""

from typing import Dict, List, Optional
from .base import Skill, SkillMetadata


class SkillRegistry:
    """
    Registry for managing available skills.
    
    Provides a central location for registering, loading, and accessing
    skills. Supports both built-in skills and custom contributor skills.
    """

    def __init__(self):
        """Initialize empty skill registry."""
        self._skills: Dict[str, Skill] = {}

    def register_skill(self, skill: Skill) -> None:
        """
        Register a skill in the registry.
        
        Args:
            skill: Skill instance to register
            
        Raises:
            ValueError: If a skill with the same name is already registered
        """
        metadata = skill.get_metadata()
        if metadata.name in self._skills:
            raise ValueError(
                f"Skill '{metadata.name}' is already registered"
            )
        self._skills[metadata.name] = skill

    def get_skill(self, name: str) -> Optional[Skill]:
        """
        Get a skill by name.
        
        Args:
            name: Name of the skill to retrieve
            
        Returns:
            Skill instance if found, None otherwise
        """
        return self._skills.get(name)

    def list_skills(self) -> List[SkillMetadata]:
        """
        List all registered skills.
        
        Returns:
            List of metadata for all registered skills
        """
        return [skill.get_metadata() for skill in self._skills.values()]

    def has_skill(self, name: str) -> bool:
        """
        Check if a skill is registered.
        
        Args:
            name: Name of the skill to check
            
        Returns:
            True if skill is registered, False otherwise
        """
        return name in self._skills

    def load_builtin_skills(self) -> None:
        """
        Load all built-in skills.
        
        This method imports and registers the core skills provided
        by the framework (memory, planning, learning).
        """
        from .memory_skill import MemorySkill
        from .planning_skill import PlanningSkill
        from .learning_skill import LearningSkill

        self.register_skill(MemorySkill())
        self.register_skill(PlanningSkill())
        self.register_skill(LearningSkill())


# Global registry instance
_global_registry: Optional[SkillRegistry] = None


def get_registry() -> SkillRegistry:
    """
    Get the global skill registry instance.
    
    Creates and initializes the registry on first call.
    
    Returns:
        Global SkillRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = SkillRegistry()
        _global_registry.load_builtin_skills()
    return _global_registry
