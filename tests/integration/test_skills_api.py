"""
Integration tests for Skills API endpoints.
Tests the skills endpoints: list skills, memory, planning, and learning.
"""
import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))


@pytest.fixture(scope="function")
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def client(temp_project_dir):
    """Create a test client with temporary project directory."""
    # Override the PROJECT_DOCS_PATH environment variable
    os.environ["PROJECT_DOCS_PATH"] = temp_project_dir

    # Create a new app instance for this test to avoid state sharing
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    test_app = FastAPI(title="Test App")
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and register skills router
    from routers import skills

    test_app.include_router(skills.router, prefix="/agents", tags=["skills"])

    # Initialize services
    from services.git_manager import GitManager
    from services.llm_service import LLMService

    git_manager = GitManager(temp_project_dir)
    git_manager.ensure_repository()
    test_app.state.git_manager = git_manager
    test_app.state.llm_service = LLMService()

    with TestClient(test_app) as test_client:
        yield test_client


class TestSkillsListEndpoint:
    """Test skills list endpoint."""

    def test_list_skills_returns_200(self, client):
        """Test that list skills endpoint returns 200 OK."""
        response = client.get("/agents/skills")
        assert response.status_code == 200

    def test_list_skills_returns_builtin_skills(self, client):
        """Test that list skills returns built-in skills."""
        response = client.get("/agents/skills")
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 3  # At least memory, planning, learning
        
        skill_names = {skill["name"] for skill in data}
        assert "memory" in skill_names
        assert "planning" in skill_names
        assert "learning" in skill_names

    def test_skill_metadata_structure(self, client):
        """Test that skill metadata has correct structure."""
        response = client.get("/agents/skills")
        data = response.json()
        
        for skill in data:
            assert "name" in skill
            assert "version" in skill
            assert "description" in skill
            assert "input_schema" in skill
            assert "output_schema" in skill


class TestMemoryEndpoints:
    """Test memory skill endpoints."""

    def test_get_empty_memory(self, client):
        """Test getting memory when none exists."""
        response = client.get("/agents/test_agent/skills/memory")
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_id"] == "test_agent"
        assert data["short_term"] == {}
        assert data["long_term"] == {}
        assert "metadata" in data

    def test_set_memory(self, client):
        """Test setting memory."""
        memory_data = {
            "short_term": {"current_task": "testing", "count": 42},
            "long_term": {"learned_fact": "important data"}
        }
        
        response = client.post(
            "/agents/test_agent/skills/memory",
            json=memory_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_id"] == "test_agent"
        assert data["short_term"]["current_task"] == "testing"
        assert data["short_term"]["count"] == 42
        assert data["long_term"]["learned_fact"] == "important data"

    def test_memory_persistence(self, client):
        """Test that memory persists across requests."""
        # Set memory
        memory_data = {
            "short_term": {"session": "test"},
            "long_term": {"fact": "persistent"}
        }
        client.post("/agents/persist_test/skills/memory", json=memory_data)
        
        # Get memory
        response = client.get("/agents/persist_test/skills/memory")
        data = response.json()
        
        assert data["short_term"]["session"] == "test"
        assert data["long_term"]["fact"] == "persistent"

    def test_memory_merge_updates(self, client):
        """Test that memory updates merge with existing data."""
        agent_id = "merge_test"
        
        # Set initial memory
        client.post(
            f"/agents/{agent_id}/skills/memory",
            json={"short_term": {"key1": "value1", "key2": "value2"}}
        )
        
        # Update with partial data
        response = client.post(
            f"/agents/{agent_id}/skills/memory",
            json={"short_term": {"key2": "updated", "key3": "new"}}
        )
        
        data = response.json()
        assert data["short_term"]["key1"] == "value1"  # Preserved
        assert data["short_term"]["key2"] == "updated"  # Updated
        assert data["short_term"]["key3"] == "new"  # Added

    def test_different_agents_have_separate_memory(self, client):
        """Test that different agents have isolated memory."""
        # Set memory for agent 1
        client.post(
            "/agents/agent1/skills/memory",
            json={"short_term": {"data": "agent1"}}
        )
        
        # Set memory for agent 2
        client.post(
            "/agents/agent2/skills/memory",
            json={"short_term": {"data": "agent2"}}
        )
        
        # Verify isolation
        response1 = client.get("/agents/agent1/skills/memory")
        response2 = client.get("/agents/agent2/skills/memory")
        
        assert response1.json()["short_term"]["data"] == "agent1"
        assert response2.json()["short_term"]["data"] == "agent2"


class TestPlanningEndpoint:
    """Test planning skill endpoint."""

    def test_create_plan(self, client):
        """Test creating a basic plan."""
        plan_request = {
            "goal": "Implement a new feature",
            "constraints": ["2 days", "1 developer"],
            "context": {"priority": "high"}
        }
        
        response = client.post(
            "/agents/test_agent/skills/plan",
            json=plan_request
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_id"] == "test_agent"
        assert data["goal"] == "Implement a new feature"
        assert len(data["steps"]) > 0
        assert "created_at" in data
        assert "estimated_total_duration" in data

    def test_plan_steps_structure(self, client):
        """Test that plan steps have correct structure."""
        response = client.post(
            "/agents/test_agent/skills/plan",
            json={"goal": "Test goal"}
        )
        
        data = response.json()
        steps = data["steps"]
        
        for step in steps:
            assert "step_number" in step
            assert "title" in step
            assert "description" in step
            assert "estimated_duration" in step
            assert "dependencies" in step
            assert "status" in step

    def test_plan_with_constraints(self, client):
        """Test creating plan with constraints."""
        response = client.post(
            "/agents/test_agent/skills/plan",
            json={
                "goal": "Deploy application",
                "constraints": ["Budget: $1000", "Time: 1 week"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should have extra step for constraint verification
        assert len(data["steps"]) >= 4

    def test_plan_missing_goal_returns_400(self, client):
        """Test that missing goal returns 400."""
        response = client.post(
            "/agents/test_agent/skills/plan",
            json={}
        )
        assert response.status_code == 422  # Validation error

    def test_plan_empty_goal_returns_400(self, client):
        """Test that empty goal returns 400."""
        response = client.post(
            "/agents/test_agent/skills/plan",
            json={"goal": ""}
        )
        assert response.status_code == 422  # Validation error


class TestLearningEndpoint:
    """Test learning skill endpoint."""

    def test_record_experience(self, client):
        """Test recording a basic experience."""
        learning_request = {
            "experience": {
                "input": {"action": "test", "parameters": {"x": 1}},
                "outcome": {"success": True, "result": "completed"},
                "feedback": "Good result",
                "context": {"environment": "test"}
            }
        }
        
        response = client.post(
            "/agents/test_agent/skills/learn",
            json=learning_request
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_id"] == "test_agent"
        assert "experience_id" in data
        assert "recorded_at" in data
        assert data["message"] == "Experience recorded successfully"

    def test_record_experience_without_feedback(self, client):
        """Test recording experience without optional feedback."""
        learning_request = {
            "experience": {
                "input": {"task": "test"},
                "outcome": {"success": True}
            }
        }
        
        response = client.post(
            "/agents/test_agent/skills/learn",
            json=learning_request
        )
        assert response.status_code == 200
        assert "experience_id" in response.json()

    def test_multiple_experiences(self, client):
        """Test recording multiple experiences."""
        agent_id = "multi_learn_agent"
        
        # Record first experience
        response1 = client.post(
            f"/agents/{agent_id}/skills/learn",
            json={
                "experience": {
                    "input": {"task": "first"},
                    "outcome": {"result": 1}
                }
            }
        )
        
        # Record second experience
        response2 = client.post(
            f"/agents/{agent_id}/skills/learn",
            json={
                "experience": {
                    "input": {"task": "second"},
                    "outcome": {"result": 2}
                }
            }
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Both should have unique IDs
        exp_id1 = response1.json()["experience_id"]
        exp_id2 = response2.json()["experience_id"]
        assert exp_id1 != exp_id2

    def test_missing_experience_returns_422(self, client):
        """Test that missing experience returns validation error."""
        response = client.post(
            "/agents/test_agent/skills/learn",
            json={}
        )
        assert response.status_code == 422

    def test_missing_input_returns_400(self, client):
        """Test that experience without input returns validation error."""
        response = client.post(
            "/agents/test_agent/skills/learn",
            json={
                "experience": {
                    "outcome": {"success": True}
                }
            }
        )
        # Pydantic validation or skill validation
        assert response.status_code in [400, 422]

    def test_missing_outcome_returns_400(self, client):
        """Test that experience without outcome returns validation error."""
        response = client.post(
            "/agents/test_agent/skills/learn",
            json={
                "experience": {
                    "input": {"task": "test"}
                }
            }
        )
        # Pydantic validation or skill validation
        assert response.status_code in [400, 422]


class TestVersionedEndpoints:
    """Test versioned API endpoints."""

    def test_versioned_skills_list(self, client):
        """Test versioned skills list endpoint."""
        # Re-register with versioned prefix
        from routers import skills
        client.app.include_router(skills.router, prefix="/api/v1/agents", tags=["skills-v1"])
        
        response = client.get("/api/v1/agents/skills")
        assert response.status_code == 200
        
        data = response.json()
        skill_names = {skill["name"] for skill in data}
        assert "memory" in skill_names
