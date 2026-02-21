"""
RAID management commands.
"""

import click
from api_client import APIClient
from utils import print_error, print_success, print_info, print_json, print_table


@click.group(name="raid")
def raid_group():
    """RAID management commands."""
    pass


@raid_group.command(name="list")
@click.option("--project", required=True, help="Project key")
@click.option(
    "--type",
    "raid_type",
    type=click.Choice(["risk", "assumption", "issue", "dependency"]),
    help="Filter by RAID type",
)
@click.option(
    "--status",
    type=click.Choice(["open", "in_progress", "mitigated", "closed", "accepted"]),
    help="Filter by status",
)
@click.option("--owner", help="Filter by owner")
@click.option(
    "--priority",
    type=click.Choice(["critical", "high", "medium", "low"]),
    help="Filter by priority",
)
def list_raid(
    project: str,
    raid_type: str,
    status: str,
    owner: str,
    priority: str,
):
    """List RAID items for a project."""
    client = APIClient()

    try:
        result = client.list_raid_items(
            project,
            raid_type=raid_type,
            status=status,
            owner=owner,
            priority=priority,
        )

        items = result.get("items", [])
        if not items:
            print_info("No RAID items found")
            return

        print_table(items, title=f"RAID Items for Project '{project}'")
        print_info(f"Total: {result.get('total', len(items))} item(s)")
    finally:
        client.close()


@raid_group.command(name="get")
@click.option("--project", required=True, help="Project key")
@click.option("--id", "raid_id", required=True, help="RAID item ID")
def get_raid(project: str, raid_id: str):
    """Get a RAID item by ID."""
    client = APIClient()

    try:
        item = client.get_raid_item(project, raid_id)
        print_json(item, title=f"RAID Item '{raid_id}'")
    finally:
        client.close()


@raid_group.command(name="add")
@click.option("--project", required=True, help="Project key")
@click.option(
    "--type",
    "raid_type",
    required=True,
    type=click.Choice(["risk", "assumption", "issue", "dependency"]),
    help="RAID type",
)
@click.option("--title", required=True, help="RAID item title")
@click.option("--description", required=True, help="RAID item description")
@click.option("--owner", required=True, help="Owner/assignee")
@click.option(
    "--priority",
    type=click.Choice(["critical", "high", "medium", "low"]),
    default="medium",
    show_default=True,
    help="Priority",
)
@click.option(
    "--status",
    type=click.Choice(["open", "in_progress", "mitigated", "closed", "accepted"]),
    default="open",
    show_default=True,
    help="Initial status",
)
def add_raid(
    project: str,
    raid_type: str,
    title: str,
    description: str,
    owner: str,
    priority: str,
    status: str,
):
    """Create a RAID item."""
    client = APIClient()

    try:
        item = client.create_raid_item(
            project_key=project,
            raid_type=raid_type,
            title=title,
            description=description,
            owner=owner,
            priority=priority,
            status=status,
        )
        print_success(f"RAID item created successfully: {item.get('id', 'N/A')}")
        print_json(item, title="Created RAID Item")
    finally:
        client.close()


@raid_group.command(name="update")
@click.option("--project", required=True, help="Project key")
@click.option("--id", "raid_id", required=True, help="RAID item ID")
@click.option("--title", help="Updated title")
@click.option("--description", help="Updated description")
@click.option("--owner", help="Updated owner")
@click.option(
    "--priority",
    type=click.Choice(["critical", "high", "medium", "low"]),
    help="Updated priority",
)
@click.option(
    "--status",
    type=click.Choice(["open", "in_progress", "mitigated", "closed", "accepted"]),
    help="Updated status",
)
def update_raid(
    project: str,
    raid_id: str,
    title: str,
    description: str,
    owner: str,
    priority: str,
    status: str,
):
    """Update a RAID item."""
    client = APIClient()

    try:
        updates = {}
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if owner is not None:
            updates["owner"] = owner
        if priority is not None:
            updates["priority"] = priority
        if status is not None:
            updates["status"] = status

        if not updates:
            print_error("No update fields provided")
            return

        item = client.update_raid_item(project, raid_id, updates)
        print_success(f"RAID item updated successfully: {raid_id}")
        print_json(item, title="Updated RAID Item")
    finally:
        client.close()


@raid_group.command(name="delete")
@click.option("--project", required=True, help="Project key")
@click.option("--id", "raid_id", required=True, help="RAID item ID")
def delete_raid(project: str, raid_id: str):
    """Delete a RAID item."""
    client = APIClient()

    try:
        client.delete_raid_item(project, raid_id)
        print_success(f"RAID item deleted successfully: {raid_id}")
    finally:
        client.close()
