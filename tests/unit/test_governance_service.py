"""
Unit tests for Governance Service.
"""
import pytest
import tempfile
import shutil
from apps.api.services.governance_service import GovernanceService
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
def governance_service():
    """Create a GovernanceService instance."""
    return GovernanceService()


@pytest.fixture
def test_project(git_manager):
    """Create a test project."""
    project_key = "TEST001"
    project_data = {"key": project_key, "name": "Test Project"}
    git_manager.create_project(project_key, project_data)
    return project_key


class TestGovernanceMetadata:
    """Test governance metadata operations."""

    def test_create_governance_metadata(self, governance_service, git_manager, test_project):
        """Test creating governance metadata."""
        metadata = {
            "objectives": ["Objective 1", "Objective 2"],
            "scope": "Test scope",
            "stakeholders": [
                {"name": "John Doe", "role": "PM", "responsibilities": "Delivery"}
            ],
            "decision_rights": {"architecture": "Tech Lead"},
            "stage_gates": [{"name": "Gate 1", "status": "pending"}],
            "approvals": [{"type": "budget", "approver": "CFO"}],
            "created_by": "test_user",
        }

        result = governance_service.create_governance_metadata(
            test_project, metadata, git_manager
        )

        assert result["objectives"] == ["Objective 1", "Objective 2"]
        assert result["scope"] == "Test scope"
        assert len(result["stakeholders"]) == 1
        assert result["created_by"] == "test_user"
        assert "created_at" in result
        assert "updated_at" in result

    def test_get_governance_metadata(self, governance_service, git_manager, test_project):
        """Test retrieving governance metadata."""
        # Create metadata first
        metadata = {
            "objectives": ["Test Objective"],
            "scope": "Test scope",
            "created_by": "test_user",
        }
        governance_service.create_governance_metadata(test_project, metadata, git_manager)

        # Retrieve metadata
        result = governance_service.get_governance_metadata(test_project, git_manager)

        assert result is not None
        assert result["objectives"] == ["Test Objective"]
        assert result["scope"] == "Test scope"

    def test_update_governance_metadata(self, governance_service, git_manager, test_project):
        """Test updating governance metadata."""
        # Create initial metadata
        metadata = {
            "objectives": ["Initial Objective"],
            "scope": "Initial scope",
            "created_by": "test_user",
        }
        governance_service.create_governance_metadata(test_project, metadata, git_manager)

        # Update metadata
        updates = {
            "objectives": ["Updated Objective 1", "Updated Objective 2"],
            "scope": "Updated scope",
            "updated_by": "another_user",
        }
        result = governance_service.update_governance_metadata(
            test_project, updates, git_manager
        )

        assert result["objectives"] == ["Updated Objective 1", "Updated Objective 2"]
        assert result["scope"] == "Updated scope"
        assert result["updated_by"] == "another_user"
        assert result["created_by"] == "test_user"  # Should not change

    def test_get_nonexistent_metadata(self, governance_service, git_manager, test_project):
        """Test retrieving metadata that doesn't exist."""
        result = governance_service.get_governance_metadata(test_project, git_manager)
        assert result is None


class TestDecisionLog:
    """Test decision log operations."""

    def test_create_decision(self, governance_service, git_manager, test_project):
        """Test creating a decision log entry."""
        decision_data = {
            "title": "Test Decision",
            "description": "Test decision description",
            "decision_maker": "CTO",
            "rationale": "Test rationale",
            "impact": "Test impact",
            "status": "approved",
            "created_by": "test_user",
        }

        result = governance_service.create_decision(
            test_project, decision_data, git_manager
        )

        assert result["title"] == "Test Decision"
        assert result["description"] == "Test decision description"
        assert result["decision_maker"] == "CTO"
        assert result["status"] == "approved"
        assert "id" in result
        assert "created_at" in result

    def test_get_decisions(self, governance_service, git_manager, test_project):
        """Test retrieving all decisions."""
        # Create multiple decisions
        for i in range(3):
            decision_data = {
                "title": f"Decision {i}",
                "description": f"Description {i}",
                "decision_maker": "CTO",
                "created_by": "test_user",
            }
            governance_service.create_decision(test_project, decision_data, git_manager)

        # Retrieve all decisions
        decisions = governance_service.get_decisions(test_project, git_manager)

        assert len(decisions) == 3
        assert decisions[0]["title"] == "Decision 0"
        assert decisions[2]["title"] == "Decision 2"

    def test_get_decision_by_id(self, governance_service, git_manager, test_project):
        """Test retrieving a specific decision."""
        # Create a decision
        decision_data = {
            "title": "Specific Decision",
            "description": "Test description",
            "decision_maker": "CTO",
            "created_by": "test_user",
        }
        created = governance_service.create_decision(
            test_project, decision_data, git_manager
        )

        # Retrieve by ID
        result = governance_service.get_decision(
            test_project, created["id"], git_manager
        )

        assert result is not None
        assert result["id"] == created["id"]
        assert result["title"] == "Specific Decision"

    def test_get_nonexistent_decision(self, governance_service, git_manager, test_project):
        """Test retrieving a decision that doesn't exist."""
        result = governance_service.get_decision(
            test_project, "nonexistent-id", git_manager
        )
        assert result is None

    def test_link_decision_to_raid(self, governance_service, git_manager, test_project):
        """Test linking a decision to a RAID item."""
        # Create a decision
        decision_data = {
            "title": "Test Decision",
            "description": "Test description",
            "decision_maker": "CTO",
            "created_by": "test_user",
        }
        decision = governance_service.create_decision(
            test_project, decision_data, git_manager
        )

        # Link to a RAID item
        raid_id = "test-raid-id"
        result = governance_service.link_decision_to_raid(
            test_project, decision["id"], raid_id, git_manager
        )

        assert result is True

        # Verify the link
        updated_decision = governance_service.get_decision(
            test_project, decision["id"], git_manager
        )
        assert raid_id in updated_decision["linked_raid_ids"]


class TestGovernanceGitIntegration:
    """Test Git integration for governance operations."""

    def test_governance_metadata_creates_git_commit(
        self, governance_service, git_manager, test_project
    ):
        """Test that creating governance metadata creates a git commit."""
        # Get initial commit count
        initial_commits = len(list(git_manager.repo.iter_commits()))

        # Create governance metadata
        metadata = {"objectives": ["Test"], "created_by": "test_user"}
        governance_service.create_governance_metadata(test_project, metadata, git_manager)

        # Verify a commit was created
        final_commits = len(list(git_manager.repo.iter_commits()))
        assert final_commits == initial_commits + 1

    def test_decision_creates_git_commit(
        self, governance_service, git_manager, test_project
    ):
        """Test that creating a decision creates a git commit."""
        # Get initial commit count
        initial_commits = len(list(git_manager.repo.iter_commits()))

        # Create a decision
        decision_data = {
            "title": "Test Decision",
            "description": "Test",
            "decision_maker": "CTO",
            "created_by": "test_user",
        }
        governance_service.create_decision(test_project, decision_data, git_manager)

        # Verify a commit was created
        final_commits = len(list(git_manager.repo.iter_commits()))
        assert final_commits == initial_commits + 1
