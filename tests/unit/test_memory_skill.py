"""
Unit tests for Memory Skill.
"""
import pytest
import tempfile
import shutil
import os
from apps.api.skills.memory_skill import MemorySkill


@pytest.fixture
def temp_docs_path():
    """Create a temporary docs directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestMemorySkill:
    """Test MemorySkill functionality."""

    def test_skill_metadata(self):
        """Test skill metadata."""
        skill = MemorySkill()
        assert skill.name == "memory"
        assert skill.version == "1.0.0"
        assert skill.description

    def test_set_short_term_memory(self, temp_docs_path):
        """Test setting short-term memory."""
        skill = MemorySkill()
        agent_id = "agent001"
        test_data = {"key": "value", "number": 42}

        result = skill.execute(
            agent_id,
            {
                "operation": "set",
                "memory_type": "short_term",
                "data": test_data,
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        assert result.data["data"] == test_data
        assert "timestamp" in result.data

        # Verify file was created
        memory_file = os.path.join(
            temp_docs_path, "agents", agent_id, "memory", "short_term.json"
        )
        assert os.path.exists(memory_file)

    def test_set_long_term_memory(self, temp_docs_path):
        """Test setting long-term memory."""
        skill = MemorySkill()
        agent_id = "agent002"
        test_data = {"knowledge": "important fact"}

        result = skill.execute(
            agent_id,
            {
                "operation": "set",
                "memory_type": "long_term",
                "data": test_data,
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        assert result.data["data"] == test_data

        # Verify file was created
        memory_file = os.path.join(
            temp_docs_path, "agents", agent_id, "memory", "long_term.json"
        )
        assert os.path.exists(memory_file)

    def test_get_nonexistent_memory(self, temp_docs_path):
        """Test getting memory that doesn't exist."""
        skill = MemorySkill()
        agent_id = "agent003"

        result = skill.execute(
            agent_id,
            {
                "operation": "get",
                "memory_type": "short_term",
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        assert result.data == {}

    def test_get_existing_memory(self, temp_docs_path):
        """Test getting existing memory."""
        skill = MemorySkill()
        agent_id = "agent004"
        test_data = {"stored": "data"}

        # First set memory
        skill.execute(
            agent_id,
            {
                "operation": "set",
                "memory_type": "short_term",
                "data": test_data,
            },
            docs_path=temp_docs_path,
        )

        # Then get it
        result = skill.execute(
            agent_id,
            {
                "operation": "get",
                "memory_type": "short_term",
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        assert result.data["data"] == test_data

    def test_missing_docs_path(self):
        """Test error when docs_path is missing."""
        skill = MemorySkill()

        result = skill.execute(
            "agent005",
            {
                "operation": "get",
                "memory_type": "short_term",
            },
        )

        assert result.success is False
        assert "docs_path required" in result.message

    def test_invalid_operation(self, temp_docs_path):
        """Test error with invalid operation."""
        skill = MemorySkill()

        result = skill.execute(
            "agent006",
            {
                "operation": "invalid",
                "memory_type": "short_term",
            },
            docs_path=temp_docs_path,
        )

        assert result.success is False
        assert "Invalid operation" in result.message

    def test_invalid_memory_type(self, temp_docs_path):
        """Test error with invalid memory type."""
        skill = MemorySkill()

        result = skill.execute(
            "agent007",
            {
                "operation": "get",
                "memory_type": "invalid_type",
            },
            docs_path=temp_docs_path,
        )

        assert result.success is False
        assert "Invalid memory_type" in result.message

    def test_set_without_data(self, temp_docs_path):
        """Test error when setting memory without data."""
        skill = MemorySkill()

        result = skill.execute(
            "agent008",
            {
                "operation": "set",
                "memory_type": "short_term",
            },
            docs_path=temp_docs_path,
        )

        assert result.success is False
        assert "data required" in result.message

    def test_memory_update_timestamp(self, temp_docs_path):
        """Test that memory updates have timestamps."""
        skill = MemorySkill()
        agent_id = "agent009"

        result = skill.execute(
            agent_id,
            {
                "operation": "set",
                "memory_type": "short_term",
                "data": {"test": "data"},
            },
            docs_path=temp_docs_path,
        )

        assert "timestamp" in result.data
        assert "updated_at" in result.data
