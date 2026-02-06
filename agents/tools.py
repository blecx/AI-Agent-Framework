"""agents.tools

Tools for the workflow agent.

These tools enable the agent to interact with GitHub, files, git, and testing.

Note: This repository is multi-repo (backend + `_external/AI-Agent-Framework-Client`).
Most tools therefore accept an optional `working_directory` and/or `repo` argument so
the agent can operate on the correct repository root.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Annotated, Optional

from agents.command_cache import get_cache
from agents.time_estimator import TimeEstimator


# ============================================================================
# GitHub Tools
# ============================================================================


def fetch_github_issue(
    issue_number: Annotated[int, "GitHub issue number"],
    repo: Annotated[Optional[str], "GitHub repo in owner/name form (optional)"] = None,
    working_directory: Annotated[str, "Working directory for gh command"] = ".",
) -> str:
    """
    Fetch GitHub issue details using gh CLI.

    Returns JSON string with issue title, body, labels, etc.
    """
    try:
        cmd = [
            "gh",
            "issue",
            "view",
            str(issue_number),
            "--json",
            "number,title,body,labels,state,assignees",
        ]
        if repo:
            cmd.extend(["--repo", repo])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=working_directory,
        )

        if result.returncode != 0:
            return f"Error fetching issue: {result.stderr}"

        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


def create_github_pr(
    title: Annotated[str, "PR title"],
    body: Annotated[str, "PR description"],
    working_directory: Annotated[str, "Working directory for gh command"] = ".",
) -> str:
    """
    Create GitHub pull request with gh CLI.

    Returns PR URL or error message.
    """
    try:
        result = subprocess.run(
            ["gh", "pr", "create", "--title", title, "--body", body],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=working_directory,
        )

        if result.returncode != 0:
            return f"Error creating PR: {result.stderr}"

        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


def list_github_issues(
    repo: Annotated[str, "GitHub repo in owner/name form (required)"],
    state: Annotated[str, "Issue state: open or closed"] = "open",
    limit: Annotated[int, "Max issues to return"] = 50,
    label: Annotated[Optional[str], "Optional single label filter"] = None,
    search: Annotated[Optional[str], "Optional search query"] = None,
    working_directory: Annotated[str, "Working directory for gh command"] = ".",
) -> str:
    """List GitHub issues via gh CLI.

    Returns JSON array string with fields needed for selection/triage.
    """
    try:
        state_norm = (state or "open").strip().lower()
        if state_norm in {"opened"}:
            state_norm = "open"
        if state_norm not in {"open", "closed"}:
            return "Error: state must be 'open' or 'closed'"

        cmd = [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            state_norm,
            "--limit",
            str(limit),
            "--json",
            "number,title,labels,createdAt,updatedAt,author,assignees",
        ]
        if label:
            cmd.extend(["--label", label])
        if search:
            cmd.extend(["--search", search])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=working_directory,
        )
        if result.returncode != 0:
            return f"Error listing issues: {result.stderr}"
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# File System Tools
# ============================================================================


def read_file_content(
    file_path: Annotated[str, "Path to file relative to base directory"],
    base_directory: Annotated[str, "Base directory to resolve file_path"] = ".",
) -> str:
    """
    Read contents of a file.

    Returns file content or error message.
    """
    try:
        path = Path(base_directory) / file_path
        if not path.exists():
            return f"Error: File {file_path} does not exist"

        if path.stat().st_size > 1_000_000:  # 1MB limit
            return f"Error: File {file_path} is too large (>1MB)"

        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file_content(
    file_path: Annotated[str, "Path to file relative to base directory"],
    content: Annotated[str, "File content to write"],
    base_directory: Annotated[str, "Base directory to resolve file_path"] = ".",
) -> str:
    """
    Write content to a file, creating directories if needed.

    Returns success message or error.
    """
    try:
        path = Path(base_directory) / file_path
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def list_directory_contents(
    directory_path: Annotated[str, "Path to directory relative to base directory"],
    base_directory: Annotated[str, "Base directory to resolve directory_path"] = ".",
) -> str:
    """
    List files and directories in a given path.

    Returns newline-separated list of entries.
    """
    try:
        path = Path(base_directory) / directory_path
        if not path.exists():
            return f"Error: Directory {directory_path} does not exist"

        if not path.is_dir():
            return f"Error: {directory_path} is not a directory"

        entries = []
        for item in sorted(path.iterdir()):
            if item.is_dir():
                entries.append(f"{item.name}/")
            else:
                entries.append(item.name)

        return "\n".join(entries)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# ============================================================================
# Git Tools
# ============================================================================


def git_commit(
    message: Annotated[str, "Commit message"],
    working_directory: Annotated[str, "Working directory for git command"] = ".",
) -> str:
    """
    Stage all changes and create a git commit.

    Returns commit hash or error message.
    """
    try:
        # Stage all changes
        subprocess.run(
            ["git", "add", "-A"],
            check=True,
            capture_output=True,
            cwd=working_directory,
        )

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=working_directory,
        )

        if result.returncode != 0:
            return f"Error committing: {result.stderr}"

        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=working_directory,
        )

        return f"Committed: {hash_result.stdout.strip()}\n{result.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_changed_files(
    working_directory: Annotated[str, "Working directory for git command"] = ".",
) -> str:
    """
    Get list of files changed in working directory.

    Returns list of changed files or empty string.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=working_directory,
        )

        if result.returncode != 0:
            return f"Error: {result.stderr}"

        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


def create_feature_branch(
    branch_name: Annotated[str, "Branch name (e.g., issue/26-description)"],
    working_directory: Annotated[str, "Working directory for git command"] = ".",
) -> str:
    """
    Create and checkout a new feature branch from main.

    Returns success message or error.
    """
    try:
        # Checkout main and pull latest
        subprocess.run(
            ["git", "checkout", "main"],
            check=True,
            capture_output=True,
            cwd=working_directory,
        )
        subprocess.run(
            ["git", "pull", "origin", "main"],
            check=True,
            capture_output=True,
            cwd=working_directory,
        )

        # Create and checkout new branch
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=working_directory,
        )

        if result.returncode != 0:
            return f"Error creating branch: {result.stderr}"

        return f"Created and checked out branch: {branch_name}"
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# Testing & Build Tools
# ============================================================================


def run_command(
    command: Annotated[str, "Shell command to execute"],
    working_directory: Annotated[str, "Working directory for command"] = ".",
    use_cache: Annotated[bool, "Use command cache for idempotent operations"] = True,
) -> str:
    """
    Execute a shell command and return output.

    Use for running tests, builds, linting, etc.
    Returns combined stdout and stderr.

    Caching:
    - Enabled by default for idempotent commands (npm install, pip install, linting)
    - 1-hour TTL per command+cwd combination
    - Saves 8-12s per issue by avoiding redundant npm installs
    - Set use_cache=False for non-idempotent commands (git commit, file writes)
    """
    cache = get_cache()

    # Check cache first
    if use_cache:
        cached = cache.get(command, working_directory)
        if cached:
            output = []
            output.append(f"[CACHED] Exit code: {cached.returncode}")
            output.append(f"[Cache saved {cached.execution_time_seconds:.1f}s]")

            if cached.stdout:
                output.append("STDOUT:")
                output.append(cached.stdout)

            if cached.stderr:
                output.append("STDERR:")
                output.append(cached.stderr)

            return "\n".join(output)

    # Run command and measure time
    start_time = time.time()

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=working_directory,
        )

        elapsed = time.time() - start_time

        # Store in cache if enabled
        if use_cache:
            cache.set(
                command,
                working_directory,
                result.stdout,
                result.stderr,
                result.returncode,
                elapsed,
            )

        output = []
        output.append(f"Exit code: {result.returncode}")

        if result.stdout:
            output.append("STDOUT:")
            output.append(result.stdout)

        if result.stderr:
            output.append("STDERR:")
            output.append(result.stderr)

        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 5 minutes"
    except Exception as e:
        return f"Error executing command: {str(e)}"


# ============================================================================
# Knowledge Base Tools
# ============================================================================


def get_knowledge_base_patterns() -> str:
    """
    Load workflow patterns from knowledge base.

    Returns JSON string of past successful workflows.
    """
    try:
        kb_file = Path("agents/knowledge/workflow_patterns.json")
        if not kb_file.exists():
            return "[]"

        with open(kb_file, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error loading knowledge base: {str(e)}"


def update_knowledge_base(
    category: Annotated[
        str, "Knowledge category (workflow_patterns, problem_solutions, time_estimates)"
    ],
    data: Annotated[str, "JSON data to add to knowledge base"],
) -> str:
    """
    Update knowledge base with new learnings.

    Returns success message or error.
    """
    try:
        kb_file = Path(f"agents/knowledge/{category}.json")
        kb_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing data
        existing = []
        if kb_file.exists():
            with open(kb_file, "r") as f:
                try:
                    existing = json.load(f)
                    if not isinstance(existing, list):
                        existing = [existing]
                except json.JSONDecodeError:
                    existing = []

        # Parse new data
        new_data = json.loads(data)
        if not isinstance(new_data, list):
            new_data = [new_data]

        # Append and save
        existing.extend(new_data)

        with open(kb_file, "w") as f:
            json.dump(existing, f, indent=2)

        return f"Updated {category} with {len(new_data)} new entries"
    except Exception as e:
        return f"Error updating knowledge base: {str(e)}"


def get_cache_metrics() -> str:
    """Get command cache performance metrics.

    Returns formatted metrics showing cache hits and time saved.
    Useful for understanding agent efficiency improvements.
    """
    cache = get_cache()
    metrics = cache.get_metrics()

    return (
        f"Command Cache Metrics:\n"
        f"  Cache hits: {metrics['cache_hits']}\n"
        f"  Time saved: {metrics['time_saved_from_cache_seconds']}s\n"
        f"  Cached entries: {metrics['cached_entries']}"
    )


def get_time_estimate(
    files_to_change: Annotated[int, "Number of files to modify"],
    lines_estimate: Annotated[int, "Estimated total lines changed"],
    domain: Annotated[
        str, "Domain: backend, frontend, docs, testing, ci, agent, other"
    ] = "other",
    is_multi_repo: Annotated[bool, "Requires changes in multiple repos"] = False,
    has_dependencies: Annotated[bool, "Depends on other issues"] = False,
    complexity_score: Annotated[int, "Complexity 1-5 (1=simple, 5=complex)"] = 3,
) -> str:
    """Get ML-based time estimate for an issue.

    Uses RandomForestRegressor trained on historical data to predict
    resolution time with confidence scoring.

    Returns formatted estimate with confidence and reasoning.
    """
    estimator = TimeEstimator()
    estimate = estimator.predict(
        files_to_change=files_to_change,
        lines_estimate=lines_estimate,
        domain=domain,
        is_multi_repo=is_multi_repo,
        has_dependencies=has_dependencies,
        complexity_score=complexity_score,
    )

    return (
        f"Time Estimate: {estimate.hours:.1f} hours\n"
        f"Confidence: {estimate.confidence:.0%}\n"
        f"Reasoning: {estimate.reasoning}\n"
        f"\nFeatures considered:\n"
        f"  - Files to change: {files_to_change}\n"
        f"  - Lines estimate: {lines_estimate}\n"
        f"  - Domain: {domain}\n"
        f"  - Multi-repo: {is_multi_repo}\n"
        f"  - Has dependencies: {has_dependencies}\n"
        f"  - Complexity: {complexity_score}/5"
    )


# ============================================================================
# Tool List for Agent
# ============================================================================


def get_all_tools():
    """Get all tools for the agent."""
    return [
        # GitHub
        fetch_github_issue,
        create_github_pr,
        list_github_issues,
        # File System
        read_file_content,
        write_file_content,
        list_directory_contents,
        # Git
        git_commit,
        get_changed_files,
        create_feature_branch,
        # Testing
        run_command,
        get_cache_metrics,
        get_time_estimate,
        # Knowledge Base
        get_knowledge_base_patterns,
        update_knowledge_base,
    ]
