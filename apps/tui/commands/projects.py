"""
Project management commands.
"""
import click
from api_client import APIClient
from utils import print_success, print_error, print_json, print_table, format_project_info
from rich.console import Console

console = Console()


@click.group(name="projects")
def projects_group():
    """Project management commands."""
    pass


@projects_group.command(name="create")
@click.option("--key", required=True, help="Unique project key (alphanumeric, dashes, underscores)")
@click.option("--name", required=True, help="Project name")
def create_project(key: str, name: str):
    """Create a new project."""
    client = APIClient()
    
    try:
        result = client.create_project(key, name)
        print_success(f"Project '{name}' created successfully!")
        print_json(result, title="Project Details")
    finally:
        client.close()


@projects_group.command(name="list")
def list_projects():
    """List all projects."""
    client = APIClient()
    
    try:
        projects = client.list_projects()
        
        if not projects:
            print_error("No projects found")
            return
        
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
