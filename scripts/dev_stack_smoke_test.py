#!/usr/bin/env python3
"""Smoke test for dev_stack_supervisor.py.

Validates that the supervisor can:
1) Start backend + frontend on isolated ports.
2) Serve healthy endpoints.
3) Restart services when watched files change.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUPERVISOR = PROJECT_ROOT / "scripts" / "dev_stack_supervisor.py"
PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"

SMOKE_DIR = PROJECT_ROOT / ".tmp" / "dev-stack-smoke"
PID_FILE = SMOKE_DIR / "supervisor.pid"
SUPERVISOR_LOG = SMOKE_DIR / "supervisor.log"
BACKEND_LOG = SMOKE_DIR / "backend.log"
FRONTEND_LOG = SMOKE_DIR / "frontend.log"

BACKEND_PORT = 18000
FRONTEND_PORT = 15173

BACKEND_TOUCH = PROJECT_ROOT / "apps" / "api" / ".dev_stack_smoke_touch.py"
FRONTEND_TOUCH = (
    PROJECT_ROOT
    / "_external"
    / "AI-Agent-Framework-Client"
    / "client"
    / "src"
    / ".dev_stack_smoke_touch.ts"
)


def _is_url_ready(url: str, timeout_seconds: float = 2.0) -> bool:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return 200 <= response.status < 500
    except urllib.error.HTTPError as exc:
        return 200 <= exc.code < 500
    except Exception:
        return False


def _wait_for_url(url: str, timeout_seconds: int = 90) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if _is_url_ready(url):
            return True
        time.sleep(1)
    return False


def _wait_for_log_contains(log_path: Path, text: str, timeout_seconds: int = 45) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if log_path.exists() and text in log_path.read_text(encoding="utf-8", errors="ignore"):
            return True
        time.sleep(1)
    return False


def _cleanup_files() -> None:
    BACKEND_TOUCH.unlink(missing_ok=True)
    FRONTEND_TOUCH.unlink(missing_ok=True)


def main() -> int:
    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    _cleanup_files()

    env = dict(os.environ)
    env.update(
        {
            "DEV_STACK_BACKEND_HOST": "127.0.0.1",
            "DEV_STACK_BACKEND_PORT": str(BACKEND_PORT),
            "DEV_STACK_FRONTEND_HOST": "127.0.0.1",
            "DEV_STACK_FRONTEND_PORT": str(FRONTEND_PORT),
            "DEV_STACK_PID_FILE": str(PID_FILE),
            "DEV_STACK_SUPERVISOR_LOG": str(SUPERVISOR_LOG),
            "DEV_STACK_BACKEND_LOG": str(BACKEND_LOG),
            "DEV_STACK_FRONTEND_LOG": str(FRONTEND_LOG),
        }
    )

    print("[smoke] starting isolated dev stack supervisor...")
    proc = subprocess.Popen(
        [str(PYTHON), "-u", str(SUPERVISOR)],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        backend_ok = _wait_for_url(f"http://127.0.0.1:{BACKEND_PORT}/health", timeout_seconds=90)
        frontend_ok = _wait_for_url(f"http://127.0.0.1:{FRONTEND_PORT}", timeout_seconds=120)

        if not backend_ok or not frontend_ok:
            print("[smoke] failed: stack did not become healthy in time")
            return 1

        print("[smoke] stack health checks passed")

        BACKEND_TOUCH.write_text("SMOKE = True\n", encoding="utf-8")
        FRONTEND_TOUCH.write_text("export const DEV_STACK_SMOKE = true\n", encoding="utf-8")

        backend_restarted = _wait_for_log_contains(
            SUPERVISOR_LOG,
            "backend files changed, restarting backend",
            timeout_seconds=45,
        )
        frontend_restarted = _wait_for_log_contains(
            SUPERVISOR_LOG,
            "frontend files changed, restarting frontend",
            timeout_seconds=60,
        )

        if not backend_restarted or not frontend_restarted:
            print("[smoke] failed: restart-on-save not observed in supervisor log")
            return 1

        print("[smoke] restart-on-save checks passed")
        print("[smoke] PASS")
        return 0
    finally:
        _cleanup_files()
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
