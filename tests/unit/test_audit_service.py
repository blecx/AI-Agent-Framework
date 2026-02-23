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
    git_manager.create_project(
        project_key, {"key": project_key, "name": "Test Project"}
    )
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
        audit_service.log_audit_event(
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
        audit_service.log_audit_event(
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


class TestEnhancedAuditRules:
    """Test enhanced audit rules (cross-artifact validation)."""

    def test_audit_issue_order_is_deterministic(
        self, audit_service, git_manager, test_project
    ):
        """Issue ordering should be stable for identical project inputs."""
        project_path = git_manager.get_project_path(test_project)
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        metadata = {
            "key": test_project,
            "name": "Test Project",
            "description": "Deterministic ordering test",
            "start_date": "2026-03-01",
            "end_date": "2026-06-01",
        }
        (project_path / "metadata.json").write_text(json.dumps(metadata))

        pmp_data = {
            "deliverables": [{"id": "D-001", "name": "Deliverable"}],
            "milestones": [
                {
                    "id": "M-002",
                    "name": "Late milestone",
                    "due_date": "2026-07-01",
                },
                {
                    "id": "M-001",
                    "name": "Early milestone",
                    "due_date": "2026-02-01",
                },
            ],
        }
        (artifacts_path / "pmp.json").write_text(json.dumps(pmp_data))

        raid_data = {
            "items": [
                {
                    "id": "R-002",
                    "type": "risk",
                    "related_deliverables": ["D-999"],
                },
                {
                    "id": "R-001",
                    "type": "risk",
                    "related_deliverables": ["D-998"],
                },
            ]
        }
        (artifacts_path / "raid.json").write_text(json.dumps(raid_data))

        first = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["cross_reference", "date_consistency"],
        )
        second = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["cross_reference", "date_consistency"],
        )

        first_messages = [issue["message"] for issue in first["issues"]]
        second_messages = [issue["message"] for issue in second["issues"]]

        assert first_messages == second_messages

    def test_run_audit_rules_no_issues(self, audit_service, git_manager, test_project):
        """Test running audit rules on a well-formed project."""
        # Create minimal valid artifacts
        project_path = git_manager.get_project_path(test_project)

        # Create artifacts directory
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        # Create minimal valid RAID
        raid_data = {"items": []}
        (artifacts_path / "raid.json").write_text(json.dumps(raid_data))

        # Run audit
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
        )

        assert "issues" in result
        assert "completeness_score" in result
        assert "rule_violations" in result
        assert isinstance(result["issues"], list)

    def test_cross_reference_validation(self, audit_service, git_manager, test_project):
        """Test cross-reference validation rule."""
        project_path = git_manager.get_project_path(test_project)
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        # Create RAID with invalid cross-reference
        raid_data = {
            "items": [
                {
                    "id": "R-001",
                    "type": "risk",
                    "related_deliverables": ["D-001"],  # Non-existent
                }
            ]
        }
        (artifacts_path / "raid.json").write_text(json.dumps(raid_data))

        # Run audit
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["cross_reference"],
        )

        assert result["total_issues"] > 0
        assert any(issue["rule"] == "cross_reference" for issue in result["issues"])

    def test_date_consistency_validation(
        self, audit_service, git_manager, test_project
    ):
        """Test date consistency rule."""
        project_path = git_manager.get_project_path(test_project)

        # Create metadata with project dates
        metadata = {
            "key": test_project,
            "name": "Test",
            "start_date": "2026-03-01",
            "end_date": "2026-06-01",
        }
        (project_path / "metadata.json").write_text(json.dumps(metadata))

        # Create artifacts with invalid milestone date
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        pmp_data = {
            "milestones": [
                {
                    "id": "M-001",
                    "name": "Kickoff",
                    "due_date": "2026-02-01",  # Before project start
                }
            ]
        }
        (artifacts_path / "pmp.json").write_text(json.dumps(pmp_data))

        # Run audit
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["date_consistency"],
        )

        assert result["total_issues"] > 0
        assert any(issue["rule"] == "date_consistency" for issue in result["issues"])

    def test_dependency_cycle_detection(self, audit_service, git_manager, test_project):
        """Test dependency cycle detection rule."""
        project_path = git_manager.get_project_path(test_project)
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        # Create PMP with circular dependencies
        pmp_data = {
            "deliverables": [
                {"id": "D-001", "name": "A", "dependencies": ["D-002"]},
                {"id": "D-002", "name": "B", "dependencies": ["D-003"]},
                {"id": "D-003", "name": "C", "dependencies": ["D-001"]},  # Cycle!
            ]
        }
        (artifacts_path / "pmp.json").write_text(json.dumps(pmp_data))

        # Run audit
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["dependency_cycles"],
        )

        assert result["total_issues"] > 0
        assert any(issue["rule"] == "dependency_cycles" for issue in result["issues"])

    def test_completeness_scoring(self, audit_service, git_manager, test_project):
        """Test completeness scoring calculation."""
        project_path = git_manager.get_project_path(test_project)

        # Create minimal metadata
        metadata = {
            "key": test_project,
            "name": "Test Project",
            "description": "A test project",
            "start_date": "2026-03-01",
        }
        (project_path / "metadata.json").write_text(json.dumps(metadata))

        # Calculate completeness
        score = audit_service._calculate_completeness_score(test_project, git_manager)

        assert 0 <= score <= 100
        assert isinstance(score, float)

    def test_audit_history_save_and_retrieve(
        self, audit_service, git_manager, test_project
    ):
        """Test saving and retrieving audit history."""
        # Run audit to generate result
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
        )

        # Save to history
        audit_service.save_audit_history(test_project, result, git_manager)

        # Retrieve history
        history = audit_service.get_audit_history(
            project_key=test_project,
            git_manager=git_manager,
        )

        assert len(history) > 0
        assert "timestamp" in history[0]
        assert "total_issues" in history[0]
        assert "completeness_score" in history[0]
