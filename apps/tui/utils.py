"""
Utility functions for TUI client.
"""
import json
import sys
from typing import Any, Dict
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()


def print_success(message: str):
    """Print success message in green."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print error message in red."""
    console.print(f"[red]✗[/red] {message}", file=sys.stderr)


def print_info(message: str):
    """Print info message in blue."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_warning(message: str):
    """Print warning message in yellow."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_json(data: Any, title: str = None):
    """Pretty print JSON data."""
    json_str = json.dumps(data, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    if title:
        console.print(Panel(syntax, title=title, border_style="blue"))
    else:
        console.print(syntax)


def print_table(data: list, title: str = None):
    """Print data as a formatted table."""
    if not data:
        print_warning("No data to display")
        return
    
    # Get keys from first item
    if isinstance(data[0], dict):
        keys = list(data[0].keys())
    else:
        print_error("Cannot create table from non-dict data")
        return
    
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    # Add columns
    for key in keys:
        table.add_column(key.replace("_", " ").title())
    
    # Add rows
    for item in data:
        row = [str(item.get(key, "")) for key in keys]
        table.add_row(*row)
    
    console.print(table)


def format_project_info(project: Dict[str, Any]) -> str:
    """Format project information for display."""
    return (
        f"[bold]Project:[/bold] {project['name']}\n"
        f"[bold]Key:[/bold] {project['key']}\n"
        f"[bold]Methodology:[/bold] {project.get('methodology', 'ISO21500')}\n"
        f"[bold]Created:[/bold] {project.get('created_at', 'N/A')}\n"
        f"[bold]Updated:[/bold] {project.get('updated_at', 'N/A')}"
    )


def confirm_action(message: str, default: bool = False) -> bool:
    """Prompt user for confirmation."""
    suffix = "[Y/n]" if default else "[y/N]"
    response = console.input(f"{message} {suffix}: ").strip().lower()
    
    if not response:
        return default
    
    return response in ["y", "yes"]
