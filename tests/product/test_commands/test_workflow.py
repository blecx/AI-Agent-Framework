import sys
from pathlib import Path

from click.testing import CliRunner

ROOT_DIR = Path(__file__).resolve().parents[3]
TUI_DIR = ROOT_DIR / "apps" / "tui"
if str(TUI_DIR) not in sys.path:
    sys.path.insert(0, str(TUI_DIR))

from commands import workflow as workflow_commands


class DummyClient:
    def __init__(self):
        self.calls = []

    def get_workflow_state(self, project):
        self.calls.append(("state", project))
        return {
            "current_state": "initiating",
            "previous_state": None,
            "transition_history": [],
            "updated_by": "system",
        }

    def transition_workflow_state(self, project_key, to_state, actor, reason=None):
        self.calls.append(("transition", project_key, to_state, actor, reason))
        return {
            "current_state": to_state,
            "previous_state": "initiating",
            "updated_by": actor,
            "transition_history": [],
        }

    def get_allowed_workflow_transitions(self, project):
        self.calls.append(("allowed", project))
        return {
            "current_state": "planning",
            "allowed_transitions": ["executing", "initiating"],
        }

    def get_audit_events(
        self,
        project_key,
        event_type=None,
        actor=None,
        since=None,
        until=None,
        limit=None,
        offset=None,
    ):
        self.calls.append(
            (
                "audit",
                project_key,
                event_type,
                actor,
                since,
                until,
                limit,
                offset,
            )
        )
        return {
            "events": [
                {
                    "event_id": "evt-1",
                    "event_type": "workflow_state_changed",
                    "actor": actor or "PM",
                    "timestamp": "2026-02-21T00:00:00Z",
                }
            ],
            "total": 1,
            "limit": limit or 100,
            "offset": offset or 0,
        }

    def close(self):
        return None


def _patch_output(monkeypatch):
    monkeypatch.setattr(workflow_commands, "print_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(workflow_commands, "print_json", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        workflow_commands, "print_success", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(workflow_commands, "print_info", lambda *args, **kwargs: None)


def test_workflow_state_command(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(workflow_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        workflow_commands.workflow_group,
        ["state", "--project", "P1"],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("state", "P1")


def test_workflow_transition_command(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(workflow_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        workflow_commands.workflow_group,
        [
            "transition",
            "--project",
            "P1",
            "--to-state",
            "planning",
            "--actor",
            "PM",
            "--reason",
            "Ready",
        ],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("transition", "P1", "planning", "PM", "Ready")


def test_workflow_allowed_transitions_command(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(workflow_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        workflow_commands.workflow_group,
        ["allowed-transitions", "--project", "P1"],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("allowed", "P1")


def test_workflow_audit_events_command_with_filters(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(workflow_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        workflow_commands.workflow_group,
        [
            "audit-events",
            "--project",
            "P1",
            "--event-type",
            "workflow_state_changed",
            "--actor",
            "PM",
            "--since",
            "2026-01-01T00:00:00Z",
            "--until",
            "2026-12-31T23:59:59Z",
            "--limit",
            "10",
            "--offset",
            "5",
        ],
    )

    assert result.exit_code == 0
    assert client.calls[0] == (
        "audit",
        "P1",
        "workflow_state_changed",
        "PM",
        "2026-01-01T00:00:00Z",
        "2026-12-31T23:59:59Z",
        10,
        5,
    )
