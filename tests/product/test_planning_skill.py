"""
Unit tests for Planning Skill.
"""

import pytest
import tempfile
import shutil
import os
import json
from apps.api.skills.planning_skill import PlanningSkill


@pytest.fixture
def temp_docs_path():
    """Create a temporary docs directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestPlanningSkill:
    """Test PlanningSkill functionality."""

    def test_skill_metadata(self):
        """Test skill metadata."""
        skill = PlanningSkill()
        assert skill.name == "planning"
        assert skill.version == "1.0.0"
        assert skill.description

    def test_generate_simple_plan(self, temp_docs_path):
        """Test generating a simple plan."""
        skill = PlanningSkill()
        agent_id = "agent001"

        result = skill.execute(
            agent_id,
            {
                "goal": "Complete a simple task",
                "constraints": [],
                "context": {},
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        assert "steps" in result.data
        assert len(result.data["steps"]) > 0
        assert "plan_id" in result.metadata

    def test_plan_with_constraints(self, temp_docs_path):
        """Test generating a plan with constraints."""
        skill = PlanningSkill()
        agent_id = "agent002"

        result = skill.execute(
            agent_id,
            {
                "goal": "Deploy application",
                "constraints": ["Limited budget", "Tight timeline"],
                "context": {"environment": "production"},
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        assert result.data["constraints"] == ["Limited budget", "Tight timeline"]
        # Should have additional step for constraint assessment
        steps = result.data["steps"]
        assert any("constraint" in step["action"].lower() for step in steps)

    def test_plan_for_creation_task(self, temp_docs_path):
        """Test plan generation for creation/build task."""
        skill = PlanningSkill()
        agent_id = "agent003"

        result = skill.execute(
            agent_id,
            {
                "goal": "Create a new feature",
                "constraints": [],
                "context": {},
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        steps = result.data["steps"]
        step_actions = [step["action"] for step in steps]

        # Should include design and implementation steps
        assert "design" in step_actions
        assert "implement" in step_actions
        assert "verify" in step_actions

    def test_plan_for_fix_task(self, temp_docs_path):
        """Test plan generation for fix/resolve task."""
        skill = PlanningSkill()
        agent_id = "agent004"

        result = skill.execute(
            agent_id,
            {
                "goal": "Fix bug in authentication",
                "constraints": [],
                "context": {},
            },
            docs_path=temp_docs_path,
        )

        assert result.success is True
        steps = result.data["steps"]
        step_actions = [step["action"] for step in steps]

        # Should include diagnose and resolve steps
        assert "diagnose" in step_actions
        assert "resolve" in step_actions

    def test_plan_persistence(self, temp_docs_path):
        """Test that plans are persisted to disk."""
        skill = PlanningSkill()
        agent_id = "agent005"

        result = skill.execute(
            agent_id,
            {
                "goal": "Test persistence",
                "constraints": [],
                "context": {},
            },
            docs_path=temp_docs_path,
        )

        plan_id = result.metadata["plan_id"]
        plan_file = os.path.join(
            temp_docs_path, "agents", agent_id, "plans", f"{plan_id}.json"
        )

        assert os.path.exists(plan_file)

        with open(plan_file, "r") as f:
            saved_plan = json.load(f)

        assert saved_plan["plan_id"] == plan_id
        assert saved_plan["goal"] == "Test persistence"
        assert "steps" in saved_plan

    def test_plan_step_structure(self, temp_docs_path):
        """Test that plan steps have correct structure."""
        skill = PlanningSkill()
        agent_id = "agent006"

        result = skill.execute(
            agent_id,
            {
                "goal": "Test step structure",
                "constraints": [],
                "context": {},
            },
            docs_path=temp_docs_path,
        )

        steps = result.data["steps"]
        for step in steps:
            assert "step" in step
            assert "action" in step
            assert "description" in step
            assert "status" in step
            assert "dependencies" in step
            assert step["status"] == "pending"

    def test_plan_dependencies(self, temp_docs_path):
        """Test that plan steps have proper dependencies."""
        skill = PlanningSkill()
        agent_id = "agent007"

        result = skill.execute(
            agent_id,
            {
                "goal": "Test dependencies",
                "constraints": [],
                "context": {},
            },
            docs_path=temp_docs_path,
        )

        steps = result.data["steps"]
        # First step should have no dependencies
        assert steps[0]["dependencies"] == []

        # Other steps should depend on previous steps
        for i in range(1, len(steps)):
            assert len(steps[i]["dependencies"]) > 0

    def test_missing_goal(self, temp_docs_path):
        """Test error when goal is missing."""
        skill = PlanningSkill()

        result = skill.execute(
            "agent008",
            {
                "constraints": [],
                "context": {},
            },
            docs_path=temp_docs_path,
        )

        assert result.success is False
        assert "goal is required" in result.message

    def test_missing_docs_path(self):
        """Test error when docs_path is missing."""
        skill = PlanningSkill()

        result = skill.execute(
            "agent009",
            {
                "goal": "Test",
                "constraints": [],
                "context": {},
            },
        )

        assert result.success is False
        assert "docs_path required" in result.message
