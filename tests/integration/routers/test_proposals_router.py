"""
Integration tests for Proposal router endpoints.
Tests all CRUD operations and apply/reject workflows with real FastAPI TestClient.
"""

import os
import sys

# Import the FastAPI app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../apps/api"))

import pytest  # noqa: E402
import tempfile  # noqa: E402
import shutil  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402
from services.git_manager import GitManager  # noqa: E402
from services.audit_service import AuditService  # noqa: E402


@pytest.fixture
def temp_project_docs():
    """Create temporary projectDocs directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(temp_project_docs):
    """Create test client with initialized app state."""
    # Initialize services in app state (mimics lifespan startup)
    git_manager = GitManager(base_path=temp_project_docs)
    git_manager.ensure_repository()
    app.state.git_manager = git_manager
    app.state.audit_service = AuditService()

    # Debug: Check if proposals router is registered
    print(f"App routes count: {len(app.routes)}")
    proposal_routes = [
        r.path for r in app.routes if hasattr(r, "path") and "proposal" in r.path
    ]
    print(f"Proposal routes: {proposal_routes}")

    return TestClient(app)


@pytest.fixture
def test_project(client):
    """Create a test project."""
    project_data = {
        "key": "TEST",
        "name": "Test Project",
        "description": "Test project for proposal testing",
    }
    response = client.post("/api/v1/projects", json=project_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_artifact(client, test_project):
    """Create a sample artifact for testing updates."""
    project_key = test_project["key"]
    artifact_path = "artifacts/requirements.md"
    content = "# Requirements\n\n- REQ-001: Initial requirement\n"

    # Write artifact directly via git_manager
    git_manager = app.state.git_manager
    git_manager.write_file(project_key, artifact_path, content)
    git_manager.commit_changes(
        project_key, f"Create {artifact_path}", files=[artifact_path]
    )

    return {"path": artifact_path, "content": content}


@pytest.fixture
def sample_proposal_create():
    """Sample proposal creation payload (CREATE type)."""
    return {
        "id": "prop-001",
        "target_artifact": "artifacts/new-doc.md",
        "change_type": "create",
        "diff": "# New Document\n\nThis is a new artifact.",
        "rationale": "Creating new project documentation",
        "author": "test-user",
    }


# ============================================================================
# POST /api/v1/projects/{key}/proposals - Create Proposal
# ============================================================================


def test_create_proposal_success(client, test_project, sample_proposal_create):
    """Test successful proposal creation."""
    project_key = test_project["key"]

    # Debug: list all routes
    routes = [r.path for r in client.app.routes if hasattr(r, "path")]
    print(f"All routes: {[r for r in routes if 'proposal' in r]}")

    response = client.post(
        f"/api/v1/projects/{project_key}/proposals", json=sample_proposal_create
    )

    if response.status_code != 201:
        print(f"Response: {response.json()}")

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "prop-001"
    assert data["project_key"] == project_key
    assert data["target_artifact"] == "artifacts/new-doc.md"
    assert data["change_type"] == "create"
    assert data["status"] == "pending"
    assert data["author"] == "test-user"
    assert "created_at" in data


def test_create_proposal_project_not_found(client, sample_proposal_create):
    """Test proposal creation for non-existent project returns 404."""
    response = client.post(
        "/api/v1/projects/NONEXISTENT/proposals", json=sample_proposal_create
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_proposal_invalid_change_type(client, test_project):
    """Test proposal creation with invalid change_type returns 422."""
    project_key = test_project["key"]
    invalid_proposal = {
        "id": "prop-002",
        "target_artifact": "artifacts/doc.md",
        "change_type": "invalid_type",  # Invalid
        "diff": "content",
        "rationale": "test",
    }

    response = client.post(
        f"/api/v1/projects/{project_key}/proposals", json=invalid_proposal
    )

    assert response.status_code == 422  # Validation error


# ============================================================================
# GET /api/v1/projects/{key}/proposals - List Proposals
# ============================================================================


def test_list_proposals_empty(client, test_project):
    """Test listing proposals for project with no proposals."""
    project_key = test_project["key"]
    response = client.get(f"/api/v1/projects/{project_key}/proposals")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_proposals_multiple(client, test_project):
    """Test listing multiple proposals."""
    project_key = test_project["key"]

    # Create 3 proposals
    for i in range(1, 4):
        proposal = {
            "id": f"prop-00{i}",
            "target_artifact": f"artifacts/doc{i}.md",
            "change_type": "create",
            "diff": f"Content {i}",
            "rationale": f"Reason {i}",
        }
        response = client.post(
            f"/api/v1/projects/{project_key}/proposals", json=proposal
        )
        assert response.status_code == 201

    # List all proposals
    response = client.get(f"/api/v1/projects/{project_key}/proposals")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(p["status"] == "pending" for p in data)


def test_list_proposals_with_status_filter(
    client, test_project, sample_proposal_create
):
    """Test listing proposals with status filter."""
    project_key = test_project["key"]

    # Create and apply one proposal
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals", json=sample_proposal_create
    )
    assert response.status_code == 201

    # Create second proposal (keep pending)
    proposal2 = sample_proposal_create.copy()
    proposal2["id"] = "prop-002"
    response = client.post(f"/api/v1/projects/{project_key}/proposals", json=proposal2)
    assert response.status_code == 201

    # Apply first proposal
    response = client.post(f"/api/v1/projects/{project_key}/proposals/prop-001/apply")
    assert response.status_code == 200

    # List only pending proposals
    response = client.get(
        f"/api/v1/projects/{project_key}/proposals?status_filter=pending"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "prop-002"


# ============================================================================
# GET /api/v1/projects/{key}/proposals/{id} - Get Proposal
# ============================================================================


def test_get_proposal_success(client, test_project, sample_proposal_create):
    """Test getting a specific proposal."""
    project_key = test_project["key"]

    # Create proposal
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals", json=sample_proposal_create
    )
    assert response.status_code == 201

    # Get proposal
    response = client.get(f"/api/v1/projects/{project_key}/proposals/prop-001")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "prop-001"
    assert data["status"] == "pending"


def test_get_proposal_not_found(client, test_project):
    """Test getting non-existent proposal returns 404."""
    project_key = test_project["key"]
    response = client.get(f"/api/v1/projects/{project_key}/proposals/nonexistent")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ============================================================================
# POST /api/v1/projects/{key}/proposals/{id}/apply - Apply Proposal
# ============================================================================


def test_apply_proposal_create_success(client, test_project, sample_proposal_create):
    """Test applying a CREATE proposal."""
    project_key = test_project["key"]

    # Create proposal
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals", json=sample_proposal_create
    )
    assert response.status_code == 201

    # Apply proposal
    response = client.post(f"/api/v1/projects/{project_key}/proposals/prop-001/apply")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["proposal_id"] == "prop-001"
    assert data["artifact"] == "artifacts/new-doc.md"
    assert data["change_type"] == "create"

    # Verify artifact was created
    git_manager = app.state.git_manager
    content = git_manager.read_file(project_key, "artifacts/new-doc.md")
    assert content == "# New Document\n\nThis is a new artifact."


def test_apply_proposal_update_success(client, test_project, sample_artifact):
    """Test applying an UPDATE proposal."""
    project_key = test_project["key"]

    # Create UPDATE proposal
    proposal = {
        "id": "prop-update",
        "target_artifact": sample_artifact["path"],
        "change_type": "update",
        "diff": "--- a/requirements.md\n+++ b/requirements.md\n@@ -1,3 +1,4 @@\n # Requirements\n \n - REQ-001: Initial requirement\n+- REQ-002: New requirement\n",
        "rationale": "Adding new requirement",
    }

    response = client.post(f"/api/v1/projects/{project_key}/proposals", json=proposal)
    assert response.status_code == 201

    # Apply proposal
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals/prop-update/apply"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["change_type"] == "update"


def test_apply_proposal_not_found(client, test_project):
    """Test applying non-existent proposal returns 404."""
    project_key = test_project["key"]
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals/nonexistent/apply"
    )

    assert response.status_code == 404


def test_apply_proposal_already_applied(client, test_project, sample_proposal_create):
    """Test applying already-applied proposal returns 409."""
    project_key = test_project["key"]

    # Create and apply proposal
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals", json=sample_proposal_create
    )
    assert response.status_code == 201

    response = client.post(f"/api/v1/projects/{project_key}/proposals/prop-001/apply")
    assert response.status_code == 200

    # Try to apply again
    response = client.post(f"/api/v1/projects/{project_key}/proposals/prop-001/apply")

    assert response.status_code == 409
    assert "already" in response.json()["detail"].lower()


# ============================================================================
# POST /api/v1/projects/{key}/proposals/{id}/reject - Reject Proposal
# ============================================================================


def test_reject_proposal_success(client, test_project, sample_proposal_create):
    """Test rejecting a proposal."""
    project_key = test_project["key"]

    # Create proposal
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals", json=sample_proposal_create
    )
    assert response.status_code == 201

    # Reject proposal
    reject_data = {"reason": "Changes not approved by stakeholders"}
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals/prop-001/reject", json=reject_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["proposal_id"] == "prop-001"
    assert data["reason"] == "Changes not approved by stakeholders"

    # Verify proposal status updated
    response = client.get(f"/api/v1/projects/{project_key}/proposals/prop-001")
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["status"] == "rejected"


def test_reject_proposal_not_found(client, test_project):
    """Test rejecting non-existent proposal returns 404."""
    project_key = test_project["key"]
    reject_data = {"reason": "test"}
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals/nonexistent/reject",
        json=reject_data,
    )

    assert response.status_code == 404


def test_reject_proposal_already_rejected(client, test_project, sample_proposal_create):
    """Test rejecting already-rejected proposal returns 409."""
    project_key = test_project["key"]

    # Create and reject proposal
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals", json=sample_proposal_create
    )
    assert response.status_code == 201

    reject_data = {"reason": "First rejection"}
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals/prop-001/reject", json=reject_data
    )
    assert response.status_code == 200

    # Try to reject again
    reject_data2 = {"reason": "Second rejection"}
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals/prop-001/reject", json=reject_data2
    )

    assert response.status_code == 409
    assert "already" in response.json()["detail"].lower()


def test_reject_applied_proposal_returns_409(
    client, test_project, sample_proposal_create
):
    """Test rejecting an already-applied proposal returns 409."""
    project_key = test_project["key"]

    # Create and apply proposal
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals", json=sample_proposal_create
    )
    assert response.status_code == 201

    response = client.post(f"/api/v1/projects/{project_key}/proposals/prop-001/apply")
    assert response.status_code == 200

    # Try to reject
    reject_data = {"reason": "Too late"}
    response = client.post(
        f"/api/v1/projects/{project_key}/proposals/prop-001/reject", json=reject_data
    )

    assert response.status_code == 409
