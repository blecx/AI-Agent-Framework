"""
AI Agent API Client

A Python CLI client for consuming the AI Agent REST API.
Demonstrates API usage without the web UI.
"""

import os
import sys
import json
import click
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))


class APIClient:
    """HTTP client for AI Agent API."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and errors."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            click.echo(f"Error: HTTP {e.response.status_code}", err=True)
            try:
                error_detail = e.response.json().get("detail", str(e))
                click.echo(f"Details: {error_detail}", err=True)
            except (ValueError, json.JSONDecodeError):
                click.echo(f"Details: {e.response.text}", err=True)
            sys.exit(1)
        except (httpx.RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            click.echo(f"Connection error: {str(e)}", err=True)
            sys.exit(1)
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = self.client.get(f"{self.base_url}/health")
        return self._handle_response(response)
    
    def create_project(self, key: str, name: str) -> Dict[str, Any]:
        """Create a new project."""
        response = self.client.post(
            f"{self.base_url}/projects",
            json={"key": key, "name": name}
        )
        return self._handle_response(response)
    
    def list_projects(self) -> list:
        """List all projects."""
        response = self.client.get(f"{self.base_url}/projects")
        return self._handle_response(response)
    
    def get_project_state(self, project_key: str) -> Dict[str, Any]:
        """Get project state."""
        response = self.client.get(f"{self.base_url}/projects/{project_key}/state")
        return self._handle_response(response)
    
    def propose_command(
        self, 
        project_key: str, 
        command: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Propose a command."""
        payload = {"command": command}
        if params:
            payload["params"] = params
        
        response = self.client.post(
            f"{self.base_url}/projects/{project_key}/commands/propose",
            json=payload
        )
        return self._handle_response(response)
    
    def apply_command(self, project_key: str, proposal_id: str) -> Dict[str, Any]:
        """Apply a command proposal."""
        response = self.client.post(
            f"{self.base_url}/projects/{project_key}/commands/apply",
            json={"proposal_id": proposal_id}
        )
        return self._handle_response(response)
    
    def list_artifacts(self, project_key: str) -> list:
        """List project artifacts."""
        response = self.client.get(f"{self.base_url}/projects/{project_key}/artifacts")
        return self._handle_response(response)
    
    def get_artifact(self, project_key: str, artifact_path: str) -> str:
        """Get artifact content."""
        response = self.client.get(
            f"{self.base_url}/projects/{project_key}/artifacts/{artifact_path}"
        )
        try:
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            click.echo(f"Error: HTTP {e.response.status_code}", err=True)
            try:
                error_detail = e.response.json().get("detail", "Artifact not found")
                click.echo(f"Details: {error_detail}", err=True)
            except (ValueError, json.JSONDecodeError):
                click.echo(f"Details: {e.response.text}", err=True)
            sys.exit(1)
        except (httpx.RequestError, httpx.TimeoutException, httpx.ConnectError) as e:
            click.echo(f"Connection error: {str(e)}", err=True)
            sys.exit(1)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


# CLI Commands
@click.group()
@click.option("--api-url", default=API_BASE_URL, help="API base URL")
@click.pass_context
def cli(ctx, api_url):
    """AI Agent API Client - Interact with the AI Agent system from the command line."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = APIClient(api_url, API_TIMEOUT)


@cli.command()
@click.pass_context
def health(ctx):
    """Check API health status."""
    client = ctx.obj["client"]
    result = client.health_check()
    click.echo("API Health Check:")
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.option("--key", required=True, help="Project key (e.g., PROJ001)")
@click.option("--name", required=True, help="Project name")
@click.pass_context
def create_project(ctx, key, name):
    """Create a new project."""
    client = ctx.obj["client"]
    click.echo(f"Creating project '{key}' with name '{name}'...")
    result = client.create_project(key, name)
    click.echo("✓ Project created successfully!")
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.pass_context
def list_projects(ctx):
    """List all projects."""
    client = ctx.obj["client"]
    projects = client.list_projects()
    
    if not projects:
        click.echo("No projects found.")
        return
    
    click.echo(f"Found {len(projects)} project(s):")
    for project in projects:
        click.echo(f"  - {project['key']}: {project['name']}")


@cli.command()
@click.option("--key", required=True, help="Project key")
@click.pass_context
def get_state(ctx, key):
    """Get project state."""
    client = ctx.obj["client"]
    state = client.get_project_state(key)
    click.echo(f"Project State for '{key}':")
    click.echo(json.dumps(state, indent=2))


@cli.command()
@click.option("--key", required=True, help="Project key")
@click.option("--command", required=True, type=click.Choice(["assess_gaps", "generate_artifact", "generate_plan"]), help="Command to run")
@click.option("--artifact-name", help="Artifact name (for generate_artifact)")
@click.option("--artifact-type", help="Artifact type (for generate_artifact)")
@click.pass_context
def propose(ctx, key, command, artifact_name, artifact_type):
    """Propose a command (preview changes)."""
    client = ctx.obj["client"]
    
    # Build parameters based on command
    params = {}
    if command == "generate_artifact":
        if not artifact_name or not artifact_type:
            click.echo("Error: --artifact-name and --artifact-type are required for generate_artifact", err=True)
            sys.exit(1)
        params = {"artifact_name": artifact_name, "artifact_type": artifact_type}
    
    click.echo(f"Proposing command '{command}' for project '{key}'...")
    result = client.propose_command(key, command, params)
    
    click.echo("✓ Proposal generated successfully!")
    click.echo(f"\nProposal ID: {result['proposal_id']}")
    click.echo(f"\nAssistant Message:\n{result['assistant_message']}")
    click.echo(f"\nFile Changes ({len(result['file_changes'])}):")
    
    for change in result["file_changes"]:
        click.echo(f"\n  {change['operation'].upper()}: {change['path']}")
        if change.get("diff"):
            click.echo("  Diff:")
            for line in change["diff"].split("\n")[:20]:  # Show first 20 lines
                click.echo(f"    {line}")
            if len(change["diff"].split("\n")) > 20:
                click.echo("    ... (truncated)")
    
    click.echo(f"\nDraft Commit Message:\n{result['draft_commit_message']}")
    click.echo(f"\nTo apply this proposal, run:")
    click.echo(f"  python -m src.client apply --key {key} --proposal-id {result['proposal_id']}")


@cli.command()
@click.option("--key", required=True, help="Project key")
@click.option("--proposal-id", required=True, help="Proposal ID from propose command")
@click.pass_context
def apply(ctx, key, proposal_id):
    """Apply a command proposal."""
    client = ctx.obj["client"]
    
    click.echo(f"Applying proposal '{proposal_id}' for project '{key}'...")
    result = client.apply_command(key, proposal_id)
    
    click.echo("✓ Proposal applied successfully!")
    click.echo(f"\nCommit Hash: {result['commit_hash']}")
    click.echo(f"Message: {result['message']}")
    click.echo(f"\nChanged Files ({len(result['changed_files'])}):")
    for file_path in result["changed_files"]:
        click.echo(f"  - {file_path}")


@cli.command()
@click.option("--key", required=True, help="Project key")
@click.pass_context
def list_artifacts(ctx, key):
    """List project artifacts."""
    client = ctx.obj["client"]
    artifacts = client.list_artifacts(key)
    
    if not artifacts:
        click.echo(f"No artifacts found for project '{key}'.")
        return
    
    click.echo(f"Artifacts for project '{key}' ({len(artifacts)}):")
    for artifact in artifacts:
        click.echo(f"  - {artifact['path']} ({artifact['type']})")


@cli.command()
@click.option("--key", required=True, help="Project key")
@click.option("--path", required=True, help="Artifact path")
@click.pass_context
def get_artifact(ctx, key, path):
    """Get artifact content."""
    client = ctx.obj["client"]
    content = client.get_artifact(key, path)
    
    click.echo(f"Artifact: {key}/{path}")
    click.echo("=" * 80)
    click.echo(content)


@cli.command()
@click.option("--key", required=True, help="Project key")
@click.option("--name", required=True, help="Project name")
@click.option("--run-gaps/--no-run-gaps", default=True, help="Run assess_gaps after creating project")
@click.pass_context
def demo(ctx, key, name, run_gaps):
    """Run a complete demo workflow (create project + assess gaps)."""
    client = ctx.obj["client"]
    
    click.echo("=" * 80)
    click.echo("AI Agent API Client - Demo Workflow")
    click.echo("=" * 80)
    
    # Step 1: Create project (or check if exists)
    click.echo(f"\n[1/4] Creating project '{key}' with name '{name}'...")
    
    # Check if project already exists
    existing_projects = client.list_projects()
    project_exists = any(p['key'] == key for p in existing_projects)
    
    if project_exists:
        click.echo("⚠ Project already exists, continuing...")
    else:
        client.create_project(key, name)
        click.echo("✓ Project created successfully!")
    
    # Step 2: Get project state
    click.echo(f"\n[2/4] Getting project state...")
    state = client.get_project_state(key)
    click.echo(f"✓ Project '{state['project_info']['name']}' is ready")
    
    if run_gaps:
        # Step 3: Propose assess_gaps
        click.echo(f"\n[3/4] Proposing 'assess_gaps' command...")
        proposal = client.propose_command(key, "assess_gaps")
        click.echo(f"✓ Proposal generated: {proposal['proposal_id']}")
        click.echo(f"\nAssistant says:\n{proposal['assistant_message'][:200]}...")
        
        # Step 4: Apply proposal
        click.echo(f"\n[4/4] Applying proposal...")
        result = client.apply_command(key, proposal["proposal_id"])
        click.echo(f"✓ Changes committed: {result['commit_hash']}")
        
        # Show artifacts
        click.echo(f"\nFinal artifacts:")
        artifacts = client.list_artifacts(key)
        for artifact in artifacts:
            click.echo(f"  - {artifact['path']}")
    else:
        click.echo(f"\n[3/4] Skipping assess_gaps (--no-run-gaps)")
        click.echo(f"\n[4/4] Done!")
    
    click.echo("\n" + "=" * 80)
    click.echo("Demo completed successfully!")
    click.echo("=" * 80)


def main():
    """Main entry point."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n\nInterrupted by user.", err=True)
        sys.exit(130)
    except (httpx.RequestError, httpx.HTTPError) as e:
        click.echo(f"\nAPI connection error: {str(e)}", err=True)
        sys.exit(1)
    except click.ClickException as e:
        e.show()
        sys.exit(1)


if __name__ == "__main__":
    main()
