"""
Unit tests for WorkflowService.
"""

import pytest
import tempfile
import shutil

from apps.api.services.workflow_service import WorkflowService, VALID_TRANSITIONS
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
def workflow_service():
    """Create a workflow service instance."""
    return WorkflowService()


@pytest.fixture
def test_project(git_manager):
    """Create a test project."""
    project_key = "TEST001"
    git_manager.create_project(
        project_key, {"key": project_key, "name": "Test Project"}
    )
    return project_key


class TestWorkflowStateInitialization:
    """Test workflow state initialization."""

    def test_initialize_workflow_state(
        self, workflow_service, git_manager, test_project
    ):
        """Test initializing workflow state for a new project."""
        state = workflow_service.initialize_workflow_state(test_project, git_manager)

        assert state["current_state"] == "initiating"
        assert state["previous_state"] is None
        assert state["transition_history"] == []
        assert "updated_at" in state
        assert state["updated_by"] == "system"

    def test_get_workflow_state_returns_default_if_not_exists(
        self, workflow_service, git_manager, test_project
    ):
        """Test getting workflow state returns default if not initialized."""
        state = workflow_service.get_workflow_state(test_project, git_manager)

        assert state["current_state"] == "initiating"
        assert state["previous_state"] is None
        assert state["transition_history"] == []

    def test_get_workflow_state_returns_existing(
        self, workflow_service, git_manager, test_project
    ):
        """Test getting workflow state returns existing state."""
        # Initialize state
        workflow_service.initialize_workflow_state(test_project, git_manager)

        # Get state
        state = workflow_service.get_workflow_state(test_project, git_manager)

        assert state["current_state"] == "initiating"
        assert "updated_at" in state


class TestStateTransitionValidation:
    """Test state transition validation logic."""

    def test_is_valid_transition_valid_cases(self, workflow_service):
        """Test valid state transitions."""
        assert workflow_service.is_valid_transition("initiating", "planning") is True
        assert workflow_service.is_valid_transition("planning", "executing") is True
        assert workflow_service.is_valid_transition("executing", "monitoring") is True
        assert workflow_service.is_valid_transition("monitoring", "closing") is True
        assert workflow_service.is_valid_transition("closing", "closed") is True

    def test_is_valid_transition_iterative_cases(self, workflow_service):
        """Test iterative/backward state transitions."""
        # Can go back from planning to initiating
        assert workflow_service.is_valid_transition("planning", "initiating") is True
        # Can go back from executing to planning
        assert workflow_service.is_valid_transition("executing", "planning") is True
        # Can go back from monitoring to executing
        assert workflow_service.is_valid_transition("monitoring", "executing") is True

    def test_is_valid_transition_invalid_cases(self, workflow_service):
        """Test invalid state transitions."""
        # Cannot skip stages
        assert workflow_service.is_valid_transition("initiating", "executing") is False
        assert workflow_service.is_valid_transition("initiating", "closed") is False
        # Cannot transition from closed
        assert workflow_service.is_valid_transition("closed", "initiating") is False
        assert workflow_service.is_valid_transition("closed", "planning") is False

    def test_is_valid_transition_invalid_state(self, workflow_service):
        """Test transition with invalid state."""
        assert (
            workflow_service.is_valid_transition("invalid_state", "planning") is False
        )


class TestStateTransitions:
    """Test state transition execution."""

    def test_transition_state_valid(self, workflow_service, git_manager, test_project):
        """Test valid state transition."""
        # Initialize state
        workflow_service.initialize_workflow_state(test_project, git_manager)

        # Transition from initiating to planning
        new_state = workflow_service.transition_state(
            project_key=test_project,
            to_state="planning",
            actor="test_user",
            reason="Ready to plan",
            git_manager=git_manager,
        )

        assert new_state["current_state"] == "planning"
        assert new_state["previous_state"] == "initiating"
        assert new_state["updated_by"] == "test_user"
        assert len(new_state["transition_history"]) == 1

        transition = new_state["transition_history"][0]
        assert transition["from_state"] == "initiating"
        assert transition["to_state"] == "planning"
        assert transition["actor"] == "test_user"
        assert transition["reason"] == "Ready to plan"
        assert "timestamp" in transition

    def test_transition_state_invalid_raises_error(
        self, workflow_service, git_manager, test_project
    ):
        """Test that invalid transition raises ValueError."""
        # Initialize state
        workflow_service.initialize_workflow_state(test_project, git_manager)

        # Try invalid transition
        with pytest.raises(ValueError) as exc_info:
            workflow_service.transition_state(
                project_key=test_project,
                to_state="closed",  # Cannot jump from initiating to closed
                actor="test_user",
                git_manager=git_manager,
            )

        assert "Invalid transition" in str(exc_info.value)
        assert "initiating" in str(exc_info.value)
        assert "closed" in str(exc_info.value)

    def test_transition_state_multiple_transitions(
        self, workflow_service, git_manager, test_project
    ):
        """Test multiple sequential transitions."""
        # Initialize state
        workflow_service.initialize_workflow_state(test_project, git_manager)

        # Transition through multiple states
        workflow_service.transition_state(
            test_project, "planning", "user1", git_manager=git_manager
        )
        workflow_service.transition_state(
            test_project, "executing", "user2", git_manager=git_manager
        )
        state = workflow_service.transition_state(
            test_project, "monitoring", "user3", git_manager=git_manager
        )

        assert state["current_state"] == "monitoring"
        assert state["previous_state"] == "executing"
        assert len(state["transition_history"]) == 3

    def test_transition_state_with_correlation_id(
        self, workflow_service, git_manager, test_project
    ):
        """Test transition with correlation ID for tracing."""
        # Initialize state
        workflow_service.initialize_workflow_state(test_project, git_manager)

        # Transition with correlation ID
        correlation_id = "req-12345"
        new_state = workflow_service.transition_state(
            project_key=test_project,
            to_state="planning",
            actor="test_user",
            git_manager=git_manager,
            correlation_id=correlation_id,
        )

        assert new_state["current_state"] == "planning"
        # Audit event should contain correlation_id (verified in integration tests)


class TestAllowedTransitions:
    """Test getting allowed transitions."""

    def test_get_allowed_transitions_from_initiating(
        self, workflow_service, git_manager, test_project
    ):
        """Test allowed transitions from initiating state."""
        workflow_service.initialize_workflow_state(test_project, git_manager)

        allowed = workflow_service.get_allowed_transitions(test_project, git_manager)

        assert allowed == ["planning"]

    def test_get_allowed_transitions_from_planning(
        self, workflow_service, git_manager, test_project
    ):
        """Test allowed transitions from planning state."""
        workflow_service.initialize_workflow_state(test_project, git_manager)
        workflow_service.transition_state(
            test_project, "planning", git_manager=git_manager
        )

        allowed = workflow_service.get_allowed_transitions(test_project, git_manager)

        assert set(allowed) == {"executing", "initiating"}

    def test_get_allowed_transitions_from_closed(
        self, workflow_service, git_manager, test_project
    ):
        """Test that closed state has no allowed transitions."""
        workflow_service.initialize_workflow_state(test_project, git_manager)
        # Transition to closed
        workflow_service.transition_state(
            test_project, "planning", git_manager=git_manager
        )
        workflow_service.transition_state(
            test_project, "executing", git_manager=git_manager
        )
        workflow_service.transition_state(
            test_project, "monitoring", git_manager=git_manager
        )
        workflow_service.transition_state(
            test_project, "closing", git_manager=git_manager
        )
        workflow_service.transition_state(
            test_project, "closed", git_manager=git_manager
        )

        allowed = workflow_service.get_allowed_transitions(test_project, git_manager)

        assert allowed == []


class TestWorkflowStatePersistence:
    """Test workflow state persistence."""

    def test_state_persists_across_service_instances(self, git_manager, test_project):
        """Test that state persists when service is recreated."""
        # Create service and initialize state
        service1 = WorkflowService()
        service1.initialize_workflow_state(test_project, git_manager)
        service1.transition_state(test_project, "planning", git_manager=git_manager)

        # Create new service instance and retrieve state
        service2 = WorkflowService()
        state = service2.get_workflow_state(test_project, git_manager)

        assert state["current_state"] == "planning"
        assert state["previous_state"] == "initiating"
        assert len(state["transition_history"]) == 1
