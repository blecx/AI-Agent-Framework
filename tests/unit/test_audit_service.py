"""
Unit tests for AuditService.
"""
import pytest
import tempfile
import shutil
import json

from apps.api.services.audit_service import AuditService
from apps.api.services.git_manager import GitManager


@pytest.fixture(scope="function")
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def git_manager(temp_project_dir):
    """Create a git manager with temporary directory."""
    manager = GitManager(temp_project_dir)
    manager.ensure_repository()
    return manager


@pytest.fixture(scope="function")
def audit_service():
    """Create an audit service instance."""
    return AuditService()


@pytest.fixture
def test_project(git_manager):
    """Create a test project."""
    project_key = "TEST001"
    git_manager.create_project(project_key, {"key": project_key, "name": "Test Project"})
    return project_key


class TestAuditEventLogging:
    """Test audit event logging."""

    def test_log_audit_event_basic(self, audit_service, git_manager, test_project):
        """Test logging a basic audit event."""
        event = audit_service.log_audit_event(
            project_key=test_project,
            event_type="test_event",
            actor="test_user",
            payload_summary={"action": "test"},
            git_manager=git_manager,
        )

        assert "event_id" in event
        assert event["event_type"] == "test_event"
        assert event["actor"] == "test_user"
        assert event["project_key"] == test_project
        assert event["payload_summary"] == {"action": "test"}
        assert "timestamp" in event

    def test_log_audit_event_with_correlation_id(
        self, audit_service, git_manager, test_project
    ):
        """Test logging event with correlation ID."""
        correlation_id = "req-12345"
        event = audit_service.log_audit_event(
            project_key=test_project,
            event_type="test_event",
            actor="test_user",
            git_manager=git_manager,
            correlation_id=correlation_id,
        )

        assert event["correlation_id"] == correlation_id

    def test_log_audit_event_with_resource_hash(
        self, audit_service, git_manager, test_project
    ):
        """Test logging event with resource hash."""
        resource_hash = "abc123def456"
        event = audit_service.log_audit_event(
            project_key=test_project,
            event_type="test_event",
            actor="test_user",
            git_manager=git_manager,
            resource_hash=resource_hash,
        )

        assert event["resource_hash"] == resource_hash

    def test_log_multiple_events(self, audit_service, git_manager, test_project):
        """Test logging multiple events appends to NDJSON file."""
        # Log multiple events
        for i in range(3):
            audit_service.log_audit_event(
                project_key=test_project,
                event_type=f"event_{i}",
                actor="test_user",
                git_manager=git_manager,
            )

        # Verify all events are in the file
        events_path = (
            git_manager.get_project_path(test_project) / "events" / "audit.ndjson"
        )
        with events_path.open("r") as f:
            lines = f.readlines()

        assert len(lines) == 3
        for i, line in enumerate(lines):
            event = json.loads(line)
            assert event["event_type"] == f"event_{i}"


class TestAuditEventRetrieval:
    """Test audit event retrieval."""

    def test_get_audit_events_empty(self, audit_service, git_manager, test_project):
        """Test retrieving events when none exist."""
        result = audit_service.get_audit_events(
            project_key=test_project, git_manager=git_manager
        )

        assert result["events"] == []
        assert result["total"] == 0
        assert result["limit"] == 100
        assert result["offset"] == 0

    def test_get_audit_events_basic(self, audit_service, git_manager, test_project):
        """Test retrieving all events."""
        # Log some events
        for i in range(3):
            audit_service.log_audit_event(
                project_key=test_project,
                event_type="test_event",
                actor="test_user",
                git_manager=git_manager,
            )

        result = audit_service.get_audit_events(
            project_key=test_project, git_manager=git_manager
        )

        assert len(result["events"]) == 3
        assert result["total"] == 3

    def test_get_audit_events_with_pagination(
        self, audit_service, git_manager, test_project
    ):
        """Test pagination of audit events."""
        # Log 10 events
        for i in range(10):
            audit_service.log_audit_event(
                project_key=test_project,
                event_type="test_event",
                actor="test_user",
                git_manager=git_manager,
            )

        # Get first page
        result1 = audit_service.get_audit_events(
            project_key=test_project, git_manager=git_manager, limit=5, offset=0
        )

        assert len(result1["events"]) == 5
        assert result1["total"] == 10
        assert result1["limit"] == 5
        assert result1["offset"] == 0

        # Get second page
        result2 = audit_service.get_audit_events(
            project_key=test_project, git_manager=git_manager, limit=5, offset=5
        )

        assert len(result2["events"]) == 5
        assert result2["total"] == 10
        assert result2["offset"] == 5


class TestAuditEventFiltering:
    """Test audit event filtering."""

    def test_filter_by_event_type(self, audit_service, git_manager, test_project):
        """Test filtering events by type."""
        # Log different event types
        audit_service.log_audit_event(
            project_key=test_project,
            event_type="type_a",
            actor="user1",
            git_manager=git_manager,
        )
        audit_service.log_audit_event(
            project_key=test_project,
            event_type="type_b",
            actor="user2",
            git_manager=git_manager,
        )
        audit_service.log_audit_event(
            project_key=test_project,
            event_type="type_a",
            actor="user3",
            git_manager=git_manager,
        )

        # Filter by type_a
        result = audit_service.get_audit_events(
            project_key=test_project, git_manager=git_manager, event_type="type_a"
        )

        assert len(result["events"]) == 2
        assert result["total"] == 2
        assert all(e["event_type"] == "type_a" for e in result["events"])
        assert result["filtered_by"]["event_type"] == "type_a"

    def test_filter_by_actor(self, audit_service, git_manager, test_project):
        """Test filtering events by actor."""
        # Log events from different actors
        audit_service.log_audit_event(
            project_key=test_project,
            event_type="test_event",
            actor="user1",
            git_manager=git_manager,
        )
        audit_service.log_audit_event(
            project_key=test_project,
            event_type="test_event",
            actor="user2",
            git_manager=git_manager,
        )
        audit_service.log_audit_event(
            project_key=test_project,
            event_type="test_event",
            actor="user1",
            git_manager=git_manager,
        )

        # Filter by user1
        result = audit_service.get_audit_events(
            project_key=test_project, git_manager=git_manager, actor="user1"
        )

        assert len(result["events"]) == 2
        assert result["total"] == 2
        assert all(e["actor"] == "user1" for e in result["events"])
        assert result["filtered_by"]["actor"] == "user1"

    def test_filter_by_time_range(self, audit_service, git_manager, test_project):
        """Test filtering events by time range."""
        # Log events
        event1 = audit_service.log_audit_event(
            project_key=test_project,
            event_type="test_event",
            actor="user1",
            git_manager=git_manager,
        )
        event2 = audit_service.log_audit_event(
            project_key=test_project,
            event_type="test_event",
            actor="user2",
            git_manager=git_manager,
        )
        event3 = audit_service.log_audit_event(
            project_key=test_project,
            event_type="test_event",
            actor="user3",
            git_manager=git_manager,
        )

        # Filter from event2's timestamp
        result = audit_service.get_audit_events(
            project_key=test_project,
            git_manager=git_manager,
            since=event2["timestamp"],
        )

        assert len(result["events"]) == 2  # event2 and event3
        assert result["filtered_by"]["since"] == event2["timestamp"]

        # Filter until event2's timestamp
        result = audit_service.get_audit_events(
            project_key=test_project,
            git_manager=git_manager,
            until=event2["timestamp"],
        )

        assert len(result["events"]) == 2  # event1 and event2
        assert result["filtered_by"]["until"] == event2["timestamp"]

    def test_filter_multiple_criteria(self, audit_service, git_manager, test_project):
        """Test filtering with multiple criteria."""
        # Log various events
        audit_service.log_audit_event(
            project_key=test_project,
            event_type="type_a",
            actor="user1",
            git_manager=git_manager,
        )
        audit_service.log_audit_event(
            project_key=test_project,
            event_type="type_b",
            actor="user1",
            git_manager=git_manager,
        )
        audit_service.log_audit_event(
            project_key=test_project,
            event_type="type_a",
            actor="user2",
            git_manager=git_manager,
        )

        # Filter by type_a AND user1
        result = audit_service.get_audit_events(
            project_key=test_project,
            git_manager=git_manager,
            event_type="type_a",
            actor="user1",
        )

        assert len(result["events"]) == 1
        assert result["total"] == 1
        assert result["events"][0]["event_type"] == "type_a"
        assert result["events"][0]["actor"] == "user1"


class TestResourceHashing:
    """Test resource hash computation."""

    def test_compute_resource_hash(self, audit_service):
        """Test computing SHA-256 hash of resource."""
        content = "test content"
        hash1 = audit_service.compute_resource_hash(content)

        # Should be deterministic
        hash2 = audit_service.compute_resource_hash(content)
        assert hash1 == hash2

        # Should be SHA-256 (64 hex characters)
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)

        # Different content should produce different hash
        hash3 = audit_service.compute_resource_hash("different content")
        assert hash1 != hash3
