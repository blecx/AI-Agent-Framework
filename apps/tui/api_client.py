"""
HTTP client for AI Agent API.
Handles all API communication.
"""

import sys
from typing import Optional, Dict, Any
import httpx
from config import Config
from utils import print_error


class APIClient:
    """HTTP client for AI Agent REST API."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        """Initialize API client.

        Args:
            base_url: API base URL (defaults to Config.API_BASE_URL)
            timeout: Request timeout in seconds (defaults to Config.API_TIMEOUT)
        """
        self.base_url = (base_url or Config.get_api_base_url()).rstrip("/")
        self.timeout = timeout or Config.API_TIMEOUT
        self.headers = Config.get_headers()
        self.client = httpx.Client(timeout=self.timeout, headers=self.headers)

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and errors.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response data

        Raises:
            SystemExit: On error (with error message printed)
        """
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print_error(f"HTTP {e.response.status_code} error")
            try:
                error_detail = e.response.json().get("detail", str(e))
                print_error(f"Details: {error_detail}")
            except Exception:
                print_error(f"Details: {e.response.text}")
            sys.exit(1)
        except (httpx.RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            print_error(f"Connection error: {str(e)}")
            print_error(f"Failed to connect to API at {self.base_url}")
            sys.exit(1)

    def health_check(self) -> Dict[str, Any]:
        """Check API health status.

        Returns:
            Health status information
        """
        response = self.client.get(f"{self.base_url}/health")
        return self._handle_response(response)

    def create_project(
        self, key: str, name: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new project.

        Args:
            key: Unique project key
            name: Project name

        Returns:
            Created project information
        """
        payload = {"key": key, "name": name}
        if description:
            payload["description"] = description

        response = self.client.post(f"{self.base_url}/projects", json=payload)
        return self._handle_response(response)

    def list_projects(self) -> list:
        """List all projects.

        Returns:
            List of project information
        """
        response = self.client.get(f"{self.base_url}/projects")
        return self._handle_response(response)

    def get_project(self, project_key: str) -> Dict[str, Any]:
        """Get project state.

        Args:
            project_key: Project key

        Returns:
            Project state information
        """
        response = self.client.get(f"{self.base_url}/projects/{project_key}/state")
        return self._handle_response(response)

    def delete_project(self, project_key: str) -> Dict[str, Any]:
        """Delete (soft-delete) a project.

        Args:
            project_key: Project key

        Returns:
            Empty response object for 204/200 style responses
        """
        response = self.client.delete(f"{self.base_url}/projects/{project_key}")
        return self._handle_response(response) if response.content else {}

    def propose_command(
        self, project_key: str, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Propose a command for a project.

        Args:
            project_key: Project key
            command: Command name (assess_gaps, generate_artifact, generate_plan)
            params: Optional command parameters

        Returns:
            Command proposal with changes preview
        """
        payload: Dict[str, Any] = {"command": command}
        if params:
            payload["params"] = params

        response = self.client.post(
            f"{self.base_url}/projects/{project_key}/commands/propose", json=payload
        )
        return self._handle_response(response)

    def apply_command(self, project_key: str, proposal_id: str) -> Dict[str, Any]:
        """Apply a previously proposed command.

        Args:
            project_key: Project key
            proposal_id: Proposal ID from propose_command

        Returns:
            Apply result with commit information
        """
        response = self.client.post(
            f"{self.base_url}/projects/{project_key}/commands/apply",
            json={"proposal_id": proposal_id},
        )
        return self._handle_response(response)

    def list_proposals(
        self,
        project_key: str,
        status_filter: Optional[str] = None,
        change_type: Optional[str] = None,
    ) -> list:
        """List proposals for a project with optional filters."""
        params: Dict[str, str] = {}
        if status_filter:
            params["status_filter"] = status_filter
        if change_type:
            params["change_type"] = change_type

        response = self.client.get(
            f"{self.base_url}/projects/{project_key}/proposals",
            params=params or None,
        )
        return self._handle_response(response)

    def get_proposal(self, project_key: str, proposal_id: str) -> Dict[str, Any]:
        """Get a proposal by ID."""
        response = self.client.get(
            f"{self.base_url}/projects/{project_key}/proposals/{proposal_id}"
        )
        return self._handle_response(response)

    def apply_proposal(self, project_key: str, proposal_id: str) -> Dict[str, Any]:
        """Apply a proposal by ID."""
        response = self.client.post(
            f"{self.base_url}/projects/{project_key}/proposals/{proposal_id}/apply"
        )
        return self._handle_response(response)

    def reject_proposal(
        self,
        project_key: str,
        proposal_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        """Reject a proposal by ID with reason."""
        response = self.client.post(
            f"{self.base_url}/projects/{project_key}/proposals/{proposal_id}/reject",
            json={"reason": reason},
        )
        return self._handle_response(response)

    def list_artifacts(self, project_key: str) -> list:
        """List project artifacts.

        Args:
            project_key: Project key

        Returns:
            List of artifact information
        """
        response = self.client.get(f"{self.base_url}/projects/{project_key}/artifacts")
        return self._handle_response(response)

    def get_artifact(self, project_key: str, artifact_path: str) -> str:
        """Get artifact content.

        Args:
            project_key: Project key
            artifact_path: Path to artifact file

        Returns:
            Artifact content as string
        """
        response = self.client.get(
            f"{self.base_url}/projects/{project_key}/artifacts/{artifact_path}"
        )
        return self._handle_response(response)

    def list_raid_items(
        self,
        project_key: str,
        raid_type: Optional[str] = None,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List RAID items for a project with optional filters."""
        params: Dict[str, str] = {}
        if raid_type:
            params["type"] = raid_type
        if status:
            params["status"] = status
        if owner:
            params["owner"] = owner
        if priority:
            params["priority"] = priority

        response = self.client.get(
            f"{self.base_url}/projects/{project_key}/raid",
            params=params or None,
        )
        return self._handle_response(response)

    def get_raid_item(self, project_key: str, raid_id: str) -> Dict[str, Any]:
        """Get a RAID item by ID."""
        response = self.client.get(
            f"{self.base_url}/projects/{project_key}/raid/{raid_id}"
        )
        return self._handle_response(response)

    def create_raid_item(
        self,
        project_key: str,
        raid_type: str,
        title: str,
        description: str,
        owner: str,
        priority: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a RAID item."""
        payload: Dict[str, Any] = {
            "type": raid_type,
            "title": title,
            "description": description,
            "owner": owner,
        }
        if priority:
            payload["priority"] = priority
        if status:
            payload["status"] = status

        response = self.client.post(
            f"{self.base_url}/projects/{project_key}/raid", json=payload
        )
        return self._handle_response(response)

    def update_raid_item(
        self,
        project_key: str,
        raid_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a RAID item."""
        response = self.client.put(
            f"{self.base_url}/projects/{project_key}/raid/{raid_id}",
            json=updates,
        )
        return self._handle_response(response)

    def delete_raid_item(self, project_key: str, raid_id: str) -> Dict[str, Any]:
        """Delete a RAID item."""
        response = self.client.delete(
            f"{self.base_url}/projects/{project_key}/raid/{raid_id}"
        )
        return self._handle_response(response)

    def get_workflow_state(self, project_key: str) -> Dict[str, Any]:
        """Get workflow state for a project."""
        response = self.client.get(
            f"{self.base_url}/projects/{project_key}/workflow/state"
        )
        return self._handle_response(response)

    def transition_workflow_state(
        self,
        project_key: str,
        to_state: str,
        actor: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transition workflow state for a project."""
        payload: Dict[str, Any] = {
            "to_state": to_state,
            "actor": actor,
        }
        if reason:
            payload["reason"] = reason

        response = self.client.patch(
            f"{self.base_url}/projects/{project_key}/workflow/state",
            json=payload,
        )
        return self._handle_response(response)

    def get_allowed_workflow_transitions(self, project_key: str) -> Dict[str, Any]:
        """Get allowed workflow transitions for current project state."""
        response = self.client.get(
            f"{self.base_url}/projects/{project_key}/workflow/allowed-transitions"
        )
        return self._handle_response(response)

    def get_audit_events(
        self,
        project_key: str,
        event_type: Optional[str] = None,
        actor: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get audit events for a project with optional filters."""
        params: Dict[str, Any] = {}
        if event_type:
            params["event_type"] = event_type
        if actor:
            params["actor"] = actor
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        response = self.client.get(
            f"{self.base_url}/projects/{project_key}/audit-events",
            params=params or None,
        )
        return self._handle_response(response)

    def close(self):
        """Close the HTTP client."""
        self.client.close()
