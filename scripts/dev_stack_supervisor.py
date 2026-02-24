#!/usr/bin/env python3
"""Development stack supervisor.

Starts backend API + UX frontend, keeps both alive, and restarts affected service
when watched files change.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = PROJECT_ROOT / ".tmp"


def _env_path(name: str, default_path: Path) -> Path:
    value = os.environ.get(name)
    if not value:
        return default_path
    path = Path(value)
    if not path.is_absolute():
        return PROJECT_ROOT / path
    return path


BACKEND_HOST = os.environ.get("DEV_STACK_BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.environ.get("DEV_STACK_BACKEND_PORT", "8000"))
FRONTEND_HOST = os.environ.get("DEV_STACK_FRONTEND_HOST", "127.0.0.1")
FRONTEND_PORT = int(os.environ.get("DEV_STACK_FRONTEND_PORT", "5173"))

PID_FILE = _env_path("DEV_STACK_PID_FILE", TMP_DIR / "dev-stack-supervisor.pid")
SUPERVISOR_LOG = _env_path("DEV_STACK_SUPERVISOR_LOG", TMP_DIR / "dev-stack-supervisor.log")

BACKEND_PATTERNS = [
    "apps/api/**/*.py",
    "apps/api/requirements.txt",
    "requirements.txt",
    "configs/**/*.json",
]

FRONTEND_PATTERNS = [
    "_external/AI-Agent-Framework-Client/client/src/**/*",
    "_external/AI-Agent-Framework-Client/client/public/**/*",
    "_external/AI-Agent-Framework-Client/client/vite.config.*",
    "_external/AI-Agent-Framework-Client/client/package.json",
    "_external/AI-Agent-Framework-Client/client/tsconfig*.json",
    "_external/AI-Agent-Framework-Client/client/.env*",
]


def _is_pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _ensure_single_instance() -> None:
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)

    if PID_FILE.exists():
        raw = PID_FILE.read_text(encoding="utf-8").strip()
        if raw.isdigit() and _is_pid_running(int(raw)):
            print(f"dev-stack-supervisor already running (pid={raw})", flush=True)
            sys.exit(0)
        PID_FILE.unlink(missing_ok=True)

    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")


def _iter_files(patterns: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        for path in PROJECT_ROOT.glob(pattern):
            if path.is_file():
                files.append(path)
    return files


def _snapshot(patterns: Iterable[str]) -> dict[str, tuple[int, int]]:
    snap: dict[str, tuple[int, int]] = {}
    for path in _iter_files(patterns):
        stat = path.stat()
        snap[str(path)] = (stat.st_mtime_ns, stat.st_size)
    return snap


def _open_log(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return open(path, "a", encoding="utf-8")


def _backend_process() -> subprocess.Popen:
    backend_cwd = PROJECT_ROOT / "apps" / "api"
    venv_python = PROJECT_ROOT / ".venv" / "bin" / "python"
    backend_log = _env_path("DEV_STACK_BACKEND_LOG", TMP_DIR / "dev-backend.log")

    (PROJECT_ROOT / "projectDocs").mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["PROJECT_DOCS_PATH"] = "../../projectDocs"

    log_file = _open_log(backend_log)
    return subprocess.Popen(
        [
            str(venv_python),
            "-m",
            "uvicorn",
            "main:app",
            "--reload",
            "--host",
            BACKEND_HOST,
            "--port",
            str(BACKEND_PORT),
        ],
        cwd=str(backend_cwd),
        env=env,
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
    )


def _frontend_process() -> subprocess.Popen:
    frontend_cwd = PROJECT_ROOT / "_external" / "AI-Agent-Framework-Client" / "client"
    frontend_log = _env_path("DEV_STACK_FRONTEND_LOG", TMP_DIR / "dev-frontend.log")

    log_file = _open_log(frontend_log)
    return subprocess.Popen(
        [
            "npm",
            "run",
            "dev",
            "--",
            "--host",
            FRONTEND_HOST,
            "--port",
            str(FRONTEND_PORT),
        ],
        cwd=str(frontend_cwd),
        env=dict(os.environ),
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
    )


def _stop_process(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=10)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def main() -> int:
    _ensure_single_instance()
    log = _open_log(SUPERVISOR_LOG)

    stop_requested = False

    def _signal_handler(_signum, _frame):
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    backend = _backend_process()
    frontend = _frontend_process()

    backend_snapshot = _snapshot(BACKEND_PATTERNS)
    frontend_snapshot = _snapshot(FRONTEND_PATTERNS)

    print(f"dev-stack-supervisor started (pid={os.getpid()})", flush=True)
    print(f"backend: http://{BACKEND_HOST}:{BACKEND_PORT}/health", flush=True)
    print(f"frontend: http://{FRONTEND_HOST}:{FRONTEND_PORT}", flush=True)
    log.write(f"[{time.ctime()}] supervisor started pid={os.getpid()}\n")
    log.flush()

    try:
        while not stop_requested:
            if backend.poll() is not None:
                log.write(f"[{time.ctime()}] backend exited, restarting\n")
                log.flush()
                backend = _backend_process()
                backend_snapshot = _snapshot(BACKEND_PATTERNS)

            if frontend.poll() is not None:
                log.write(f"[{time.ctime()}] frontend exited, restarting\n")
                log.flush()
                frontend = _frontend_process()
                frontend_snapshot = _snapshot(FRONTEND_PATTERNS)

            current_backend = _snapshot(BACKEND_PATTERNS)
            if current_backend != backend_snapshot:
                log.write(f"[{time.ctime()}] backend files changed, restarting backend\n")
                log.flush()
                _stop_process(backend)
                backend = _backend_process()
                backend_snapshot = current_backend

            current_frontend = _snapshot(FRONTEND_PATTERNS)
            if current_frontend != frontend_snapshot:
                log.write(
                    f"[{time.ctime()}] frontend files changed, restarting frontend\n"
                )
                log.flush()
                _stop_process(frontend)
                frontend = _frontend_process()
                frontend_snapshot = current_frontend

            time.sleep(1.0)
    finally:
        _stop_process(backend)
        _stop_process(frontend)
        PID_FILE.unlink(missing_ok=True)
        log.write(f"[{time.ctime()}] supervisor stopped\n")
        log.flush()
        log.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
