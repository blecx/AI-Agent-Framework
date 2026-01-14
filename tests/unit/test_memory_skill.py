"""
Unit tests for Memory Skill.
"""
import pytest
import tempfile
import shutil
import json
import os
from apps.api.skills.memory_skill import MemorySkill
from apps.api.services.git_manager import GitManager


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def git_manager(temp_project_dir):
    """Create a GitManager instance with temporary directory."""
    manager = GitManager(temp_project_dir)
    manager.ensure_repository()
    return manager


@pytest.fixture
def memory_skill():
    """Create a MemorySkill instance."""
    return MemorySkill()


class TestMemorySkillMetadata:
    """Test memory skill metadata."""

    def test_get_metadata(self, memory_skill):
        """Test getting memory skill metadata."""
        metadata = memory_skill.get_metadata()
        
        assert metadata.name == "memory"
        assert metadata.version == "1.0.0"
        assert "memory" in metadata.description.lower()
        assert "operation" in metadata.input_schema["properties"]
        assert metadata.output_schema["type"] == "object"


@pytest.mark.asyncio
class TestMemorySkillExecution:
    """Test memory skill execution."""

    async def test_get_empty_memory(self, memory_skill, git_manager):
        """Test getting memory when none exists."""
        result = await memory_skill.execute(
            agent_id="test_agent",
            input_data={"operation": "get"},
            context={"git_manager": git_manager}
        )
        
        assert result["agent_id"] == "test_agent"
        assert result["short_term"] == {}
        assert result["long_term"] == {}
        assert "metadata" in result
        assert "created_at" in result["metadata"]

    async def test_set_memory(self, memory_skill, git_manager):
        """Test setting memory."""
        short_term = {"working": "data", "count": 42}
        long_term = {"fact": "important", "learned": True}
        
        result = await memory_skill.execute(
            agent_id="test_agent",
            input_data={
                "operation": "set",
                "short_term": short_term,
                "long_term": long_term
            },
            context={"git_manager": git_manager}
        )
        
        assert result["agent_id"] == "test_agent"
        assert result["short_term"] == short_term
        assert result["long_term"] == long_term
        assert "updated_at" in result["metadata"]

    async def test_memory_persistence(self, memory_skill, git_manager):
        """Test that memory persists across operations."""
        agent_id = "persist_test"
        
        # Set initial memory
        await memory_skill.execute(
            agent_id=agent_id,
            input_data={
                "operation": "set",
                "short_term": {"key1": "value1"},
                "long_term": {"fact1": "data1"}
            },
            context={"git_manager": git_manager}
        )
        
        # Get memory to verify persistence
        result = await memory_skill.execute(
            agent_id=agent_id,
            input_data={"operation": "get"},
            context={"git_manager": git_manager}
        )
        
        assert result["short_term"]["key1"] == "value1"
        assert result["long_term"]["fact1"] == "data1"

    async def test_memory_merge(self, memory_skill, git_manager):
        """Test that memory updates merge with existing data."""
        agent_id = "merge_test"
        
        # Set initial memory
        await memory_skill.execute(
            agent_id=agent_id,
            input_data={
                "operation": "set",
                "short_term": {"key1": "value1", "key2": "value2"}
            },
            context={"git_manager": git_manager}
        )
        
        # Update with partial data
        result = await memory_skill.execute(
            agent_id=agent_id,
            input_data={
                "operation": "set",
                "short_term": {"key2": "updated", "key3": "new"}
            },
            context={"git_manager": git_manager}
        )
        
        assert result["short_term"]["key1"] == "value1"  # Preserved
        assert result["short_term"]["key2"] == "updated"  # Updated
        assert result["short_term"]["key3"] == "new"  # Added

    async def test_invalid_operation_raises_error(self, memory_skill, git_manager):
        """Test that invalid operation raises error."""
        with pytest.raises(ValueError, match="Invalid operation"):
            await memory_skill.execute(
                agent_id="test",
                input_data={"operation": "invalid"},
                context={"git_manager": git_manager}
            )

    async def test_missing_git_manager_raises_error(self, memory_skill):
        """Test that missing git_manager raises error."""
        with pytest.raises(ValueError, match="git_manager required"):
            await memory_skill.execute(
                agent_id="test",
                input_data={"operation": "get"},
                context={}
            )

    async def test_memory_file_location(self, memory_skill, git_manager):
        """Test that memory is stored in correct location."""
        agent_id = "location_test"
        
        await memory_skill.execute(
            agent_id=agent_id,
            input_data={
                "operation": "set",
                "short_term": {"test": "data"}
            },
            context={"git_manager": git_manager}
        )
        
        # Verify file exists
        memory_file = os.path.join(
            str(git_manager.base_path), "_agents", "memory", f"{agent_id}.json"
        )
        assert os.path.exists(memory_file)
        
        # Verify content
        with open(memory_file, 'r') as f:
            data = json.load(f)
        
        assert data["agent_id"] == agent_id
        assert data["short_term"]["test"] == "data"
