import sys
from pathlib import Path

import httpx
import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
TUI_DIR = ROOT_DIR / "apps" / "tui"
if str(TUI_DIR) not in sys.path:
    sys.path.insert(0, str(TUI_DIR))

from api_client import APIClient


class DummyHTTPClient:
    def __init__(self):
        self.calls = []
        self.closed = False

    def get(self, url, params=None):
        self.calls.append(("get", url, params))
        return httpx.Response(200, request=httpx.Request("GET", url), json={"ok": True})

    def post(self, url, json=None, params=None):
        payload = json if json is not None else params
        self.calls.append(("post", url, payload))
        return httpx.Response(
            200, request=httpx.Request("POST", url), json={"ok": True}
        )

    def put(self, url, json=None):
        self.calls.append(("put", url, json))
        return httpx.Response(200, request=httpx.Request("PUT", url), json={"ok": True})

    def patch(self, url, json=None):
        self.calls.append(("patch", url, json))
        return httpx.Response(
            200,
            request=httpx.Request("PATCH", url),
            json={"ok": True},
        )

    def delete(self, url):
        self.calls.append(("delete", url, None))
        if "/raid/" in url:
            return httpx.Response(
                200,
                request=httpx.Request("DELETE", url),
                json={"message": "deleted"},
            )
        return httpx.Response(204, request=httpx.Request("DELETE", url), content=b"")

    def close(self):
        self.closed = True


def _client() -> tuple[APIClient, DummyHTTPClient]:
    client = APIClient(base_url="http://api.local", timeout=5)
    dummy = DummyHTTPClient()
    client.client = dummy
    return client, dummy


def test_create_project_with_description_includes_payload():
    client, dummy = _client()

    client.create_project("P1", "Proj", "Desc")

    method, url, payload = dummy.calls[0]
    assert method == "post"
    assert url.endswith("/projects")
    assert payload == {"key": "P1", "name": "Proj", "description": "Desc"}


def test_health_check_and_project_queries_use_expected_paths():
    client, dummy = _client()

    client.health_check()
    client.list_projects()
    client.get_project("P1")

    assert dummy.calls[0] == ("get", "http://api.local/health", None)
    assert dummy.calls[1] == ("get", "http://api.local/projects", None)
    assert dummy.calls[2] == ("get", "http://api.local/projects/P1/state", None)


def test_create_project_without_description_omits_field():
    client, dummy = _client()

    client.create_project("P1", "Proj")

    _, _, payload = dummy.calls[0]
    assert payload == {"key": "P1", "name": "Proj"}


def test_delete_project_handles_empty_body_response():
    client, dummy = _client()

    result = client.delete_project("P1")

    assert result == {}
    assert dummy.calls[0][0] == "delete"


def test_list_raid_items_builds_query_params():
    client, dummy = _client()

    client.list_raid_items(
        "P1",
        raid_type="risk",
        status="open",
        owner="PM",
        priority="high",
    )

    method, url, params = dummy.calls[0]
    assert method == "get"
    assert url.endswith("/projects/P1/raid")
    assert params == {
        "type": "risk",
        "status": "open",
        "owner": "PM",
        "priority": "high",
    }


def test_list_raid_items_without_filters_uses_no_params():
    client, dummy = _client()

    client.list_raid_items("P1")

    assert dummy.calls[0] == ("get", "http://api.local/projects/P1/raid", None)


def test_command_and_artifact_methods_use_expected_payloads():
    client, dummy = _client()

    client.propose_command("P1", "assess_gaps", {"depth": "full"})
    client.propose_command("P1", "assess_gaps")
    client.apply_command("P1", "prop-1")
    client.list_artifacts("P1")
    client.get_artifact("P1", "artifacts/a.md")

    assert dummy.calls[0] == (
        "post",
        "http://api.local/projects/P1/commands/propose",
        {"command": "assess_gaps", "params": {"depth": "full"}},
    )
    assert dummy.calls[1] == (
        "post",
        "http://api.local/projects/P1/commands/propose",
        {"command": "assess_gaps"},
    )
    assert dummy.calls[2] == (
        "post",
        "http://api.local/projects/P1/commands/apply",
        {"proposal_id": "prop-1"},
    )
    assert dummy.calls[3] == ("get", "http://api.local/projects/P1/artifacts", None)
    assert dummy.calls[4] == (
        "get",
        "http://api.local/projects/P1/artifacts/artifacts/a.md",
        None,
    )


def test_proposal_methods_use_expected_paths_payloads_and_filters():
    client, dummy = _client()

    client.list_proposals(
        project_key="P1",
        status_filter="pending",
        change_type="update",
    )
    client.list_proposals(project_key="P1")
    client.get_proposal("P1", "prop-1")
    client.apply_proposal("P1", "prop-1")
    client.reject_proposal("P1", "prop-1", "Not aligned")

    assert dummy.calls[0] == (
        "get",
        "http://api.local/projects/P1/proposals",
        {
            "status_filter": "pending",
            "change_type": "update",
        },
    )
    assert dummy.calls[1] == ("get", "http://api.local/projects/P1/proposals", None)
    assert dummy.calls[2] == (
        "get",
        "http://api.local/projects/P1/proposals/prop-1",
        None,
    )
    assert dummy.calls[3] == (
        "post",
        "http://api.local/projects/P1/proposals/prop-1/apply",
        None,
    )
    assert dummy.calls[4] == (
        "post",
        "http://api.local/projects/P1/proposals/prop-1/reject",
        {"reason": "Not aligned"},
    )


def test_raid_crud_methods_use_expected_payloads_and_paths():
    client, dummy = _client()

    client.get_raid_item("P1", "RISK001")
    client.create_raid_item(
        project_key="P1",
        raid_type="risk",
        title="Risk",
        description="Desc",
        owner="PM",
    )
    client.create_raid_item(
        project_key="P1",
        raid_type="issue",
        title="Issue",
        description="Desc",
        owner="Lead",
        priority="high",
        status="open",
    )
    client.update_raid_item("P1", "RISK001", {"status": "closed"})
    client.delete_raid_item("P1", "RISK001")

    assert dummy.calls[0] == ("get", "http://api.local/projects/P1/raid/RISK001", None)
    assert dummy.calls[1] == (
        "post",
        "http://api.local/projects/P1/raid",
        {
            "type": "risk",
            "title": "Risk",
            "description": "Desc",
            "owner": "PM",
        },
    )
    assert dummy.calls[2] == (
        "post",
        "http://api.local/projects/P1/raid",
        {
            "type": "issue",
            "title": "Issue",
            "description": "Desc",
            "owner": "Lead",
            "priority": "high",
            "status": "open",
        },
    )
    assert dummy.calls[3] == (
        "put",
        "http://api.local/projects/P1/raid/RISK001",
        {"status": "closed"},
    )
    assert dummy.calls[4] == (
        "delete",
        "http://api.local/projects/P1/raid/RISK001",
        None,
    )


def test_workflow_methods_use_expected_paths_and_payloads():
    client, dummy = _client()

    client.get_workflow_state("P1")
    client.transition_workflow_state(
        project_key="P1",
        to_state="planning",
        actor="PM",
        reason="Kickoff approved",
    )
    client.transition_workflow_state(
        project_key="P1",
        to_state="executing",
        actor="PM",
    )
    client.get_allowed_workflow_transitions("P1")
    client.get_audit_events(
        project_key="P1",
        event_type="workflow_state_changed",
        actor="PM",
        since="2026-01-01T00:00:00Z",
        until="2026-12-31T23:59:59Z",
        limit=10,
        offset=5,
    )
    client.get_audit_events(project_key="P1")
    client.run_audit("P1")
    client.run_audit("P1", rule_set=["required_fields", "workflow_state"])

    assert dummy.calls[0] == (
        "get",
        "http://api.local/projects/P1/workflow/state",
        None,
    )
    assert dummy.calls[1] == (
        "patch",
        "http://api.local/projects/P1/workflow/state",
        {
            "to_state": "planning",
            "actor": "PM",
            "reason": "Kickoff approved",
        },
    )
    assert dummy.calls[2] == (
        "patch",
        "http://api.local/projects/P1/workflow/state",
        {
            "to_state": "executing",
            "actor": "PM",
        },
    )
    assert dummy.calls[3] == (
        "get",
        "http://api.local/projects/P1/workflow/allowed-transitions",
        None,
    )
    assert dummy.calls[4] == (
        "get",
        "http://api.local/projects/P1/audit-events",
        {
            "event_type": "workflow_state_changed",
            "actor": "PM",
            "since": "2026-01-01T00:00:00Z",
            "until": "2026-12-31T23:59:59Z",
            "limit": 10,
            "offset": 5,
        },
    )
    assert dummy.calls[5] == (
        "get",
        "http://api.local/projects/P1/audit-events",
        None,
    )
    assert dummy.calls[6] == (
        "post",
        "http://api.local/projects/P1/audit",
        None,
    )
    assert dummy.calls[7] == (
        "post",
        "http://api.local/projects/P1/audit",
        {"rule_set": ["required_fields", "workflow_state"]},
    )


def test_handle_response_http_error_exits(monkeypatch):
    client, _ = _client()
    captured = []
    monkeypatch.setattr(
        "api_client.print_error", lambda message: captured.append(message)
    )

    response = httpx.Response(
        400,
        request=httpx.Request("GET", "http://api.local/test"),
        json={"detail": "bad request"},
    )

    with pytest.raises(SystemExit):
        client._handle_response(response)

    assert any("HTTP 400" in message for message in captured)
    assert any("bad request" in message for message in captured)


def test_handle_response_http_error_fallback_to_text(monkeypatch):
    client, _ = _client()
    captured = []
    monkeypatch.setattr(
        "api_client.print_error", lambda message: captured.append(message)
    )

    response = httpx.Response(
        500,
        request=httpx.Request("GET", "http://api.local/test"),
        text="server exploded",
    )

    with pytest.raises(SystemExit):
        client._handle_response(response)

    assert any("HTTP 500" in message for message in captured)
    assert any("server exploded" in message for message in captured)


def test_handle_response_request_error_exits(monkeypatch):
    client, _ = _client()
    captured = []
    monkeypatch.setattr(
        "api_client.print_error", lambda message: captured.append(message)
    )

    class BrokenResponse:
        status_code = 0
        text = ""

        def raise_for_status(self):
            raise httpx.RequestError(
                "network down",
                request=httpx.Request("GET", "http://api.local"),
            )

        def json(self):
            return {}

    with pytest.raises(SystemExit):
        client._handle_response(BrokenResponse())

    assert any("Connection error" in message for message in captured)


def test_close_delegates_to_http_client():
    client, dummy = _client()

    client.close()

    assert dummy.closed is True
