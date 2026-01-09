"""
Command propose and apply workflow.
"""
import click
from api_client import APIClient
from utils import print_success, print_error, print_json, print_info, confirm_action
from rich.console import Console
from rich.syntax import Syntax

console = Console()


@click.group(name="commands")
def propose_group():
    """Command propose/apply workflow."""
    pass


@propose_group.command(name="propose")
@click.option("--project", required=True, help="Project key")
@click.option("--command", required=True, 
              type=click.Choice(["assess_gaps", "generate_artifact", "generate_plan"]),
              help="Command to propose")
@click.option("--artifact-name", help="Artifact name (for generate_artifact command)")
@click.option("--artifact-type", help="Artifact type (for generate_artifact command)")
def propose_command(project: str, command: str, artifact_name: str, artifact_type: str):
    """Propose a command and preview changes."""
    client = APIClient()
    
    try:
        # Build params if needed
        params = {}
        if command == "generate_artifact":
            if not artifact_name or not artifact_type:
                print_error("For generate_artifact command, both --artifact-name and --artifact-type are required")
                return
            params["artifact_name"] = artifact_name
            params["artifact_type"] = artifact_type
        
        print_info(f"Proposing command '{command}' for project '{project}'...")
        
        result = client.propose_command(project, command, params if params else None)
        
        print_success("Command proposed successfully!")
        
        # Display proposal details
        console.print("\n[bold cyan]Proposal ID:[/bold cyan]", result["proposal_id"])
        console.print("\n[bold cyan]Assistant Message:[/bold cyan]")
        console.print(result["assistant_message"])
        
        console.print("\n[bold cyan]Draft Commit Message:[/bold cyan]")
        console.print(result["draft_commit_message"])
        
        # Display file changes
        console.print("\n[bold cyan]File Changes:[/bold cyan]")
        for change in result["file_changes"]:
            console.print(f"\n[bold]{change['operation'].upper()}:[/bold] {change['path']}")
            if change.get("diff"):
                syntax = Syntax(change["diff"], "diff", theme="monokai")
                console.print(syntax)
        
        # Show apply command
        console.print(f"\n[bold green]To apply this proposal, run:[/bold green]")
        console.print(f"  python main.py commands apply --project {project} --proposal {result['proposal_id']}")
        
    finally:
        client.close()


@propose_group.command(name="apply")
@click.option("--project", required=True, help="Project key")
@click.option("--proposal", required=True, help="Proposal ID to apply")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def apply_command(project: str, proposal: str, yes: bool):
    """Apply a previously proposed command."""
    client = APIClient()
    
    try:
        if not yes:
            if not confirm_action(f"Apply proposal {proposal} to project {project}?", default=True):
                print_info("Apply cancelled")
                return
        
        print_info(f"Applying proposal '{proposal}'...")
        
        result = client.apply_command(project, proposal)
        
        print_success("Command applied successfully!")
        
        # Display result
        console.print(f"\n[bold cyan]Commit Hash:[/bold cyan] {result['commit_hash']}")
        console.print(f"\n[bold cyan]Message:[/bold cyan] {result['message']}")
        console.print(f"\n[bold cyan]Changed Files:[/bold cyan]")
        for file in result["changed_files"]:
            console.print(f"  • {file}")
        
    finally:
        client.close()
