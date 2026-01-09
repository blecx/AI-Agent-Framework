"""
Artifact management commands.
"""
import click
from api_client import APIClient
from utils import print_error, print_table
from rich.console import Console
from rich.syntax import Syntax

console = Console()


@click.group(name="artifacts")
def artifacts_group():
    """Artifact management commands."""
    pass


@artifacts_group.command(name="list")
@click.option("--project", required=True, help="Project key")
def list_artifacts(project: str):
    """List artifacts for a project."""
    client = APIClient()
    
    try:
        artifacts = client.list_artifacts(project)
        
        if not artifacts:
            print_error("No artifacts found")
            return
        
        print_table(artifacts, title=f"Artifacts for Project '{project}'")
        console.print(f"\n[bold]Total:[/bold] {len(artifacts)} artifact(s)")
    finally:
        client.close()


@artifacts_group.command(name="get")
@click.option("--project", required=True, help="Project key")
@click.option("--path", required=True, help="Artifact path")
def get_artifact(project: str, path: str):
    """Get and display artifact content."""
    client = APIClient()
    
    try:
        content = client.get_artifact(project, path)
        
        console.print(f"\n[bold cyan]Artifact:[/bold cyan] {path}")
        console.print(f"[bold cyan]Project:[/bold cyan] {project}\n")
        
        # Try to detect file type for syntax highlighting
        if path.endswith(".md"):
            syntax = Syntax(content, "markdown", theme="monokai", line_numbers=True)
        elif path.endswith(".json"):
            syntax = Syntax(content, "json", theme="monokai", line_numbers=True)
        elif path.endswith((".yaml", ".yml")):
            syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
        else:
            syntax = Syntax(content, "text", theme="monokai", line_numbers=True)
        
        console.print(syntax)
        
    finally:
        client.close()
