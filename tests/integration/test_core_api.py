"""
Integration tests for Core API endpoints.
Tests the main API endpoints: health, projects, commands, and artifacts.
"""

import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil
import sys
import os
import subprocess
from pathlib import Path

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
    from routers import projects, commands, artifacts

    test_app.include_router(projects.router, prefix="/projects", tags=["projects"])
    test_app.include_router(
        commands.router,
        prefix="/projects/{project_key}/commands",
        tags=["commands"],
    )
    test_app.include_router(
        artifacts.router,
        prefix="/projects/{project_key}/artifacts",
        tags=["artifacts"],
    )

    # Add health endpoint
    @test_app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "docs_path": temp_project_dir,
            "docs_exists": os.path.exists(temp_project_dir),
            "docs_is_git": os.path.exists(os.path.join(temp_project_dir, ".git")),
        }

    # Initialize services
    from services.git_manager import GitManager
    from services.llm_service import LLMService

    git_manager = GitManager(temp_project_dir)
    git_manager.ensure_repository()
    test_app.state.git_manager = git_manager
    test_app.state.llm_service = LLMService()

    with TestClient(test_app) as test_client:
        yield test_client


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_status(self, client):
        """Test that health check returns status field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_returns_docs_path(self, client):
        """Test that health check returns docs_path."""
        response = client.get("/health")
        data = response.json()
        assert "docs_path" in data
        assert data["docs_path"] is not None

    def test_health_check_verifies_git_repo(self, client):
        """Test that health check verifies git repo exists."""
        response = client.get("/health")
        data = response.json()
        assert "docs_exists" in data
        assert "docs_is_git" in data
        assert data["docs_exists"] is True
        assert data["docs_is_git"] is True


class TestProjectsAPI:
    """Test project management endpoints."""

    def test_create_project_success(self, client):
        """Test creating a new project."""
        response = client.post(
            "/projects", json={"key": "TEST001", "name": "Test Project"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["key"] == "TEST001"
        assert data["name"] == "Test Project"
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_project_duplicate_fails(self, client):
        """Test that creating duplicate project returns 409."""
        # Create first project
        client.post("/projects", json={"key": "DUP001", "name": "Project 1"})

        # Try to create duplicate
        response = client.post("/projects", json={"key": "DUP001", "name": "Project 2"})

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_project_missing_key(self, client):
        """Test that creating project without key fails."""
        response = client.post("/projects", json={"name": "No Key Project"})
        assert response.status_code == 422  # Validation error

    def test_create_project_missing_name(self, client):
        """Test that creating project without name fails."""
        response = client.post("/projects", json={"key": "NONAME"})
        assert response.status_code == 422  # Validation error

    def test_list_projects_empty(self, client):
        """Test listing projects when none exist."""
        response = client.get("/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_projects_returns_created_projects(self, client):
        """Test that listing returns created projects."""
        # Create multiple projects
        client.post("/projects", json={"key": "PROJ1", "name": "Project 1"})
        client.post("/projects", json={"key": "PROJ2", "name": "Project 2"})
        client.post("/projects", json={"key": "PROJ3", "name": "Project 3"})

        response = client.get("/projects")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        keys = [p["key"] for p in data]
        assert "PROJ1" in keys
        assert "PROJ2" in keys
        assert "PROJ3" in keys

    def test_get_project_state_success(self, client):
        """Test getting project state."""
        # Create project
        client.post("/projects", json={"key": "STATE001", "name": "State Test"})

        response = client.get("/projects/STATE001/state")
        assert response.status_code == 200
        data = response.json()

        assert "project_info" in data
        assert data["project_info"]["key"] == "STATE001"
        assert "artifacts" in data
        assert "last_commit" in data

    def test_get_project_state_nonexistent_returns_404(self, client):
        """Test getting state for nonexistent project."""
        response = client.get("/projects/NONEXISTENT/state")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestCommandsAPI:
    """Test command propose/apply endpoints."""

    @pytest.fixture
    def test_project(self, client):
        """Create a test project."""
        response = client.post(
            "/projects", json={"key": "CMD001", "name": "Command Test"}
        )
        assert response.status_code == 201
        return response.json()

    def test_propose_command_nonexistent_project(self, client):
        """Test proposing command for nonexistent project."""
        response = client.post(
            "/projects/NONEXISTENT/commands/propose",
            json={"command": "assess_gaps", "params": {}},
        )
        assert response.status_code == 404

    def test_propose_unknown_command(self, client, test_project):
        """Test proposing an unknown command."""
        response = client.post(
            "/projects/CMD001/commands/propose",
            json={"command": "unknown_command", "params": {}},
        )
        assert response.status_code == 400
        assert "Unknown command" in response.json()["detail"]

    def test_propose_assess_gaps_command(self, client, test_project):
        """Test proposing assess_gaps command."""
        response = client.post(
            "/projects/CMD001/commands/propose",
            json={"command": "assess_gaps", "params": {}},
        )

        # May succeed or fail depending on LLM availability
        # If LLM unavailable, command service handles gracefully
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "proposal_id" in data
            assert "assistant_message" in data
            assert "file_changes" in data
            assert "draft_commit_message" in data

    def test_propose_generate_artifact_command(self, client, test_project):
        """Test proposing generate_artifact command."""
        response = client.post(
            "/projects/CMD001/commands/propose",
            json={
                "command": "generate_artifact",
                "params": {
                    "artifact_name": "project_charter.md",
                    "artifact_type": "project_charter",
                },
            },
        )

        # May succeed or fail depending on LLM availability
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "proposal_id" in data
            assert "file_changes" in data

    def test_apply_nonexistent_proposal(self, client, test_project):
        """Test applying nonexistent proposal."""
        response = client.post(
            "/projects/CMD001/commands/apply",
            json={"proposal_id": "nonexistent-proposal-id"},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    def test_apply_command_nonexistent_project(self, client):
        """Test applying command for nonexistent project."""
        response = client.post(
            "/projects/NONEXISTENT/commands/apply",
            json={"proposal_id": "some-id"},
        )
        assert response.status_code == 404


class TestArtifactsAPI:
    """Test artifact listing and retrieval endpoints."""

    @pytest.fixture
    def test_project_with_artifacts(self, client, temp_project_dir):
        """Create a test project with artifacts."""
        # Create project
        response = client.post(
            "/projects", json={"key": "ART001", "name": "Artifact Test"}
        )
        assert response.status_code == 201

        # Write some artifacts directly via filesystem
        import os
        from pathlib import Path

        project_path = Path(temp_project_dir) / "ART001" / "artifacts"
        project_path.mkdir(parents=True, exist_ok=True)

        (project_path / "charter.md").write_text("# Project Charter\n\nTest content")
        (project_path / "plan.md").write_text("# Project Plan\n\nTest plan")

        # Commit directly via git commands
        try:
            subprocess.run(
                ["git", "add", "."],
                cwd=temp_project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "[ART001] Add test artifacts"],
                cwd=temp_project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            pytest.fail(
                f"Git command failed in test fixture.\n"
                f"  Command: {exc.cmd}\n"
                f"  Return code: {exc.returncode}\n"
                f"  Stdout: {exc.stdout}\n"
                f"  Stderr: {exc.stderr}"
            )

        return "ART001"

    def test_list_artifacts_nonexistent_project(self, client):
        """Test listing artifacts for nonexistent project."""
        response = client.get("/projects/NONEXISTENT/artifacts")
        assert response.status_code == 404

    def test_list_artifacts_empty_project(self, client):
        """Test listing artifacts for project with no artifacts."""
        client.post("/projects", json={"key": "EMPTY", "name": "Empty Project"})
        response = client.get("/projects/EMPTY/artifacts")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_artifacts_returns_artifacts(
        self, client, test_project_with_artifacts
    ):
        """Test listing artifacts returns created artifacts."""
        response = client.get("/projects/ART001/artifacts")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

        artifact_names = [a["name"] for a in data]
        assert "charter.md" in artifact_names
        assert "plan.md" in artifact_names

    def test_get_artifact_nonexistent_project(self, client):
        """Test getting artifact for nonexistent project."""
        response = client.get("/projects/NONEXISTENT/artifacts/test.md")
        assert response.status_code == 404

    def test_get_artifact_nonexistent_file(self, client):
        """Test getting nonexistent artifact."""
        client.post("/projects", json={"key": "GETART", "name": "Get Artifact Test"})
        response = client.get("/projects/GETART/artifacts/nonexistent.md")
        assert response.status_code == 404

    def test_get_artifact_success(self, client, test_project_with_artifacts):
        """Test successfully getting an artifact."""
        response = client.get("/projects/ART001/artifacts/artifacts/charter.md")

        assert response.status_code == 200
        content = response.text
        assert "Project Charter" in content
        assert response.headers["content-type"] in [
            "text/markdown",
            "text/markdown; charset=utf-8",
        ]

    def test_get_artifact_returns_correct_content(
        self, client, test_project_with_artifacts
    ):
        """Test that artifact content is correct."""
        response = client.get("/projects/ART001/artifacts/artifacts/plan.md")

        assert response.status_code == 200
        content = response.text
        assert "Project Plan" in content
        assert "Test plan" in content


class TestAPIIntegrationFlow:
    """Test complete API workflows."""

    def test_complete_project_workflow(self, client):
        """Test creating project and managing artifacts."""
        # 1. Create project
        create_response = client.post(
            "/projects", json={"key": "FLOW001", "name": "Flow Test"}
        )
        assert create_response.status_code == 201

        # 2. Get project state
        state_response = client.get("/projects/FLOW001/state")
        assert state_response.status_code == 200

        # 3. List projects
        list_response = client.get("/projects")
        assert list_response.status_code == 200
        projects = list_response.json()
        assert any(p["key"] == "FLOW001" for p in projects)

        # 4. List artifacts (should be empty)
        artifacts_response = client.get("/projects/FLOW001/artifacts")
        assert artifacts_response.status_code == 200
        assert len(artifacts_response.json()) == 0

    def test_error_handling_consistency(self, client):
        """Test that 404 errors are consistent across endpoints."""
        # All these should return 404 for nonexistent project
        endpoints = [
            ("/projects/NOTFOUND/state", "get"),
            ("/projects/NOTFOUND/artifacts", "get"),
            ("/projects/NOTFOUND/commands/propose", "post"),
            ("/projects/NOTFOUND/commands/apply", "post"),
        ]

        for endpoint, method in endpoints:
            if method == "get":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})

            assert response.status_code in [404, 422], f"Failed for {endpoint}"
