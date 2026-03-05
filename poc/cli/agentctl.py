#!/usr/bin/env python3
"""agentctl – CLI for the AI Agent Framework PoC hub.

Usage examples:
  agentctl run create --repo owner/repo --ref main --spec ./spec.md
  agentctl run status <run_id>
  agentctl task list --run <run_id>
  agentctl config set-approvals on
  agentctl logs tail <run_id>
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Annotated, Optional

import httpx
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="agentctl", help="AI Agent Framework PoC control CLI")
run_app = typer.Typer(help="Manage runs")
task_app = typer.Typer(help="Manage tasks")
config_app = typer.Typer(help="Hub configuration")
logs_app = typer.Typer(help="View logs")

app.add_typer(run_app, name="run")
app.add_typer(task_app, name="task")
app.add_typer(config_app, name="config")
app.add_typer(logs_app, name="logs")

console = Console()
err_console = Console(stderr=True, style="red")


def _hub_url() -> str:
    return os.environ.get("HUB_URL", "http://localhost:8000")


def _client() -> httpx.Client:
    return httpx.Client(base_url=_hub_url(), timeout=30)


def _die(msg: str, code: int = 1) -> None:
    err_console.print(f"[bold red]Error:[/bold red] {msg}")
    raise typer.Exit(code)


# ── run commands ──────────────────────────────────────────────────────────────

@run_app.command("create")
def run_create(
    repo: Annotated[str, typer.Option("--repo", help="GitHub owner/repo")] = "",
    ref: Annotated[str, typer.Option("--ref", help="git ref (branch, SHA, tag)")] = "main",
    spec: Annotated[Optional[Path], typer.Option("--spec", help="Path to spec.md")] = None,
):
    """Create a new run and its default task DAG."""
    if not repo:
        _die("--repo is required")

    spec_content: Optional[str] = None
    if spec:
        if not spec.exists():
            _die(f"Spec file not found: {spec}")
        spec_content = spec.read_text()

    with _client() as c:
        resp = c.post("/runs", json={"repo": repo, "ref": ref, "spec_content": spec_content})
        if resp.status_code != 201:
            _die(f"Hub returned {resp.status_code}: {resp.text}")
        run = resp.json()

    console.print(f"[green]✓ Run created:[/green] {run['id']}")
    console.print(f"  Repo : {run['repo']}")
    console.print(f"  Ref  : {run['ref']}")
    console.print(f"  Status: {run['status']}")
    return run["id"]


@run_app.command("status")
def run_status(run_id: str):
    """Show status of a run and its tasks."""
    with _client() as c:
        r = c.get(f"/runs/{run_id}")
        if r.status_code == 404:
            _die(f"Run not found: {run_id}")
        r.raise_for_status()
        run = r.json()

        t = c.get(f"/runs/{run_id}/tasks")
        t.raise_for_status()
        tasks = t.json()

    console.print(f"\n[bold]Run {run['id']}[/bold]")
    console.print(f"  Repo  : {run['repo']}")
    console.print(f"  Ref   : {run['ref']}")
    console.print(f"  Status: [bold]{run['status']}[/bold]")
    console.print(f"  Created: {run['created_at']}")

    table = Table(title="Tasks", show_lines=True)
    table.add_column("ID", style="dim", max_width=36)
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Worker")
    table.add_column("Updated")

    status_colors = {
        "pending": "yellow",
        "claimed": "blue",
        "completed": "green",
        "failed": "red",
    }
    for task in tasks:
        status = task["status"]
        color = status_colors.get(status, "white")
        table.add_row(
            str(task["id"])[:8] + "...",
            task["task_type"],
            f"[{color}]{status}[/{color}]",
            task.get("worker_id") or "-",
            task["updated_at"][:19],
        )

    console.print(table)


@run_app.command("list")
def run_list(limit: int = 10):
    """List recent runs."""
    with _client() as c:
        resp = c.get("/runs", params={"limit": limit})
        resp.raise_for_status()
        runs = resp.json()

    table = Table(title="Runs", show_lines=True)
    table.add_column("ID", style="dim")
    table.add_column("Repo")
    table.add_column("Ref")
    table.add_column("Status")
    table.add_column("Created")

    for run in runs:
        table.add_row(
            str(run["id"])[:8] + "...",
            run["repo"],
            run["ref"],
            run["status"],
            run["created_at"][:19],
        )
    console.print(table)


# ── task commands ─────────────────────────────────────────────────────────────

@task_app.command("list")
def task_list(
    run: Annotated[str, typer.Option("--run", help="Run ID")] = "",
):
    """List tasks for a run."""
    if not run:
        _die("--run is required")

    with _client() as c:
        resp = c.get(f"/runs/{run}/tasks")
        if resp.status_code == 404:
            _die(f"Run not found: {run}")
        resp.raise_for_status()
        tasks = resp.json()

    table = Table(title=f"Tasks for run {run[:8]}...", show_lines=True)
    table.add_column("ID", style="dim")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Worker")
    table.add_column("Retries")
    table.add_column("Error", max_width=40)

    for task in tasks:
        table.add_row(
            str(task["id"])[:8] + "...",
            task["task_type"],
            task["status"],
            task.get("worker_id") or "-",
            str(task.get("retry_count", 0)),
            (task.get("error_message") or "")[:40],
        )
    console.print(table)


@task_app.command("approve")
def task_approve(task_id: str):
    """Approve a task that requires manual approval."""
    with _client() as c:
        resp = c.post(f"/tasks/{task_id}/approve")
        if resp.status_code == 404:
            _die(f"Task not found: {task_id}")
        resp.raise_for_status()
        task = resp.json()
    console.print(f"[green]✓ Task {task_id} approved[/green] (status={task['status']})")


# ── config commands ───────────────────────────────────────────────────────────

@config_app.command("set-approvals")
def config_set_approvals(
    value: Annotated[str, typer.Argument(help="on|off")],
):
    """Toggle global manual approval requirement."""
    if value.lower() not in ("on", "off", "true", "false", "1", "0"):
        _die("Value must be on|off")

    normalized = "true" if value.lower() in ("on", "true", "1") else "false"
    with _client() as c:
        resp = c.put("/config/require_approvals", json={"value": normalized})
        resp.raise_for_status()
        cfg = resp.json()
    state = "ENABLED" if cfg["value"] == "true" else "DISABLED"
    console.print(f"[bold]Manual approvals:[/bold] {state}")


@config_app.command("get")
def config_get(key: str):
    """Get a config value."""
    with _client() as c:
        resp = c.get(f"/config/{key}")
        resp.raise_for_status()
        cfg = resp.json()
    console.print(f"{cfg['key']} = {cfg['value']}")


@config_app.command("list")
def config_list():
    """List all config values."""
    with _client() as c:
        resp = c.get("/config")
        resp.raise_for_status()
        items = resp.json()

    table = Table(title="Hub Config", show_lines=True)
    table.add_column("Key")
    table.add_column("Value")
    table.add_column("Updated")

    for item in items:
        table.add_row(item["key"], item["value"], item["updated_at"][:19])
    console.print(table)


# ── logs commands ─────────────────────────────────────────────────────────────

@logs_app.command("tail")
def logs_tail(
    run_id: str,
    interval: float = typer.Option(3.0, "--interval", help="Poll interval (seconds)"),
    count: int = typer.Option(0, "--count", help="Stop after N polls (0=forever)"),
):
    """Tail task status and artifacts for a run (best-effort polling)."""
    console.print(f"[dim]Tailing run {run_id} (Ctrl+C to stop)...[/dim]")
    seen_tasks: dict[str, str] = {}
    polls = 0

    while True:
        try:
            with _client() as c:
                resp = c.get(f"/runs/{run_id}/tasks")
                if resp.status_code == 404:
                    _die(f"Run not found: {run_id}")
                resp.raise_for_status()
                tasks = resp.json()

            for task in tasks:
                tid = task["id"]
                status = task["status"]
                if seen_tasks.get(tid) != status:
                    seen_tasks[tid] = status
                    console.print(
                        f"[dim]{task['updated_at'][:19]}[/dim] "
                        f"{task['task_type']:<22} → [bold]{status}[/bold]"
                        + (f" ✗ {task['error_message']}" if task.get("error_message") else "")
                    )

            polls += 1
            if count and polls >= count:
                break
            time.sleep(interval)

        except KeyboardInterrupt:
            break
        except Exception as exc:
            err_console.print(f"Poll error: {exc}")
            time.sleep(interval)


if __name__ == "__main__":
    app()
