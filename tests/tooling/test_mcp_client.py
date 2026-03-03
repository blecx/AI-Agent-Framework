"""Unit tests for MCPMultiClient — MAESTRO unified MCP client.

Uses unittest.mock to simulate httpx responses — no live MCP servers needed.
Tests cover: connect, list_tools, call_tool routing, error cases, context manager.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx

from agents.mcp_client import (
    MCPMultiClient,
    ToolInfo,
    ToolNotFoundError,
    ToolConflictError,
    MCPCallError,
)


# ---------------------------------------------------------------------------
# Helpers to build fake httpx responses
# ---------------------------------------------------------------------------


_DUMMY_REQUEST = httpx.Request("POST", "http://localhost/mcp")


def _json_response(data: Any, status_code: int = 200) -> httpx.Response:
    """Build a mock httpx.Response with JSON body (request attached for raise_for_status)."""
    content = json.dumps(data).encode()
    return httpx.Response(
        status_code=status_code,
        content=content,
        headers={"content-type": "application/json"},
        request=_DUMMY_REQUEST,
    )


def _rpc_ok(result: Any, req_id: int = 1) -> dict[str, Any]:
    """Wrap a result in a JSON-RPC 2.0 success envelope."""
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _rpc_error(code: int, message: str, req_id: int = 1) -> dict[str, Any]:
    """Wrap an error in a JSON-RPC 2.0 error envelope."""
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _tools_list_response(*tool_names: str) -> dict[str, Any]:
    """Build a tools/list JSON-RPC result with given tool names."""
    return _rpc_ok({
        "tools": [
            {"name": name, "description": f"Tool {name}", "inputSchema": {}}
            for name in tool_names
        ]
    })


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def two_servers() -> list[dict[str, str]]:
    return [
        {"name": "memory", "url": "http://localhost:3030"},
        {"name": "bus", "url": "http://localhost:3031"},
    ]


# ---------------------------------------------------------------------------
# connect() — fetches tool manifests on startup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_connect_fetches_tools_from_all_servers(two_servers):
    """connect() loads all tools from all servers into _tools map."""
    responses = [
        _json_response(_tools_list_response("memory_store_lesson", "memory_get_lessons")),
        _json_response(_tools_list_response("bus_create_run", "bus_set_status")),
    ]
    mock_http = AsyncMock()
    mock_http.post = AsyncMock(side_effect=responses)

    client = MCPMultiClient(two_servers)
    with patch("agents.mcp_client.httpx.AsyncClient", return_value=mock_http):
        await client.connect()

    tools = client.list_tools()
    names = {t.name for t in tools}
    assert "memory_store_lesson" in names
    assert "memory_get_lessons" in names
    assert "bus_create_run" in names
    assert "bus_set_status" in names
    await client.close()


@pytest.mark.asyncio
async def test_connect_assigns_correct_server_to_tool():
    """Each tool is assigned to the correct server."""
    servers = [{"name": "memory", "url": "http://localhost:3030"}]
    client = MCPMultiClient(servers)
    client._http = AsyncMock()
    client._http.post = AsyncMock(return_value=_json_response(
        _tools_list_response("memory_store_lesson")
    ))

    tools = await client._fetch_tools("http://localhost:3030", "memory")
    assert len(tools) == 1
    assert tools[0].server_name == "memory"
    assert tools[0].server_url == "http://localhost:3030"
    assert tools[0].name == "memory_store_lesson"


# ---------------------------------------------------------------------------
# list_tools()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_tools_returns_all_tools():
    """list_tools() returns flat list of all tools from all servers."""
    client = MCPMultiClient([])
    client._tools = {
        "tool_a": ToolInfo("tool_a", "desc a", "server1", "http://s1"),
        "tool_b": ToolInfo("tool_b", "desc b", "server2", "http://s2"),
    }
    tools = client.list_tools()
    assert len(tools) == 2
    names = {t.name for t in tools}
    assert names == {"tool_a", "tool_b"}


def test_list_tools_empty_before_connect():
    """Before connect(), list_tools() returns empty list."""
    client = MCPMultiClient([{"name": "memory", "url": "http://localhost:3030"}])
    assert client.list_tools() == []


# ---------------------------------------------------------------------------
# get_tool()
# ---------------------------------------------------------------------------


def test_get_tool_returns_correct_info():
    client = MCPMultiClient([])
    client._tools = {
        "bus_create_run": ToolInfo("bus_create_run", "Create a run", "bus", "http://bus"),
    }
    t = client.get_tool("bus_create_run")
    assert t.name == "bus_create_run"
    assert t.server_name == "bus"


def test_get_tool_raises_for_unknown_tool():
    client = MCPMultiClient([])
    with pytest.raises(ToolNotFoundError):
        client.get_tool("nonexistent_tool")


# ---------------------------------------------------------------------------
# call_tool() — routing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_call_tool_routes_to_correct_server():
    """call_tool() sends the request to the server that owns the tool."""
    client = MCPMultiClient([])
    client._tools = {
        "memory_store_lesson": ToolInfo("memory_store_lesson", "", "memory", "http://memory:3030"),
        "bus_create_run": ToolInfo("bus_create_run", "", "bus", "http://bus:3031"),
    }
    client._http = AsyncMock()

    memory_response = _json_response(_rpc_ok({"ok": True, "lesson_id": 1}))
    bus_response = _json_response(_rpc_ok({"run_id": "abc-123"}))

    call_counter = {"memory": 0, "bus": 0}

    async def mock_post(url: str, **kwargs):
        if "memory" in url:
            call_counter["memory"] += 1
            return memory_response
        else:
            call_counter["bus"] += 1
            return bus_response

    client._http.post = mock_post

    result = await client.call_tool("memory_store_lesson", {"issue_number": 42, "outcome": "success", "summary": "test", "learnings": []})
    assert result == {"ok": True, "lesson_id": 1}
    assert call_counter["memory"] == 1
    assert call_counter["bus"] == 0

    result2 = await client.call_tool("bus_create_run", {"issue_number": 42})
    assert result2 == {"run_id": "abc-123"}
    assert call_counter["bus"] == 1


@pytest.mark.asyncio
async def test_call_tool_raises_tool_not_found():
    """call_tool() raises ToolNotFoundError for unregistered tools."""
    client = MCPMultiClient([])
    client._tools = {}
    client._http = AsyncMock()

    with pytest.raises(ToolNotFoundError):
        await client.call_tool("nonexistent_tool", {})


@pytest.mark.asyncio
async def test_call_tool_raises_mcp_error_on_rpc_error():
    """call_tool() raises MCPCallError when server returns JSON-RPC error."""
    client = MCPMultiClient([])
    client._tools = {
        "failing_tool": ToolInfo("failing_tool", "", "server", "http://server"),
    }
    client._http = AsyncMock()
    client._http.post = AsyncMock(return_value=_json_response(
        _rpc_error(-32601, "Method not found")
    ))

    with pytest.raises(MCPCallError, match="Method not found"):
        await client.call_tool("failing_tool", {})


@pytest.mark.asyncio
async def test_call_tool_raises_mcp_error_on_http_error():
    """call_tool() raises MCPCallError on HTTP failure."""
    client = MCPMultiClient([])
    client._tools = {
        "my_tool": ToolInfo("my_tool", "", "server", "http://server"),
    }
    client._http = AsyncMock()
    client._http.post = AsyncMock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    with pytest.raises(MCPCallError):
        await client.call_tool("my_tool", {})


# ---------------------------------------------------------------------------
# ToolConflictError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_conflict_error_when_two_servers_expose_same_tool():
    """connect() raises ToolConflictError if two servers expose a tool with the same name."""
    servers = [
        {"name": "server_a", "url": "http://localhost:3030"},
        {"name": "server_b", "url": "http://localhost:3031"},
    ]
    client = MCPMultiClient(servers)
    client._http = AsyncMock()

    # Both servers expose "shared_tool"
    both_expose = _json_response(_tools_list_response("shared_tool"))
    client._http.post = AsyncMock(return_value=both_expose)

    # Manually run the connect logic to trigger conflict
    client._tools = {}
    tools_a = await client._fetch_tools("http://localhost:3030", "server_a")
    for t in tools_a:
        client._tools[t.name] = t

    with pytest.raises(ToolConflictError, match="shared_tool"):
        tools_b = await client._fetch_tools("http://localhost:3031", "server_b")
        for t in tools_b:
            if t.name in client._tools:
                existing = client._tools[t.name]
                raise ToolConflictError(
                    f"Tool '{t.name}' is exposed by both "
                    f"'{existing.server_name}' and '{t.server_name}'."
                )


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_context_manager_calls_close_on_exit():
    """async with MCPMultiClient(...) calls close() on exit."""
    servers = [{"name": "memory", "url": "http://localhost:3030"}]
    client = MCPMultiClient(servers)

    mock_http = AsyncMock()
    mock_http.post = AsyncMock(return_value=_json_response(_tools_list_response()))
    mock_http.aclose = AsyncMock()

    with patch("agents.mcp_client.httpx.AsyncClient", return_value=mock_http):
        async with client:
            pass

    mock_http.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_context_manager_http_is_none_after_close():
    """After close(), _http is set to None."""
    client = MCPMultiClient([])
    client._http = AsyncMock()
    client._http.aclose = AsyncMock()
    await client.close()
    assert client._http is None
