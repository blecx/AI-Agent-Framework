"""
Unit tests for Learning Skill.
"""
import pytest
import tempfile
import shutil
import os
import json
from apps.api.skills.learning_skill import LearningSkill


@pytest.fixture
def temp_docs_path():
    """Create a temporary docs directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestLearningSkill:
    """Test LearningSkill functionality."""

    def test_skill_metadata(self):
        """Test skill metadata."""
        skill = LearningSkill()
        assert skill.name == "learning"
        assert skill.version == "1.0.0"
        assert skill.description

    def test_log_experience(self, temp_docs_path):
        """Test logging an experience."""
        skill = LearningSkill()
        agent_id = "agent001"

        result = skill.execute(
            agent_id,
            {
                "operation": "log",
                "context": "Working on authentication",
                "action": "Implemented JWT tokens",
                "outcome": "Authentication works correctly",
                "feedback": "Good approach",
                "tags": ["authentication", "security"],
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        assert "timestamp" in result.data

        # Verify file was created
        experience_file = os.path.join(
            temp_docs_path, "agents", agent_id, "learning", "experience.ndjson"
        )
        assert os.path.exists(experience_file)

    def test_log_multiple_experiences(self, temp_docs_path):
        """Test logging multiple experiences."""
        skill = LearningSkill()
        agent_id = "agent002"

        # Log first experience
        skill.execute(
            agent_id,
            {
                "operation": "log",
                "context": "Testing",
                "action": "Wrote tests",
                "outcome": "All tests pass",
                "tags": ["testing"],
            },
            docs_path=temp_docs_path,
        )

        # Log second experience
        skill.execute(
            agent_id,
            {
                "operation": "log",
                "context": "Debugging",
                "action": "Fixed bug",
                "outcome": "Bug resolved",
                "tags": ["debugging"],
            },
            docs_path=temp_docs_path,
        )

        # Verify both are stored
        experience_file = os.path.join(
            temp_docs_path, "agents", agent_id, "learning", "experience.ndjson"
        )

        with open(experience_file, "r") as f:
            lines = f.readlines()

        assert len(lines) == 2

    def test_get_summary_no_experiences(self, temp_docs_path):
        """Test getting summary when no experiences exist."""
        skill = LearningSkill()
        agent_id = "agent003"

        result = skill.execute(
            agent_id,
            {
                "operation": "summary",
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        assert result.data["total_experiences"] == 0

    def test_get_summary_with_experiences(self, temp_docs_path):
        """Test getting summary with experiences."""
        skill = LearningSkill()
        agent_id = "agent004"

        # Log some experiences
        for i in range(5):
            skill.execute(
                agent_id,
                {
                    "operation": "log",
                    "context": f"Context {i}",
                    "action": f"Action {i}",
                    "outcome": f"Outcome {i}",
                    "tags": ["tag1", "tag2"] if i % 2 == 0 else ["tag3"],
                },
                docs_path=temp_docs_path,
            )

        # Get summary
        result = skill.execute(
            agent_id,
            {
                "operation": "summary",
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        assert result.data["total_experiences"] == 5
        assert len(result.data["tags"]) > 0
        assert len(result.data["recent_experiences"]) == 5

    def test_summary_tag_counts(self, temp_docs_path):
        """Test that summary includes tag counts."""
        skill = LearningSkill()
        agent_id = "agent005"

        # Log experiences with different tags
        skill.execute(
            agent_id,
            {
                "operation": "log",
                "context": "Test 1",
                "action": "Action 1",
                "outcome": "Outcome 1",
                "tags": ["common", "unique1"],
            },
            docs_path=temp_docs_path,
        )

        skill.execute(
            agent_id,
            {
                "operation": "log",
                "context": "Test 2",
                "action": "Action 2",
                "outcome": "Outcome 2",
                "tags": ["common", "unique2"],
            },
            docs_path=temp_docs_path,
        )

        # Get summary
        result = skill.execute(
            agent_id,
            {
                "operation": "summary",
            },
            docs_path=temp_docs_path,
        )

        tags = {tag["tag"]: tag["count"] for tag in result.data["tags"]}
        assert tags["common"] == 2
        assert tags["unique1"] == 1
        assert tags["unique2"] == 1

    def test_summary_recent_limit(self, temp_docs_path):
        """Test that summary limits recent experiences to 10."""
        skill = LearningSkill()
        agent_id = "agent006"

        # Log 15 experiences
        for i in range(15):
            skill.execute(
                agent_id,
                {
                    "operation": "log",
                    "context": f"Context {i}",
                    "action": f"Action {i}",
                    "outcome": f"Outcome {i}",
                },
                docs_path=temp_docs_path,
            )

        # Get summary
        result = skill.execute(
            agent_id,
            {
                "operation": "summary",
            },
            docs_path=temp_docs_path,
        )

        assert result.data["total_experiences"] == 15
        assert len(result.data["recent_experiences"]) == 10

    def test_missing_required_fields(self, temp_docs_path):
        """Test error when required fields are missing."""
        skill = LearningSkill()

        result = skill.execute(
            "agent007",
            {
                "operation": "log",
                "context": "Test",
                # Missing action and outcome
            },
            docs_path=temp_docs_path,
        )

        assert result.success is False
        assert "required" in result.message.lower()

    def test_invalid_operation(self, temp_docs_path):
        """Test error with invalid operation."""
        skill = LearningSkill()

        result = skill.execute(
            "agent008",
            {
                "operation": "invalid",
            },
            docs_path=temp_docs_path,
        )

        assert result.success is False
        assert "Invalid operation" in result.message

    def test_missing_docs_path(self):
        """Test error when docs_path is missing."""
        skill = LearningSkill()

        result = skill.execute(
            "agent009",
            {
                "operation": "log",
                "context": "Test",
                "action": "Test",
                "outcome": "Test",
            },
        )

        assert result.success is False
        assert "docs_path required" in result.message

    def test_ndjson_format(self, temp_docs_path):
        """Test that experiences are stored in valid NDJSON format."""
        skill = LearningSkill()
        agent_id = "agent010"

        # Log experiences
        skill.execute(
            agent_id,
            {
                "operation": "log",
                "context": "Test",
                "action": "Test action",
                "outcome": "Test outcome",
            },
            docs_path=temp_docs_path,
        )

        experience_file = os.path.join(
            temp_docs_path, "agents", agent_id, "learning", "experience.ndjson"
        )

        # Verify each line is valid JSON
        with open(experience_file, "r") as f:
            for line in f:
                if line.strip():
                    # Should not raise exception
                    json.loads(line)
