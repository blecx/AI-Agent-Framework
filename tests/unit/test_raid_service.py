"""
Unit tests for RAID Service.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from apps.api.services.raid_service import RAIDService
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
def raid_service():
    """Create a RAIDService instance."""
    return RAIDService()


@pytest.fixture
def test_project(git_manager):
    """Create a test project."""
    project_key = "TEST001"
    project_data = {"key": project_key, "name": "Test Project"}
    git_manager.create_project(project_key, project_data)
    return project_key


class TestRAIDItemCRUD:
    """Test RAID item CRUD operations."""

    def test_create_raid_item(self, raid_service, git_manager, test_project):
        """Test creating a RAID item."""
        item_data = {
            "type": "risk",
            "title": "Test Risk",
            "description": "Test risk description",
            "owner": "John Doe",
            "priority": "high",
            "impact": "high",
            "likelihood": "possible",
            "mitigation_plan": "Test mitigation",
            "next_actions": ["Action 1", "Action 2"],
            "created_by": "test_user",
        }

        result = raid_service.create_raid_item(test_project, item_data, git_manager)

        assert result["type"] == "risk"
        assert result["title"] == "Test Risk"
        assert result["owner"] == "John Doe"
        assert result["priority"] == "high"
        assert result["impact"] == "high"
        assert result["likelihood"] == "possible"
        assert "id" in result
        assert "created_at" in result
        assert len(result["next_actions"]) == 2

    def test_get_raid_items(self, raid_service, git_manager, test_project):
        """Test retrieving all RAID items."""
        # Create multiple items
        for i in range(3):
            item_data = {
                "type": "risk" if i % 2 == 0 else "issue",
                "title": f"Item {i}",
                "description": f"Description {i}",
                "owner": "Test Owner",
                "created_by": "test_user",
            }
            raid_service.create_raid_item(test_project, item_data, git_manager)

        # Retrieve all items
        items = raid_service.get_raid_items(test_project, git_manager)

        assert len(items) == 3
        assert items[0]["title"] == "Item 0"
        assert items[2]["title"] == "Item 2"

    def test_get_raid_item_by_id(self, raid_service, git_manager, test_project):
        """Test retrieving a specific RAID item."""
        # Create an item
        item_data = {
            "type": "issue",
            "title": "Specific Issue",
            "description": "Test description",
            "owner": "Test Owner",
            "created_by": "test_user",
        }
        created = raid_service.create_raid_item(test_project, item_data, git_manager)

        # Retrieve by ID
        result = raid_service.get_raid_item(test_project, created["id"], git_manager)

        assert result is not None
        assert result["id"] == created["id"]
        assert result["title"] == "Specific Issue"

    def test_update_raid_item(self, raid_service, git_manager, test_project):
        """Test updating a RAID item."""
        # Create an item
        item_data = {
            "type": "risk",
            "title": "Original Title",
            "description": "Original description",
            "owner": "Original Owner",
            "status": "open",
            "created_by": "test_user",
        }
        created = raid_service.create_raid_item(test_project, item_data, git_manager)

        # Update the item
        updates = {
            "title": "Updated Title",
            "status": "in_progress",
            "next_actions": ["New Action 1", "New Action 2"],
            "updated_by": "another_user",
        }
        result = raid_service.update_raid_item(
            test_project, created["id"], updates, git_manager
        )

        assert result["title"] == "Updated Title"
        assert result["status"] == "in_progress"
        assert len(result["next_actions"]) == 2
        assert result["updated_by"] == "another_user"
        assert result["owner"] == "Original Owner"  # Unchanged
        assert result["created_by"] == "test_user"  # Unchanged

    def test_delete_raid_item(self, raid_service, git_manager, test_project):
        """Test deleting a RAID item."""
        # Create an item
        item_data = {
            "type": "issue",
            "title": "To Be Deleted",
            "description": "Test description",
            "owner": "Test Owner",
            "created_by": "test_user",
        }
        created = raid_service.create_raid_item(test_project, item_data, git_manager)

        # Delete the item
        result = raid_service.delete_raid_item(test_project, created["id"], git_manager)
        assert result is True

        # Verify it's gone
        items = raid_service.get_raid_items(test_project, git_manager)
        assert len(items) == 0

    def test_delete_nonexistent_item(self, raid_service, git_manager, test_project):
        """Test deleting an item that doesn't exist."""
        result = raid_service.delete_raid_item(
            test_project, "nonexistent-id", git_manager
        )
        assert result is False


class TestRAIDItemFiltering:
    """Test RAID item filtering."""

    @pytest.fixture
    def sample_items(self, raid_service, git_manager, test_project):
        """Create sample RAID items for filtering tests."""
        items_data = [
            {
                "type": "risk",
                "title": "Risk 1",
                "description": "Risk 1",
                "owner": "Alice",
                "priority": "high",
                "status": "open",
            },
            {
                "type": "issue",
                "title": "Issue 1",
                "description": "Issue 1",
                "owner": "Bob",
                "priority": "critical",
                "status": "in_progress",
            },
            {
                "type": "risk",
                "title": "Risk 2",
                "description": "Risk 2",
                "owner": "Alice",
                "priority": "medium",
                "status": "closed",
            },
            {
                "type": "dependency",
                "title": "Dependency 1",
                "description": "Dependency 1",
                "owner": "Charlie",
                "priority": "low",
                "status": "open",
            },
        ]

        for item_data in items_data:
            item_data["created_by"] = "test_user"
            raid_service.create_raid_item(test_project, item_data, git_manager)

        return raid_service.get_raid_items(test_project, git_manager)

    def test_filter_by_type(self, raid_service, sample_items):
        """Test filtering RAID items by type."""
        filtered = raid_service.filter_raid_items(sample_items, raid_type="risk")
        assert len(filtered) == 2
        assert all(item["type"] == "risk" for item in filtered)

    def test_filter_by_status(self, raid_service, sample_items):
        """Test filtering RAID items by status."""
        filtered = raid_service.filter_raid_items(sample_items, status="open")
        assert len(filtered) == 2
        assert all(item["status"] == "open" for item in filtered)

    def test_filter_by_owner(self, raid_service, sample_items):
        """Test filtering RAID items by owner."""
        filtered = raid_service.filter_raid_items(sample_items, owner="Alice")
        assert len(filtered) == 2
        assert all(item["owner"] == "Alice" for item in filtered)

    def test_filter_by_priority(self, raid_service, sample_items):
        """Test filtering RAID items by priority."""
        filtered = raid_service.filter_raid_items(sample_items, priority="high")
        assert len(filtered) == 1
        assert filtered[0]["priority"] == "high"

    def test_filter_multiple_criteria(self, raid_service, sample_items):
        """Test filtering with multiple criteria."""
        filtered = raid_service.filter_raid_items(
            sample_items, raid_type="risk", owner="Alice", status="open"
        )
        assert len(filtered) == 1
        assert filtered[0]["type"] == "risk"
        assert filtered[0]["owner"] == "Alice"
        assert filtered[0]["status"] == "open"


class TestRAIDTraceability:
    """Test RAID traceability features."""

    def test_link_raid_to_decision(self, raid_service, git_manager, test_project):
        """Test linking a RAID item to a decision."""
        # Create a RAID item
        item_data = {
            "type": "risk",
            "title": "Test Risk",
            "description": "Test description",
            "owner": "Test Owner",
            "created_by": "test_user",
        }
        raid_item = raid_service.create_raid_item(test_project, item_data, git_manager)

        # Link to a decision
        decision_id = "test-decision-id"
        result = raid_service.link_raid_to_decision(
            test_project, raid_item["id"], decision_id, git_manager
        )

        assert result is True

        # Verify the link
        updated_item = raid_service.get_raid_item(
            test_project, raid_item["id"], git_manager
        )
        assert decision_id in updated_item["linked_decisions"]

    def test_get_raid_items_by_decision(self, raid_service, git_manager, test_project):
        """Test retrieving RAID items linked to a specific decision."""
        decision_id = "test-decision-id"

        # Create multiple RAID items, some linked to the decision
        for i in range(3):
            item_data = {
                "type": "risk",
                "title": f"Risk {i}",
                "description": f"Description {i}",
                "owner": "Test Owner",
                "created_by": "test_user",
            }
            if i < 2:  # Link first two items to the decision
                item_data["linked_decisions"] = [decision_id]

            raid_service.create_raid_item(test_project, item_data, git_manager)

        # Retrieve items by decision
        items = raid_service.get_raid_items_by_decision(
            test_project, decision_id, git_manager
        )

        assert len(items) == 2
        assert all(decision_id in item["linked_decisions"] for item in items)


class TestRAIDGitIntegration:
    """Test Git integration for RAID operations."""

    def test_create_raid_item_creates_git_commit(
        self, raid_service, git_manager, test_project
    ):
        """Test that creating a RAID item creates a git commit."""
        # Get initial commit count
        initial_commits = len(list(git_manager.repo.iter_commits()))

        # Create a RAID item
        item_data = {
            "type": "risk",
            "title": "Test Risk",
            "description": "Test",
            "owner": "Test Owner",
            "created_by": "test_user",
        }
        raid_service.create_raid_item(test_project, item_data, git_manager)

        # Verify a commit was created
        final_commits = len(list(git_manager.repo.iter_commits()))
        assert final_commits == initial_commits + 1

    def test_update_raid_item_creates_git_commit(
        self, raid_service, git_manager, test_project
    ):
        """Test that updating a RAID item creates a git commit."""
        # Create a RAID item
        item_data = {
            "type": "risk",
            "title": "Test Risk",
            "description": "Test",
            "owner": "Test Owner",
            "created_by": "test_user",
        }
        created = raid_service.create_raid_item(test_project, item_data, git_manager)

        # Get commit count after creation
        initial_commits = len(list(git_manager.repo.iter_commits()))

        # Update the item
        updates = {"status": "in_progress", "updated_by": "test_user"}
        raid_service.update_raid_item(test_project, created["id"], updates, git_manager)

        # Verify a commit was created
        final_commits = len(list(git_manager.repo.iter_commits()))
        assert final_commits == initial_commits + 1
