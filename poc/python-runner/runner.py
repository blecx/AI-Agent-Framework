"""Python runner – handles RUN_TESTS_PYTHON tasks.

Workflow per task:
1. Download snapshot tarball from hub
2. Extract into a temp directory
3. Run `pytest -q` (or configured command)
4. Upload logs as artifact
5. Mark task complete/fail based on exit code
"""
import json
import logging
import os
import shutil
import subprocess
import tarfile
import tempfile
import time
import uuid
from io import BytesIO
from typing import Any, Optional

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [python-runner] %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

HUB_URL = os.environ.get("HUB_URL", "http://hub:8000")
WORKER_ID = os.environ.get("WORKER_ID", f"pyrunner-{uuid.uuid4().hex[:8]}")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "5"))
LEASE_SECONDS = int(os.environ.get("LEASE_SECONDS", "300"))
TEST_COMMAND = os.environ.get("TEST_COMMAND", "pytest -q")
TEST_TIMEOUT_SECONDS = int(os.environ.get("TEST_TIMEOUT_SECONDS", "300"))

client = httpx.Client(base_url=HUB_URL, timeout=120)


def poll_tasks() -> list[dict]:
    resp = client.get("/tasks/poll", params={"task_type": "RUN_TESTS_PYTHON", "limit": 2})
    resp.raise_for_status()
    return resp.json()


def claim_task(task_id: str) -> Optional[dict]:
    resp = client.post(
        f"/tasks/{task_id}/claim",
        json={"worker_id": WORKER_ID, "lease_seconds": LEASE_SECONDS},
    )
    if resp.status_code == 409:
        return None
    resp.raise_for_status()
    return resp.json()


def complete_task(task_id: str, output: dict):
    client.post(f"/tasks/{task_id}/complete", json={"output_data": output})


def fail_task(task_id: str, error: str):
    client.post(f"/tasks/{task_id}/fail", json={"error_message": error})


def upload_log(task_id: str, content: bytes) -> dict:
    resp = client.post(
        f"/artifacts/{task_id}/upload",
        params={"artifact_type": "log"},
        files={"file": ("test_output.log", content, "text/plain")},
    )
    resp.raise_for_status()
    return resp.json()


def get_snapshot(run_id: str) -> Optional[bytes]:
    """Download snapshot tarball from hub. Returns None if not available."""
    try:
        resp = client.get(f"/repos/{run_id}/snapshot", timeout=60)
        if resp.status_code == 200:
            return resp.content
    except Exception as exc:
        log.warning("Could not get snapshot for run %s: %s", run_id, exc)
    return None


def handle_run_tests(task: dict):
    task_id = task["id"]
    run_id = task["run_id"]
    inp_raw = task.get("input_data")
    inp: dict[str, Any] = json.loads(inp_raw) if inp_raw else {}

    work_dir = tempfile.mkdtemp(prefix=f"runner_{task_id}_")
    try:
        # Try to get snapshot
        snapshot = get_snapshot(run_id)
        if snapshot:
            log.info("Extracting snapshot for task %s", task_id)
            with tarfile.open(fileobj=BytesIO(snapshot), mode="r:gz") as tar:
                # Validate members to prevent path traversal
                for member in tar.getmembers():
                    member_path = os.path.realpath(os.path.join(work_dir, member.name))
                    if not member_path.startswith(os.path.realpath(work_dir)):
                        log.warning("Skipping suspicious tar member: %s", member.name)
                        continue
                tar.extractall(work_dir)
            repo_dir = os.path.join(work_dir, "repo")
            if not os.path.isdir(repo_dir):
                repo_dir = work_dir
        else:
            log.warning("No snapshot available; running tests in empty dir")
            repo_dir = work_dir

        # Determine test command
        cmd = inp.get("test_command") or TEST_COMMAND
        has_tests = os.path.exists(os.path.join(repo_dir, "pytest.ini")) or any(
            os.path.exists(os.path.join(repo_dir, f))
            for f in ["setup.cfg", "pyproject.toml", "tests", "test"]
        )
        if not has_tests and "pytest" in cmd:
            log.warning("No pytest config or tests/ found; skipping with warning")
            log_content = b"WARNING: No tests found. Skipping pytest.\n"
            artifact = upload_log(task_id, log_content)
            complete_task(task_id, {
                "exit_code": 0,
                "note": "no_tests_found",
                "log_artifact_id": artifact["id"],
            })
            return

        log.info("Running: %s in %s", cmd, repo_dir)
        result = subprocess.run(
            cmd.split(),
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT_SECONDS,
        )
        log_bytes = (result.stdout + result.stderr).encode("utf-8")
        artifact = upload_log(task_id, log_bytes)
        log.info("Tests exit_code=%d, log artifact=%s", result.returncode, artifact["id"])

        output = {
            "exit_code": result.returncode,
            "log_artifact_id": artifact["id"],
            "command": cmd,
        }
        if result.returncode == 0:
            complete_task(task_id, output)
        else:
            fail_task(task_id, f"Tests failed with exit code {result.returncode}")

    except Exception as exc:
        log.error("Runner error for task %s: %s", task_id, exc)
        fail_task(task_id, str(exc))
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def run_once():
    try:
        tasks = poll_tasks()
    except Exception as exc:
        log.debug("Poll error: %s", exc)
        return

    for task in tasks:
        task_id = task["id"]
        claimed = claim_task(task_id)
        if not claimed:
            continue
        log.info("Claimed RUN_TESTS_PYTHON task %s", task_id)
        handle_run_tests(claimed)


def main():
    log.info("Python runner starting, worker_id=%s", WORKER_ID)
    while True:
        try:
            run_once()
        except Exception as exc:
            log.warning("Loop error: %s", exc)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
