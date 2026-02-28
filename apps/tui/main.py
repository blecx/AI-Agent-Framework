#!/usr/bin/env python3
"""
TUI Client for ISO 21500 AI-Agent Framework

A command-line interface for interacting with the AI Agent API.
Provides commands for project management, command execution, and artifact access.
"""
import click
from api_client import APIClient
from utils import print_success, print_json, print_info, print_warning, print_table
from commands.projects import projects_group
from commands.propose import propose_group
from commands.proposals import proposals_group
from commands.artifacts import artifacts_group
from commands.raid import raid_group
from commands.workflow import workflow_group
from commands.config import config_group


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

@cli.command(name="audit")
@click.option("--project", required=True, help="Project key")
@click.option(
    "--rule",
    "rules",
    multiple=True,
    help="Optional audit rule filter (repeatable)",
)
@click.option(
    "--limit",
    default=10,
    show_default=True,
    type=click.IntRange(min=1),
    help="Maximum number of issues to display",
)
def audit(project: str, rules: tuple[str, ...], limit: int):
    """Run audit rules and show a compact result summary."""
    client = APIClient()

    try:
        result = client.run_audit(project_key=project, rule_set=list(rules) or None)

        issues = result.get("issues", [])
        total_issues = int(result.get("total_issues", len(issues)))
        completeness_score = result.get("completeness_score", 0)
        rule_violations = result.get("rule_violations", {})

        severity_counts = {"error": 0, "warning": 0, "info": 0}
        for issue in issues:
            severity = str(issue.get("severity", "")).lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

        print_success(f"Audit completed for '{project}'")
        print_info(f"Completeness score: {completeness_score}")
        print_info(f"Total issues: {total_issues}")

        severity_rows = [
            {"severity": "error", "count": severity_counts["error"]},
            {"severity": "warning", "count": severity_counts["warning"]},
            {"severity": "info", "count": severity_counts["info"]},
        ]
        print_table(severity_rows, title="Issue Counts by Severity")

        if rule_violations:
            rule_rows = [
                {"rule": rule_name, "violations": count}
                for rule_name, count in sorted(rule_violations.items())
            ]
            print_table(rule_rows, title="Rule Violations")

        if issues:
            issue_rows = [
                {
                    "severity": issue.get("severity", ""),
                    "rule": issue.get("rule", ""),
                    "artifact": issue.get("artifact", ""),
                    "message": issue.get("message", ""),
                }
                for issue in issues[:limit]
            ]
            print_table(issue_rows, title=f"First {min(limit, len(issues))} Issue(s)")
            if len(issues) > limit:
                print_info(
                    f"Showing {limit} of {len(issues)} issues. Increase --limit to view more."
                )
        else:
            print_warning("No audit issues found")

        print_json(result, title="Audit Result")
    finally:
        client.close()


# Add command groups
cli.add_command(projects_group)
cli.add_command(propose_group)
cli.add_command(proposals_group)
cli.add_command(artifacts_group)
cli.add_command(raid_group)
cli.add_command(workflow_group)
cli.add_command(config_group)


if __name__ == "__main__":
    cli()
