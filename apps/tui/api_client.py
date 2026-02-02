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

    def __init__(self, base_url: str = None, timeout: int = None):
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

    def create_project(self, key: str, name: str) -> Dict[str, Any]:
        """Create a new project.

        Args:
            key: Unique project key
            name: Project name

        Returns:
            Created project information
        """
        response = self.client.post(
            f"{self.base_url}/projects", json={"key": key, "name": name}
        )
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
        payload = {"command": command}
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

    def close(self):
        """Close the HTTP client."""
        self.client.close()
