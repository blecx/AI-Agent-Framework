"""
Tools for the workflow agent.

These tools enable the agent to interact with GitHub, files, git, and testing.
"""

import json
import subprocess
from pathlib import Path
from typing import Annotated, Optional


# ============================================================================
# GitHub Tools
# ============================================================================

def fetch_github_issue(issue_number: Annotated[int, "GitHub issue number"]) -> str:
    """
    Fetch GitHub issue details using gh CLI.
    
    Returns JSON string with issue title, body, labels, etc.
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "view", str(issue_number), "--json", 
             "number,title,body,labels,state,assignees"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Error fetching issue: {result.stderr}"
        
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


def create_github_pr(
    title: Annotated[str, "PR title"],
    body: Annotated[str, "PR description"],
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
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Error creating PR: {result.stderr}"
        
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# File System Tools
# ============================================================================

def read_file_content(
    file_path: Annotated[str, "Path to file relative to project root"],
) -> str:
    """
    Read contents of a file.
    
    Returns file content or error message.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} does not exist"
        
        if path.stat().st_size > 1_000_000:  # 1MB limit
            return f"Error: File {file_path} is too large (>1MB)"
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file_content(
    file_path: Annotated[str, "Path to file relative to project root"],
    content: Annotated[str, "File content to write"],
) -> str:
    """
    Write content to a file, creating directories if needed.
    
    Returns success message or error.
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def list_directory_contents(
    directory_path: Annotated[str, "Path to directory relative to project root"],
) -> str:
    """
    List files and directories in a given path.
    
    Returns newline-separated list of entries.
    """
    try:
        path = Path(directory_path)
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
) -> str:
    """
    Stage all changes and create a git commit.
    
    Returns commit hash or error message.
    """
    try:
        # Stage all changes
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Error committing: {result.stderr}"
        
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        
        return f"Committed: {hash_result.stdout.strip()}\n{result.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_changed_files() -> str:
    """
    Get list of files changed in working directory.
    
    Returns list of changed files or empty string.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


def create_feature_branch(
    branch_name: Annotated[str, "Branch name (e.g., issue/26-description)"],
) -> str:
    """
    Create and checkout a new feature branch from main.
    
    Returns success message or error.
    """
    try:
        # Checkout main and pull latest
        subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
        subprocess.run(["git", "pull", "origin", "main"], check=True, capture_output=True)
        
        # Create and checkout new branch
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            capture_output=True,
            text=True,
            timeout=30
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
) -> str:
    """
    Execute a shell command and return output.
    
    Use for running tests, builds, linting, etc.
    Returns combined stdout and stderr.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=working_directory
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
        
        with open(kb_file, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error loading knowledge base: {str(e)}"


def update_knowledge_base(
    category: Annotated[str, "Knowledge category (workflow_patterns, problem_solutions, time_estimates)"],
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
            with open(kb_file, 'r') as f:
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
        
        with open(kb_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        return f"Updated {category} with {len(new_data)} new entries"
    except Exception as e:
        return f"Error updating knowledge base: {str(e)}"


# ============================================================================
# Tool List for Agent
# ============================================================================

def get_all_tools():
    """Get all tools for the agent."""
    return [
        # GitHub
        fetch_github_issue,
        create_github_pr,
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
        # Knowledge Base
        get_knowledge_base_patterns,
        update_knowledge_base,
    ]
