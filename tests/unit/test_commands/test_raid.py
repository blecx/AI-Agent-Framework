import sys
from pathlib import Path

from click.testing import CliRunner

ROOT_DIR = Path(__file__).resolve().parents[3]
TUI_DIR = ROOT_DIR / "apps" / "tui"
if str(TUI_DIR) not in sys.path:
    sys.path.insert(0, str(TUI_DIR))

from commands import raid as raid_commands


class DummyClient:
    def __init__(self):
        self.calls = []

    def list_raid_items(
        self, project, raid_type=None, status=None, owner=None, priority=None
    ):
        self.calls.append(("list", project, raid_type, status, owner, priority))
        return {"items": [{"id": "RISK001", "title": "Risk"}], "total": 1}

    def get_raid_item(self, project, raid_id):
        self.calls.append(("get", project, raid_id))
        return {"id": raid_id, "title": "Risk"}

    def create_raid_item(self, **kwargs):
        self.calls.append(("add", kwargs))
        return {"id": "RISK001", **kwargs}

    def update_raid_item(self, project, raid_id, updates):
        self.calls.append(("update", project, raid_id, updates))
        return {"id": raid_id, **updates}

    def delete_raid_item(self, project, raid_id):
        self.calls.append(("delete", project, raid_id))
        return {"message": "deleted"}

    def close(self):
        return None


def _patch_output(monkeypatch):
    monkeypatch.setattr(raid_commands, "print_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(raid_commands, "print_json", lambda *args, **kwargs: None)
    monkeypatch.setattr(raid_commands, "print_success", lambda *args, **kwargs: None)
    monkeypatch.setattr(raid_commands, "print_info", lambda *args, **kwargs: None)
    monkeypatch.setattr(raid_commands, "print_error", lambda *args, **kwargs: None)


def test_raid_list_command(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(raid_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        raid_commands.raid_group,
        [
            "list",
            "--project",
            "P1",
            "--type",
            "risk",
            "--status",
            "open",
            "--owner",
            "PM",
            "--priority",
            "high",
        ],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("list", "P1", "risk", "open", "PM", "high")


def test_raid_get_command(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(raid_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        raid_commands.raid_group,
        ["get", "--project", "P1", "--id", "RISK001"],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("get", "P1", "RISK001")


def test_raid_add_command(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(raid_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        raid_commands.raid_group,
        [
            "add",
            "--project",
            "P1",
            "--type",
            "risk",
            "--title",
            "Risk",
            "--description",
            "Desc",
            "--owner",
            "PM",
            "--priority",
            "high",
            "--status",
            "open",
        ],
    )

    assert result.exit_code == 0
    assert client.calls[0][0] == "add"
    assert client.calls[0][1]["project_key"] == "P1"


def test_raid_update_command(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(raid_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        raid_commands.raid_group,
        [
            "update",
            "--project",
            "P1",
            "--id",
            "RISK001",
            "--status",
            "in_progress",
            "--owner",
            "Alice",
        ],
    )

    assert result.exit_code == 0
    assert client.calls[0] == (
        "update",
        "P1",
        "RISK001",
        {"owner": "Alice", "status": "in_progress"},
    )


def test_raid_update_requires_fields(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(raid_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        raid_commands.raid_group,
        ["update", "--project", "P1", "--id", "RISK001"],
    )

    assert result.exit_code == 0
    assert client.calls == []


def test_raid_delete_command(monkeypatch):
    client = DummyClient()
    _patch_output(monkeypatch)
    monkeypatch.setattr(raid_commands, "APIClient", lambda: client)

    result = CliRunner().invoke(
        raid_commands.raid_group,
        ["delete", "--project", "P1", "--id", "RISK001"],
    )

    assert result.exit_code == 0
    assert client.calls[0] == ("delete", "P1", "RISK001")
