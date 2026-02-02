"""
Integration tests for Skills API endpoints.
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

    # Import and register routers
    from routers import skills

    test_app.include_router(skills.router, prefix="/api/v1/agents", tags=["skills"])

    # Initialize services
    from services.git_manager import GitManager
    from services.llm_service import LLMService

    git_manager = GitManager(temp_project_dir)
    git_manager.ensure_repository()
    test_app.state.git_manager = git_manager
    test_app.state.llm_service = LLMService()

    with TestClient(test_app) as test_client:
        yield test_client


class TestSkillsAPI:
    """Test Skills API endpoints."""

    def test_list_skills(self, client):
        """Test listing available skills."""
        response = client.get("/api/v1/agents/test-agent/skills")
        assert response.status_code == 200

        data = response.json()
        assert "skills" in data
        assert "total" in data
        assert data["total"] > 0

        # Check that built-in skills are present
        skill_names = {skill["name"] for skill in data["skills"]}
        assert "memory" in skill_names
        assert "planning" in skill_names
        assert "learning" in skill_names

    def test_get_memory_nonexistent(self, client):
        """Test getting non-existent memory."""
        response = client.get(
            "/api/v1/agents/test-agent/skills/memory",
            params={"memory_type": "short_term"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"] == {}

    def test_set_and_get_memory(self, client):
        """Test setting and getting memory."""
        # Set memory
        set_response = client.post(
            "/api/v1/agents/test-agent/skills/memory",
            json={"memory_type": "short_term", "data": {"key": "value"}},
        )
        assert set_response.status_code == 200

        set_data = set_response.json()
        assert set_data["success"] is True
        assert set_data["data"]["data"]["key"] == "value"

        # Get memory
        get_response = client.get(
            "/api/v1/agents/test-agent/skills/memory",
            params={"memory_type": "short_term"},
        )
        assert get_response.status_code == 200

        get_data = get_response.json()
        assert get_data["success"] is True
        assert get_data["data"]["data"]["key"] == "value"

    def test_set_long_term_memory(self, client):
        """Test setting long-term memory."""
        response = client.post(
            "/api/v1/agents/test-agent/skills/memory",
            json={
                "memory_type": "long_term",
                "data": {"knowledge": "important fact"},
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["data"]["knowledge"] == "important fact"

    def test_create_plan(self, client):
        """Test creating a plan."""
        response = client.post(
            "/api/v1/agents/test-agent/skills/plan",
            json={
                "goal": "Complete project deliverable",
                "constraints": ["Limited time", "Budget constraint"],
                "context": {"priority": "high"},
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "steps" in data["data"]
        assert len(data["data"]["steps"]) > 0
        assert "plan_id" in data["metadata"]
        assert data["data"]["goal"] == "Complete project deliverable"
        assert len(data["data"]["constraints"]) == 2

    def test_create_plan_minimal(self, client):
        """Test creating a plan with minimal parameters."""
        response = client.post(
            "/api/v1/agents/test-agent/skills/plan", json={"goal": "Simple task"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "steps" in data["data"]

    def test_create_plan_missing_goal(self, client):
        """Test creating a plan without goal fails validation."""
        response = client.post(
            "/api/v1/agents/test-agent/skills/plan", json={"constraints": []}
        )
        assert response.status_code == 422  # Validation error

    def test_log_experience(self, client):
        """Test logging an experience."""
        response = client.post(
            "/api/v1/agents/test-agent/skills/learn",
            json={
                "context": "Working on authentication feature",
                "action": "Implemented OAuth2",
                "outcome": "Successful authentication flow",
                "feedback": "Works well with the existing system",
                "tags": ["authentication", "oauth2"],
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "timestamp" in data["data"]

    def test_log_experience_minimal(self, client):
        """Test logging experience with minimal fields."""
        response = client.post(
            "/api/v1/agents/test-agent/skills/learn",
            json={
                "context": "Testing",
                "action": "Wrote tests",
                "outcome": "All tests pass",
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

    def test_log_experience_missing_required(self, client):
        """Test logging experience without required fields fails."""
        response = client.post(
            "/api/v1/agents/test-agent/skills/learn",
            json={
                "context": "Test",
                # Missing action and outcome
            },
        )
        assert response.status_code == 422  # Validation error

    def test_get_learning_summary_empty(self, client):
        """Test getting learning summary when no experiences exist."""
        response = client.get("/api/v1/agents/test-agent/skills/learn/summary")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_experiences"] == 0

    def test_get_learning_summary_with_data(self, client):
        """Test getting learning summary after logging experiences."""
        # Log some experiences
        for i in range(3):
            client.post(
                "/api/v1/agents/test-agent/skills/learn",
                json={
                    "context": f"Context {i}",
                    "action": f"Action {i}",
                    "outcome": f"Outcome {i}",
                    "tags": ["test", f"tag{i}"],
                },
            )

        # Get summary
        response = client.get("/api/v1/agents/test-agent/skills/learn/summary")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_experiences"] == 3
        assert len(data["data"]["tags"]) > 0

    def test_different_agents_isolated(self, client):
        """Test that different agents have isolated data."""
        # Set memory for agent1
        client.post(
            "/api/v1/agents/agent1/skills/memory",
            json={"memory_type": "short_term", "data": {"agent": "one"}},
        )

        # Set memory for agent2
        client.post(
            "/api/v1/agents/agent2/skills/memory",
            json={"memory_type": "short_term", "data": {"agent": "two"}},
        )

        # Get agent1 memory
        response1 = client.get(
            "/api/v1/agents/agent1/skills/memory", params={"memory_type": "short_term"}
        )
        data1 = response1.json()
        assert data1["data"]["data"]["agent"] == "one"

        # Get agent2 memory
        response2 = client.get(
            "/api/v1/agents/agent2/skills/memory", params={"memory_type": "short_term"}
        )
        data2 = response2.json()
        assert data2["data"]["data"]["agent"] == "two"

    def test_skill_workflow(self, client):
        """Test a complete workflow using multiple skills."""
        agent_id = "workflow-agent"

        # 1. Create a plan
        plan_response = client.post(
            f"/api/v1/agents/{agent_id}/skills/plan",
            json={"goal": "Implement new feature"},
        )
        assert plan_response.status_code == 200
        plan_data = plan_response.json()
        assert plan_data["success"] is True

        # 2. Store plan in memory
        memory_response = client.post(
            f"/api/v1/agents/{agent_id}/skills/memory",
            json={
                "memory_type": "short_term",
                "data": {"current_plan": plan_data["data"]},
            },
        )
        assert memory_response.status_code == 200

        # 3. Log experience
        learn_response = client.post(
            f"/api/v1/agents/{agent_id}/skills/learn",
            json={
                "context": "Executing plan for new feature",
                "action": "Completed design phase",
                "outcome": "Design approved",
                "tags": ["planning", "design"],
            },
        )
        assert learn_response.status_code == 200

        # 4. Verify memory was stored
        get_memory_response = client.get(
            f"/api/v1/agents/{agent_id}/skills/memory",
            params={"memory_type": "short_term"},
        )
        memory_data = get_memory_response.json()
        assert "current_plan" in memory_data["data"]["data"]
