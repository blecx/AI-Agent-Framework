"""
Unit tests for Learning Skill.
"""
import pytest
import tempfile
import shutil
import json
import os
from apps.api.skills.learning_skill import LearningSkill
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
def learning_skill():
    """Create a LearningSkill instance."""
    return LearningSkill()


class TestLearningSkillMetadata:
    """Test learning skill metadata."""

    def test_get_metadata(self, learning_skill):
        """Test getting learning skill metadata."""
        metadata = learning_skill.get_metadata()
        
        assert metadata.name == "learning"
        assert metadata.version == "1.0.0"
        assert "learn" in metadata.description.lower() or "experience" in metadata.description.lower()
        assert "experience" in metadata.input_schema["properties"]
        assert "experience_id" in metadata.output_schema["properties"]


@pytest.mark.asyncio
class TestLearningSkillExecution:
    """Test learning skill execution."""

    async def test_record_experience(self, learning_skill, git_manager):
        """Test recording a basic experience."""
        experience = {
            "input": {"action": "test", "parameters": {"x": 1}},
            "outcome": {"success": True, "result": "completed"},
            "feedback": "Good result",
            "context": {"environment": "test"}
        }
        
        result = await learning_skill.execute(
            agent_id="test_agent",
            input_data={"experience": experience},
            context={"git_manager": git_manager}
        )
        
        assert result["agent_id"] == "test_agent"
        assert "experience_id" in result
        assert "recorded_at" in result
        assert result["message"] == "Experience recorded successfully"

    async def test_experience_persistence(self, learning_skill, git_manager):
        """Test that experiences are persisted to file."""
        agent_id = "persist_test"
        experience = {
            "input": {"task": "test"},
            "outcome": {"status": "success"}
        }
        
        result = await learning_skill.execute(
            agent_id=agent_id,
            input_data={"experience": experience},
            context={"git_manager": git_manager}
        )
        
        # Verify file exists
        experiences_file = os.path.join(
            str(git_manager.base_path), "_agents", "experiences", f"{agent_id}.ndjson"
        )
        assert os.path.exists(experiences_file)
        
        # Verify content
        with open(experiences_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 1
        stored = json.loads(lines[0])
        assert stored["agent_id"] == agent_id
        assert stored["experience_id"] == result["experience_id"]
        assert stored["input"]["task"] == "test"

    async def test_multiple_experiences_append(self, learning_skill, git_manager):
        """Test that multiple experiences append to the same file."""
        agent_id = "multi_test"
        
        # Record first experience
        await learning_skill.execute(
            agent_id=agent_id,
            input_data={
                "experience": {
                    "input": {"action": "first"},
                    "outcome": {"result": 1}
                }
            },
            context={"git_manager": git_manager}
        )
        
        # Record second experience
        await learning_skill.execute(
            agent_id=agent_id,
            input_data={
                "experience": {
                    "input": {"action": "second"},
                    "outcome": {"result": 2}
                }
            },
            context={"git_manager": git_manager}
        )
        
        # Verify both are in file
        experiences_file = os.path.join(
            str(git_manager.base_path), "_agents", "experiences", f"{agent_id}.ndjson"
        )
        
        with open(experiences_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 2
        
        exp1 = json.loads(lines[0])
        exp2 = json.loads(lines[1])
        
        assert exp1["input"]["action"] == "first"
        assert exp2["input"]["action"] == "second"

    async def test_experience_with_feedback(self, learning_skill, git_manager):
        """Test recording experience with feedback."""
        experience = {
            "input": {"task": "test"},
            "outcome": {"success": True},
            "feedback": "Excellent performance"
        }
        
        result = await learning_skill.execute(
            agent_id="test",
            input_data={"experience": experience},
            context={"git_manager": git_manager}
        )
        
        # Verify feedback is stored
        experiences_file = os.path.join(
            str(git_manager.base_path), "_agents", "experiences", f"test.ndjson"
        )
        
        with open(experiences_file, 'r') as f:
            stored = json.loads(f.readline())
        
        assert stored["feedback"] == "Excellent performance"

    async def test_experience_without_feedback(self, learning_skill, git_manager):
        """Test recording experience without optional feedback."""
        experience = {
            "input": {"task": "test"},
            "outcome": {"success": True}
        }
        
        result = await learning_skill.execute(
            agent_id="test",
            input_data={"experience": experience},
            context={"git_manager": git_manager}
        )
        
        assert "experience_id" in result
        assert result["message"] == "Experience recorded successfully"

    async def test_missing_experience_raises_error(self, learning_skill, git_manager):
        """Test that missing experience raises error."""
        with pytest.raises(ValueError, match="experience is required"):
            await learning_skill.execute(
                agent_id="test",
                input_data={},
                context={"git_manager": git_manager}
            )

    async def test_missing_input_raises_error(self, learning_skill, git_manager):
        """Test that experience without input raises error."""
        with pytest.raises(ValueError, match="must contain 'input' and 'outcome'"):
            await learning_skill.execute(
                agent_id="test",
                input_data={
                    "experience": {"outcome": {"success": True}}
                },
                context={"git_manager": git_manager}
            )

    async def test_missing_outcome_raises_error(self, learning_skill, git_manager):
        """Test that experience without outcome raises error."""
        with pytest.raises(ValueError, match="must contain 'input' and 'outcome'"):
            await learning_skill.execute(
                agent_id="test",
                input_data={
                    "experience": {"input": {"task": "test"}}
                },
                context={"git_manager": git_manager}
            )

    async def test_missing_git_manager_raises_error(self, learning_skill):
        """Test that missing git_manager raises error."""
        with pytest.raises(ValueError, match="git_manager required"):
            await learning_skill.execute(
                agent_id="test",
                input_data={
                    "experience": {
                        "input": {"task": "test"},
                        "outcome": {"success": True}
                    }
                },
                context={}
            )

    async def test_ndjson_format(self, learning_skill, git_manager):
        """Test that experiences are stored in valid NDJSON format."""
        agent_id = "ndjson_test"
        
        # Record multiple experiences
        for i in range(3):
            await learning_skill.execute(
                agent_id=agent_id,
                input_data={
                    "experience": {
                        "input": {"iteration": i},
                        "outcome": {"value": i * 2}
                    }
                },
                context={"git_manager": git_manager}
            )
        
        # Verify NDJSON format (each line is valid JSON)
        experiences_file = os.path.join(
            str(git_manager.base_path), "_agents", "experiences", f"{agent_id}.ndjson"
        )
        
        with open(experiences_file, 'r') as f:
            for line_num, line in enumerate(f):
                # Each line should be valid JSON
                data = json.loads(line.strip())
                assert data["agent_id"] == agent_id
                assert "experience_id" in data
                assert data["input"]["iteration"] == line_num
