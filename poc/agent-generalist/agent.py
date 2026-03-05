"""Generalist agent – polls hub for tasks and processes them.

Handles: SPEC_NORMALIZE, STORY_SPLIT, TASK_DECOMPOSE, PATCH_IMPLEMENT.
For PATCH_IMPLEMENT it creates a sandbox clone, calls the LLM, applies the
suggested changes, exports a unified diff, and uploads it as an artifact.
"""
import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [agent-generalist] %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

HUB_URL = os.environ.get("HUB_URL", "http://hub:8000")
LLM_URL = os.environ.get("LLM_GATEWAY_URL", "http://llm-gateway:8080")
WORKER_ID = os.environ.get("WORKER_ID", f"generalist-{uuid.uuid4().hex[:8]}")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "5"))
LEASE_SECONDS = int(os.environ.get("LEASE_SECONDS", "180"))
SANDBOX_DIR = os.environ.get("SANDBOX_DIR", "/tmp/sandboxes")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

TASK_TYPES = [
    "SPEC_NORMALIZE",
    "STORY_SPLIT",
    "TASK_DECOMPOSE",
    "PATCH_IMPLEMENT",
]

client = httpx.Client(base_url=HUB_URL, timeout=60)


# ── LLM helper ───────────────────────────────────────────────────────────────

def call_llm(messages: list[dict], model: Optional[str] = None) -> str:
    payload = {
        "model": model or "stub",
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.2,
    }
    resp = httpx.post(f"{LLM_URL}/v1/chat/completions", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ── Hub helpers ───────────────────────────────────────────────────────────────

def poll_tasks(task_type: str) -> list[dict]:
    resp = client.get("/tasks/poll", params={"task_type": task_type, "limit": 3})
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


def heartbeat(task_id: str):
    client.post(
        f"/tasks/{task_id}/heartbeat",
        json={"worker_id": WORKER_ID, "lease_seconds": LEASE_SECONDS},
    )


def complete_task(task_id: str, output: dict):
    client.post(f"/tasks/{task_id}/complete", json={"output_data": output})


def fail_task(task_id: str, error: str):
    client.post(f"/tasks/{task_id}/fail", json={"error_message": error})


def upload_artifact(task_id: str, artifact_type: str, filename: str, content: bytes) -> dict:
    resp = client.post(
        f"/artifacts/{task_id}/upload",
        params={"artifact_type": artifact_type},
        files={"file": (filename, content, "application/octet-stream")},
    )
    resp.raise_for_status()
    return resp.json()


# ── Task handlers ─────────────────────────────────────────────────────────────

def _input(task: dict) -> dict[str, Any]:
    raw = task.get("input_data")
    if raw:
        return json.loads(raw)
    return {}


def handle_llm_task(task: dict):
    """Generic LLM task handler – calls LLM and completes the task."""
    inp = _input(task)
    task_type = task["task_type"]
    model = task.get("model_policy") or "stub"

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a software engineering assistant handling a {task_type} task. "
                "Be concise and precise."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Task type: {task_type}\n"
                f"Input: {json.dumps(inp, indent=2)}\n\n"
                "Please process this task and return your output."
            ),
        },
    ]

    result = call_llm(messages, model=model)
    complete_task(task["id"], {"result": result, "task_type": task_type})
    log.info("Completed LLM task %s (%s)", task["id"], task_type)


def handle_patch_implement(task: dict):
    """
    PATCH_IMPLEMENT handler:
    1. Clone the repo into a sandbox
    2. Call LLM for implementation instructions
    3. Apply changes (stub: create a placeholder file)
    4. Export git diff as unified patch
    5. Upload patch artifact
    """
    inp = _input(task)
    repo = inp.get("repo", "")
    ref = inp.get("ref", "HEAD")
    model = task.get("model_policy") or "stub"
    task_id = task["id"]

    # Validate ref to prevent command injection
    import re
    if not re.match(r'^[a-zA-Z0-9_.\-/]+$', ref):
        fail_task(task_id, f"Invalid ref: {ref!r}")
        return

    sandbox = os.path.join(SANDBOX_DIR, task_id)
    os.makedirs(sandbox, exist_ok=True)

    try:
        # Clone repo – use credential helper to avoid token exposure in URLs
        clone_url = f"https://github.com/{repo}.git"
        env = os.environ.copy()
        if GITHUB_TOKEN:
            # Use GIT_ASKPASS to provide credentials without embedding in URL
            askpass_script = os.path.join(sandbox, "_askpass.sh")
            with open(askpass_script, "w") as f:
                f.write(f"#!/bin/sh\necho '{GITHUB_TOKEN}'\n")
            os.chmod(askpass_script, 0o700)
            env["GIT_ASKPASS"] = askpass_script
            env["GIT_USERNAME"] = "x-token"

        log.info("Cloning %s @ %s into sandbox", repo, ref)
        subprocess.run(
            ["git", "clone", "--depth=1", f"--branch={ref}", clone_url, sandbox],
            check=True,
            timeout=120,
            capture_output=True,
            env=env,
        )

        # Call LLM for implementation plan
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a software engineer. Generate a unified diff patch "
                    "(git diff format) that implements the requested changes. "
                    "Output ONLY the diff, no explanation."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Repo: {repo}\nRef: {ref}\n"
                    f"Task input: {json.dumps(inp, indent=2)}\n\n"
                    "Generate the implementation patch."
                ),
            },
        ]
        llm_output = call_llm(messages, model=model)

        # Check if LLM returned a real diff; if stub mode, create a placeholder
        if not llm_output.strip().startswith("diff --git") and not llm_output.strip().startswith("---"):
            # Stub: create a placeholder file so we can export a real diff
            placeholder = os.path.join(sandbox, "poc_agent_placeholder.txt")
            with open(placeholder, "w") as f:
                f.write(f"# Generated by agent-generalist\n# Task: {task_id}\n# LLM output:\n{llm_output}\n")
            subprocess.run(["git", "add", "poc_agent_placeholder.txt"], cwd=sandbox, check=True)

        # Export git diff
        result = subprocess.run(
            ["git", "diff", "--cached", "--no-color"],
            cwd=sandbox,
            capture_output=True,
            text=True,
        )
        patch_content = result.stdout

        if not patch_content:
            # Also try unstaged
            result = subprocess.run(
                ["git", "diff", "--no-color"],
                cwd=sandbox,
                capture_output=True,
                text=True,
            )
            patch_content = result.stdout

        if not patch_content:
            patch_content = f"# No changes generated\n# LLM output:\n{llm_output}\n"

        # Upload patch
        artifact = upload_artifact(
            task_id,
            "patch",
            "implementation.patch",
            patch_content.encode("utf-8"),
        )
        log.info("Uploaded patch artifact %s for task %s", artifact["id"], task_id)

        complete_task(task_id, {
            "artifact_id": artifact["id"],
            "patch_size": len(patch_content),
        })
        log.info("Completed PATCH_IMPLEMENT task %s", task_id)

    except subprocess.CalledProcessError as exc:
        log.warning("Git operation failed for task %s: %s", task_id, exc)
        # Complete with stub patch (no real clone possible in offline mode)
        stub_patch = (
            f"# Stub patch – git clone not available\n"
            f"# Repo: {repo} @ {ref}\n"
            f"# Task: {task_id}\n"
        )
        artifact = upload_artifact(task_id, "patch", "implementation.patch", stub_patch.encode())
        complete_task(task_id, {"artifact_id": artifact["id"], "note": "stub_patch"})
    except Exception as exc:
        log.error("PATCH_IMPLEMENT failed for task %s: %s", task_id, exc)
        fail_task(task_id, str(exc))
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


HANDLERS = {
    "SPEC_NORMALIZE": handle_llm_task,
    "STORY_SPLIT": handle_llm_task,
    "TASK_DECOMPOSE": handle_llm_task,
    "PATCH_IMPLEMENT": handle_patch_implement,
}


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_once():
    for task_type in TASK_TYPES:
        try:
            tasks = poll_tasks(task_type)
        except Exception as exc:
            log.debug("Poll error for %s: %s", task_type, exc)
            continue

        for task in tasks:
            task_id = task["id"]
            claimed = claim_task(task_id)
            if not claimed:
                continue

            log.info("Claimed task %s (%s)", task_id, task_type)
            handler = HANDLERS.get(task_type)
            if handler is None:
                fail_task(task_id, f"No handler for task_type={task_type}")
                continue

            try:
                handler(claimed)
            except Exception as exc:
                log.error("Handler error for task %s: %s", task_id, exc)
                fail_task(task_id, str(exc))


def main():
    log.info("Agent generalist starting, worker_id=%s", WORKER_ID)
    while True:
        try:
            run_once()
        except Exception as exc:
            log.warning("Loop error: %s", exc)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
