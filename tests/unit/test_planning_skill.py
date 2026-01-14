"""
Unit tests for Planning Skill.
"""
import pytest
from apps.api.skills.planning_skill import PlanningSkill


@pytest.fixture
def planning_skill():
    """Create a PlanningSkill instance."""
    return PlanningSkill()


class TestPlanningSkillMetadata:
    """Test planning skill metadata."""

    def test_get_metadata(self, planning_skill):
        """Test getting planning skill metadata."""
        metadata = planning_skill.get_metadata()
        
        assert metadata.name == "planning"
        assert metadata.version == "1.0.0"
        assert "plan" in metadata.description.lower()
        assert "goal" in metadata.input_schema["properties"]
        assert "steps" in metadata.output_schema["properties"]


@pytest.mark.asyncio
class TestPlanningSkillExecution:
    """Test planning skill execution."""

    async def test_create_basic_plan(self, planning_skill):
        """Test creating a basic plan."""
        result = await planning_skill.execute(
            agent_id="test_agent",
            input_data={
                "goal": "Implement a new feature",
                "constraints": [],
                "context": {}
            },
            context={}
        )
        
        assert result["agent_id"] == "test_agent"
        assert result["goal"] == "Implement a new feature"
        assert len(result["steps"]) > 0
        assert "created_at" in result
        assert "estimated_total_duration" in result

    async def test_plan_steps_structure(self, planning_skill):
        """Test that plan steps have correct structure."""
        result = await planning_skill.execute(
            agent_id="test",
            input_data={"goal": "Test goal"},
            context={}
        )
        
        steps = result["steps"]
        assert len(steps) > 0
        
        # Check first step structure
        first_step = steps[0]
        assert first_step["step_number"] == 1
        assert "title" in first_step
        assert "description" in first_step
        assert "estimated_duration" in first_step
        assert "dependencies" in first_step
        assert first_step["status"] == "pending"

    async def test_plan_with_constraints(self, planning_skill):
        """Test creating plan with constraints."""
        constraints = ["Time constraint: 2 days", "Budget constraint: $1000"]
        
        result = await planning_skill.execute(
            agent_id="test",
            input_data={
                "goal": "Build feature",
                "constraints": constraints,
                "context": {}
            },
            context={}
        )
        
        # Should create additional step for constraint verification
        assert len(result["steps"]) >= 4
        
        # Last step should verify constraints
        last_step = result["steps"][-1]
        assert "constraint" in last_step["title"].lower() or "verify" in last_step["title"].lower()

    async def test_plan_with_context(self, planning_skill):
        """Test creating plan with additional context."""
        result = await planning_skill.execute(
            agent_id="test",
            input_data={
                "goal": "Deploy application",
                "constraints": [],
                "context": {"environment": "production", "priority": "high"}
            },
            context={}
        )
        
        assert result["goal"] == "Deploy application"
        assert len(result["steps"]) > 0

    async def test_step_dependencies(self, planning_skill):
        """Test that steps have proper dependencies."""
        result = await planning_skill.execute(
            agent_id="test",
            input_data={"goal": "Test dependencies"},
            context={}
        )
        
        steps = result["steps"]
        
        # First step should have no dependencies
        assert steps[0]["dependencies"] == []
        
        # Later steps should depend on earlier steps
        for i in range(1, len(steps)):
            assert len(steps[i]["dependencies"]) > 0
            # Dependencies should be earlier step numbers
            for dep in steps[i]["dependencies"]:
                assert dep < steps[i]["step_number"]

    async def test_duration_estimation(self, planning_skill):
        """Test that duration is estimated."""
        result = await planning_skill.execute(
            agent_id="test",
            input_data={"goal": "Test duration"},
            context={}
        )
        
        # Each step should have estimated duration
        for step in result["steps"]:
            assert step["estimated_duration"] is not None
            assert "h" in step["estimated_duration"] or "m" in step["estimated_duration"]
        
        # Total duration should be calculated
        assert result["estimated_total_duration"] is not None
        total = result["estimated_total_duration"]
        assert "h" in total or "m" in total

    async def test_missing_goal_raises_error(self, planning_skill):
        """Test that missing goal raises error."""
        with pytest.raises(ValueError, match="goal is required"):
            await planning_skill.execute(
                agent_id="test",
                input_data={},
                context={}
            )

    async def test_empty_goal_raises_error(self, planning_skill):
        """Test that empty goal raises error."""
        with pytest.raises(ValueError, match="goal is required"):
            await planning_skill.execute(
                agent_id="test",
                input_data={"goal": ""},
                context={}
            )

    async def test_estimate_total_duration_calculation(self, planning_skill):
        """Test the total duration calculation."""
        # Create a simple plan
        result = await planning_skill.execute(
            agent_id="test",
            input_data={"goal": "Test calculation"},
            context={}
        )
        
        # The skill has a public helper we can use to verify calculation
        total_minutes = planning_skill._parse_duration_to_minutes(result["steps"])
        formatted = planning_skill._format_duration(total_minutes)
        
        assert result["estimated_total_duration"] == formatted

    async def test_duration_parsing_edge_cases(self, planning_skill):
        """Test that duration parsing handles edge cases."""
        # Test various duration formats
        assert planning_skill._parse_single_duration("2h") == 120
        assert planning_skill._parse_single_duration("30m") == 30
        assert planning_skill._parse_single_duration("1h 30m") == 90
        assert planning_skill._parse_single_duration("") == 0
        assert planning_skill._parse_single_duration("invalid") == 0
        assert planning_skill._parse_single_duration(None) == 0
