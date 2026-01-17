"""
Workflow service for managing project workflow state transitions.
Aligned with ISO 21500 standards.
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Define valid state transitions (ISO 21500 aligned)
VALID_TRANSITIONS = {
    "initiating": ["planning"],
    "planning": ["executing", "initiating"],  # Can go back to refine
    "executing": ["monitoring", "planning"],  # Can iterate back to planning
    "monitoring": [
        "executing",
        "closing",
    ],  # Can go back to executing or move to closing
    "closing": ["closed"],
    "closed": [],  # Terminal state
}


class WorkflowService:
    """Service for handling workflow state transitions."""

    def __init__(self):
        """Initialize workflow service."""
        pass

    def get_workflow_state(
        self, project_key: str, git_manager
    ) -> Optional[Dict[str, Any]]:
        """Get current workflow state for a project."""
        content = git_manager.read_file(project_key, "workflow/state.json")
        if content is None:
            # Return default initial state
            return {
                "current_state": "initiating",
                "previous_state": None,
                "transition_history": [],
                "updated_at": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "updated_by": "system",
            }
        return json.loads(content)

    def initialize_workflow_state(
        self, project_key: str, git_manager
    ) -> Dict[str, Any]:
        """Initialize workflow state for a new project."""
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        state = {
            "current_state": "initiating",
            "previous_state": None,
            "transition_history": [],
            "updated_at": now,
            "updated_by": "system",
        }

        # Write state
        content = json.dumps(state, indent=2)
        git_manager.write_file(project_key, "workflow/state.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Initialize workflow state",
            ["workflow/state.json"],
        )

        return state

    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a state transition is valid."""
        if from_state not in VALID_TRANSITIONS:
            return False
        return to_state in VALID_TRANSITIONS[from_state]

    def transition_state(
        self,
        project_key: str,
        to_state: str,
        actor: str = "system",
        reason: Optional[str] = None,
        git_manager=None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transition workflow state with validation and audit.

        Args:
            project_key: Project key
            to_state: Target state
            actor: User/actor performing transition
            reason: Optional reason for transition
            git_manager: Git manager instance
            correlation_id: Optional correlation ID for tracing

        Returns:
            Updated workflow state

        Raises:
            ValueError: If transition is invalid
        """
        # Get current state
        current = self.get_workflow_state(project_key, git_manager)
        from_state = current["current_state"]

        # Validate transition
        if not self.is_valid_transition(from_state, to_state):
            raise ValueError(
                f"Invalid transition from '{from_state}' to '{to_state}'. "
                f"Valid transitions from '{from_state}': {VALID_TRANSITIONS.get(from_state, [])}"
            )

        # Create transition record
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        transition = {
            "from_state": from_state,
            "to_state": to_state,
            "timestamp": now,
            "actor": actor,
            "reason": reason,
        }

        # Update state
        new_state = {
            "current_state": to_state,
            "previous_state": from_state,
            "transition_history": current.get("transition_history", []) + [transition],
            "updated_at": now,
            "updated_by": actor,
        }

        # Write state
        content = json.dumps(new_state, indent=2)
        git_manager.write_file(project_key, "workflow/state.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Transition workflow state: {from_state} -> {to_state}",
            ["workflow/state.json"],
        )

        # Create audit event
        # Import here to avoid circular dependency
        try:
            from services.audit_service import AuditService
        except ImportError:
            from apps.api.services.audit_service import AuditService

        audit_service = AuditService()
        audit_service.log_audit_event(
            project_key=project_key,
            event_type="workflow_state_changed",
            actor=actor,
            payload_summary={
                "from_state": from_state,
                "to_state": to_state,
                "reason": reason,
            },
            git_manager=git_manager,
            correlation_id=correlation_id,
        )

        return new_state

    def get_allowed_transitions(self, project_key: str, git_manager) -> List[str]:
        """Get list of allowed transitions from current state."""
        current = self.get_workflow_state(project_key, git_manager)
        current_state = current["current_state"]
        return VALID_TRANSITIONS.get(current_state, [])
