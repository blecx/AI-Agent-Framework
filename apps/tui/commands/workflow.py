"""
Workflow management commands.
"""

import click
from api_client import APIClient
from utils import print_success, print_info, print_json, print_table


@click.group(name="workflow")
def workflow_group():
    """Workflow state and audit commands."""
    pass


@workflow_group.command(name="state")
@click.option("--project", required=True, help="Project key")
def workflow_state(project: str):
    """Get current workflow state for a project."""
    client = APIClient()

    try:
        state = client.get_workflow_state(project)
        print_json(state, title=f"Workflow State for '{project}'")
    finally:
        client.close()


@workflow_group.command(name="transition")
@click.option("--project", required=True, help="Project key")
@click.option(
    "--to-state",
    required=True,
    type=click.Choice(
        ["initiating", "planning", "executing", "monitoring", "closing", "closed"]
    ),
    help="Target workflow state",
)
@click.option("--actor", required=True, help="Actor performing transition")
@click.option("--reason", help="Optional transition reason")
def workflow_transition(project: str, to_state: str, actor: str, reason: str):
    """Transition workflow state for a project."""
    client = APIClient()

    try:
        state = client.transition_workflow_state(
            project_key=project,
            to_state=to_state,
            actor=actor,
            reason=reason,
        )
        print_success(
            f"Workflow transitioned to '{state.get('current_state', to_state)}'"
        )
        print_json(state, title="Updated Workflow State")
    finally:
        client.close()


@workflow_group.command(name="allowed-transitions")
@click.option("--project", required=True, help="Project key")
def workflow_allowed_transitions(project: str):
    """Get allowed workflow transitions from current state."""
    client = APIClient()

    try:
        result = client.get_allowed_workflow_transitions(project)
        transitions = result.get("allowed_transitions", [])

        if transitions:
            rows = [{"transition": transition} for transition in transitions]
            print_table(rows, title=f"Allowed Transitions for '{project}'")
        else:
            print_info("No allowed transitions")

        print_json(result, title="Transition Details")
    finally:
        client.close()


@workflow_group.command(name="audit-events")
@click.option("--project", required=True, help="Project key")
@click.option("--event-type", help="Filter by event type")
@click.option("--actor", help="Filter by actor")
@click.option("--since", help="Filter events since timestamp (ISO 8601)")
@click.option("--until", help="Filter events until timestamp (ISO 8601)")
@click.option("--limit", type=int, help="Max events to return")
@click.option("--offset", type=int, help="Events to skip")
def workflow_audit_events(
    project: str,
    event_type: str,
    actor: str,
    since: str,
    until: str,
    limit: int,
    offset: int,
):
    """List workflow audit events for a project."""
    client = APIClient()

    try:
        result = client.get_audit_events(
            project_key=project,
            event_type=event_type,
            actor=actor,
            since=since,
            until=until,
            limit=limit,
            offset=offset,
        )

        events = result.get("events", [])
        if events:
            rows = [
                {
                    "event_id": event.get("event_id", ""),
                    "event_type": event.get("event_type", ""),
                    "actor": event.get("actor", ""),
                    "timestamp": event.get("timestamp", ""),
                }
                for event in events
            ]
            print_table(rows, title=f"Audit Events for '{project}'")
            print_info(f"Total: {result.get('total', len(events))} event(s)")
        else:
            print_info("No audit events found")

        print_json(result, title="Audit Event Details")
    finally:
        client.close()
