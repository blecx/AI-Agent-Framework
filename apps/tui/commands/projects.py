"""
Project management commands.
"""

import json
import click
from api_client import APIClient
from utils import (
    print_success,
    print_error,
    print_json,
    print_table,
    format_project_info,
)
from rich.console import Console

console = Console()


@click.group(name="projects")
def projects_group():
    """Project management commands."""
    pass


@projects_group.command(name="create")
@click.option(
    "--key",
    required=True,
    help="Unique project key (alphanumeric, dashes, underscores)",
)
@click.option("--name", required=True, help="Project name")
@click.option("--description", help="Optional project description")
def create_project(key: str, name: str, description: str):
    """Create a new project."""
    client = APIClient()

    try:
        result = client.create_project(key, name, description)
        print_success(f"Project '{name}' created successfully!")
        print_json(result, title="Project Details")
    finally:
        client.close()


@projects_group.command(name="list")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    show_default=True,
    help="Output format",
)
def list_projects(output_format: str):
    """List all projects."""
    client = APIClient()

    try:
        projects = client.list_projects()

        if not projects:
            if output_format == "json":
                click.echo("[]")
            else:
                print_error("No projects found")
            return

        if output_format == "json":
            click.echo(json.dumps(projects))
        else:
            print_table(projects, title="Projects")
            console.print(f"\n[bold]Total:[/bold] {len(projects)} project(s)")
    finally:
        client.close()


@projects_group.command(name="get")
@click.option("--key", required=True, help="Project key")
def get_project(key: str):
    """Get project details and state."""
    client = APIClient()

    try:
        state = client.get_project(key)

        # Display project info
        console.print("\n[bold cyan]Project Information[/bold cyan]")
        console.print(format_project_info(state["project_info"]))

        # Display artifacts
        console.print("\n[bold cyan]Artifacts[/bold cyan]")
        if state["artifacts"]:
            print_table(state["artifacts"])
        else:
            console.print("[dim]No artifacts yet[/dim]")

        # Display last commit
        console.print("\n[bold cyan]Last Commit[/bold cyan]")
        if state["last_commit"]:
            print_json(state["last_commit"])
        else:
            console.print("[dim]No commits yet[/dim]")
    finally:
        client.close()


@projects_group.command(name="delete")
@click.option("--key", required=True, help="Project key")
def delete_project(key: str):
    """Delete (soft-delete) a project."""
    client = APIClient()

    try:
        client.delete_project(key)
        print_success(f"Project '{key}' deleted successfully!")
    finally:
        client.close()
