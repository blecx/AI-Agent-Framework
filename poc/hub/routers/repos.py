"""Repos router – canonical clone management and snapshot serving."""
import os
import subprocess
import tarfile
import tempfile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Run

router = APIRouter(prefix="/repos", tags=["repos"])

REPOS_DIR = os.environ.get("REPOS_DIR", "/data/repos")
ARTIFACT_DIR = os.environ.get("ARTIFACT_DIR", "/data/artifacts")


def _repo_dir(repo: str) -> str:
    """Return path to the canonical shared clone for a repo."""
    safe = repo.replace("/", "__")
    return os.path.join(REPOS_DIR, safe)


def _ensure_clone(repo: str) -> str:
    """Ensure a canonical clone exists; return its path."""
    path = _repo_dir(repo)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        url = f"https://github.com/{repo}.git"
        result = subprocess.run(
            ["git", "clone", "--bare", url, path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, result.args, result.stdout, result.stderr
            )
    else:
        result = subprocess.run(
            ["git", "fetch", "--all", "--prune"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, result.args, result.stdout, result.stderr
            )
    return path


@router.post("/{run_id}/prepare")
def prepare_repo(run_id: str, db: Session = Depends(get_db)):
    """Clone/fetch the repo for a run and create a worktree branch."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        repo_path = _ensure_clone(run.repo)
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr or ""
        raise HTTPException(status_code=500, detail=f"Git operation failed: {stderr.strip() or exc}") from exc

    branch = f"run/{run_id}"
    worktree_path = os.path.join(REPOS_DIR, f"worktrees/{run_id}")

    if not os.path.exists(worktree_path):
        os.makedirs(os.path.dirname(worktree_path), exist_ok=True)
        subprocess.run(
            ["git", "worktree", "add", "-b", branch, worktree_path, run.ref],
            cwd=repo_path,
            check=True,
            timeout=30,
        )

    return {"repo_path": repo_path, "worktree_path": worktree_path, "branch": branch}


@router.post("/{run_id}/apply-patch")
def apply_patch(run_id: str, patch_artifact_id: str, db: Session = Depends(get_db)):
    """Apply a unified diff patch to the run's worktree."""
    from models import Artifact

    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    artifact = db.query(Artifact).filter(Artifact.id == patch_artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    worktree_path = os.path.join(REPOS_DIR, f"worktrees/{run_id}")
    if not os.path.exists(worktree_path):
        raise HTTPException(status_code=404, detail="Worktree not found; call /prepare first")

    result = subprocess.run(
        ["git", "apply", "--whitespace=fix", artifact.storage_path],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=422, detail=f"Patch apply failed: {result.stderr}")

    return {"status": "applied", "worktree": worktree_path}


@router.get("/{run_id}/snapshot")
def get_snapshot(run_id: str, db: Session = Depends(get_db)):
    """Return a tar.gz snapshot of the run worktree for runners.

    Uses `git archive` to produce a clean tarball without `.git/` metadata.
    Falls back to a manual tar if the worktree is not a git repo.
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    worktree_path = os.path.join(REPOS_DIR, f"worktrees/{run_id}")
    if not os.path.exists(worktree_path):
        raise HTTPException(
            status_code=404,
            detail="Worktree not found; call /repos/{run_id}/prepare first",
        )

    snap_dir = os.path.join(ARTIFACT_DIR, str(run_id))
    os.makedirs(snap_dir, exist_ok=True)
    snap_path = os.path.join(snap_dir, "snapshot.tar.gz")

    # Use git archive for a clean export (excludes .git metadata)
    result = subprocess.run(
        ["git", "archive", "--format=tar.gz", "--prefix=repo/", "-o", snap_path, "HEAD"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Fallback: manual tar excluding .git
        with tarfile.open(snap_path, "w:gz") as tar:
            for entry in os.scandir(worktree_path):
                if entry.name == ".git":
                    continue
                tar.add(entry.path, arcname=os.path.join("repo", entry.name))

    return FileResponse(snap_path, filename="snapshot.tar.gz", media_type="application/gzip")
