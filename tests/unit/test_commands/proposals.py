import sys
from pathlib import Path

from click.testing import CliRunner

ROOT_DIR = Path(__file__).resolve().parents[3]
TUI_DIR = ROOT_DIR / "apps" / "tui"
if str(TUI_DIR) not in sys.path:
    sys.path.insert(0, str(TUI_DIR))

from commands import proposals as proposals_commands


class DummyClient:
    def __init__(self):
        self.calls = []

    def list_proposals(self, project_key, status_filter=None, change_type=None):
        self.calls.append(("list", project_key, status_filter, change_type))
        return [
            {
                "id": "prop-1",
                "status": status_filter or "pending",
                "change_type": change_type or "update",
                "target_artifact": "artifacts/project_plan.md",
                "author": "PM",
                "created_at": "2026-02-21T00:00:00Z",
            }
        ]

    def get_proposal(self, project_key, proposal_id):
        self.calls.append(("get", project_key, proposal_id))
        return {
            "id": proposal_id,
            "project_key": project_key,
            "status": "pending",
        }

    def apply_proposal(self, project_key, proposal_id):
        self.calls.append(("apply", project_key, proposal_id))
        return {
            "message": "Proposal applied",
            "proposal_id": proposal_id,
        }

    def reject_proposal(self, project_key, proposal_id, reason):
        self.calls.append(("reject", project_key, proposal_id, reason))
        return {
            "message": "Proposal rejected",
            "proposal_id": proposal_id,
            "reason": reason,
        }

    def close(self):
        return None


class EmptyListClient(DummyClient):
    def list_proposals(self, project_key, status_filter=None, change_type=None):
        self.calls.append(("list", project_key, status_filter, change_type))
        return []


def _patch_output(monkeypatch):
    monkeypatch.setattr(proposals_commands, "print_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(proposals_commands, "print_json", lambda *args, **kwargs: None)
    monkeypatch.setattr(proposals_commands, "print_info", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        proposals_commands, "print_success", lambda *args, **kwargs: None
    )


def test_proposals_list_with_filters(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(proposals_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        proposals_commands.proposals_group,
        [
            "list",
            "--project",
            "P1",
            "--status",
            "pending",
            "--change-type",
            "update",
        ],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("list", "P1", "pending", "update")


def test_proposals_list_without_results(monkeypatch):
    client = EmptyListClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(proposals_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        proposals_commands.proposals_group,
        ["list", "--project", "P1"],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("list", "P1", None, None)


def test_proposals_get(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(proposals_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        proposals_commands.proposals_group,
        ["get", "--project", "P1", "--id", "prop-1"],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("get", "P1", "prop-1")


def test_proposals_apply(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(proposals_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        proposals_commands.proposals_group,
        ["apply", "--project", "P1", "--id", "prop-1"],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("apply", "P1", "prop-1")


def test_proposals_reject_requires_reason(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(proposals_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        proposals_commands.proposals_group,
        ["reject", "--project", "P1", "--id", "prop-1"],
    )

    assert result.exit_code != 0
    assert "Missing option '--reason'" in result.output


def test_proposals_reject(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(proposals_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        proposals_commands.proposals_group,
        [
            "reject",
            "--project",
            "P1",
            "--id",
            "prop-1",
            "--reason",
            "Out of scope",
        ],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("reject", "P1", "prop-1", "Out of scope")
