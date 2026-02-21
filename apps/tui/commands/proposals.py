"""
Proposal lifecycle management commands.
"""

import click
from api_client import APIClient
from utils import print_success, print_info, print_json, print_table


@click.group(name="proposals")
def proposals_group():
    """Proposal lifecycle management commands."""
    pass


@proposals_group.command(name="list")
@click.option("--project", required=True, help="Project key")
@click.option(
    "--status",
    "status_filter",
    type=click.Choice(["pending", "accepted", "rejected"]),
    help="Filter by proposal status",
)
@click.option(
    "--change-type",
    type=click.Choice(["create", "update", "delete"]),
    help="Filter by change type",
)
def list_proposals(project: str, status_filter: str, change_type: str):
    """List proposals for a project."""
    client = APIClient()

    try:
        proposals = client.list_proposals(
            project_key=project,
            status_filter=status_filter,
            change_type=change_type,
        )

        if not proposals:
            print_info("No proposals found")
            return

        rows = [
            {
                "id": proposal.get("id", ""),
                "status": proposal.get("status", ""),
                "change_type": proposal.get("change_type", ""),
                "target_artifact": proposal.get("target_artifact", ""),
                "author": proposal.get("author", ""),
                "created_at": proposal.get("created_at", ""),
            }
            for proposal in proposals
        ]

        print_table(rows, title=f"Proposals for Project '{project}'")
        print_info(f"Total: {len(proposals)} proposal(s)")
    finally:
        client.close()


@proposals_group.command(name="get")
@click.option("--project", required=True, help="Project key")
@click.option("--id", "proposal_id", required=True, help="Proposal ID")
def get_proposal(project: str, proposal_id: str):
    """Get proposal details by ID."""
    client = APIClient()

    try:
        proposal = client.get_proposal(project, proposal_id)
        print_json(proposal, title=f"Proposal '{proposal_id}'")
    finally:
        client.close()


@proposals_group.command(name="apply")
@click.option("--project", required=True, help="Project key")
@click.option("--id", "proposal_id", required=True, help="Proposal ID")
def apply_proposal(project: str, proposal_id: str):
    """Apply a proposal by ID."""
    client = APIClient()

    try:
        result = client.apply_proposal(project, proposal_id)
        print_success(f"Proposal applied successfully: {proposal_id}")
        print_json(result, title="Apply Result")
    finally:
        client.close()


@proposals_group.command(name="reject")
@click.option("--project", required=True, help="Project key")
@click.option("--id", "proposal_id", required=True, help="Proposal ID")
@click.option("--reason", required=True, help="Reason for rejection")
def reject_proposal(project: str, proposal_id: str, reason: str):
    """Reject a proposal by ID."""
    client = APIClient()

    try:
        result = client.reject_proposal(project, proposal_id, reason)
        print_success(f"Proposal rejected successfully: {proposal_id}")
        print_json(result, title="Reject Result")
    finally:
        client.close()
