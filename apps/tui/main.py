#!/usr/bin/env python3
"""
TUI Client for ISO 21500 AI-Agent Framework

A command-line interface for interacting with the AI Agent API.
Provides commands for project management, command execution, and artifact access.
"""
import click
from api_client import APIClient
from utils import print_success, print_json
from commands.projects import projects_group
from commands.propose import propose_group
from commands.artifacts import artifacts_group


@click.group()
@click.version_option(version="1.0.0", prog_name="ISO 21500 TUI Client")
def cli():
    """
    ISO 21500 AI-Agent Framework - TUI Client
    
    A command-line interface for managing ISO 21500 projects via the AI Agent API.
    
    \b
    Quick Start:
      # Create a project
      python main.py projects create --key PROJ001 --name "My Project"
      
      # List projects
      python main.py projects list
      
      # Propose a command
      python main.py commands propose --project PROJ001 --command assess_gaps
      
      # Apply a proposal
      python main.py commands apply --project PROJ001 --proposal <proposal-id>
    
    \b
    Environment Variables:
      API_BASE_URL    API endpoint (default: http://localhost:8000)
      API_TIMEOUT     Request timeout in seconds (default: 30)
      API_KEY         Optional API key for authentication
    """
    pass


@cli.command()
def health():
    """Check API health status."""
    client = APIClient()
    try:
        result = client.health_check()
        print_success("API is healthy!")
        print_json(result, title="Health Status")
    finally:
        client.close()


# Add command groups
cli.add_command(projects_group)
cli.add_command(propose_group)
cli.add_command(artifacts_group)


if __name__ == "__main__":
    cli()
