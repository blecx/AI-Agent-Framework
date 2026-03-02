"""Public fixture-helper API for TUI E2E tests.

This module is the canonical entry-point referenced by issue #680.
It re-exports all deterministic helper utilities from :mod:`e2e.tui.helpers`
so that test code can import from a single, stable location::

    from e2e.tui.fixture_helper import build_tui_workspace, reset_tui_workspace

All symbols remain available via :mod:`e2e.tui.helpers` for backward
compatibility.
"""

from __future__ import annotations

from e2e.tui.helpers import (  # noqa: F401  (re-exported public API)
    TuiE2EWorkspace,
    build_tui_workspace,
    reset_tui_workspace,
    reserve_local_port,
    resolve_python_executable,
    start_backend_server,
    stop_backend_server,
    wait_for_http_ok,
    write_json,
)

__all__ = [
    "TuiE2EWorkspace",
    "build_tui_workspace",
    "reset_tui_workspace",
    "reserve_local_port",
    "resolve_python_executable",
    "start_backend_server",
    "stop_backend_server",
    "wait_for_http_ok",
    "write_json",
]
