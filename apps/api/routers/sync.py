from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from domain.sync.models import SyncStateResponse
from services.git_manager import GitManager
import os

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])

def get_git_manager() -> GitManager:
    base_path = os.getenv("PROJECT_DOCS_PATH", "../../projectDocs")
    manager = GitManager(base_path)
    manager.ensure_repository()
    return manager

@router.get("/state", response_model=SyncStateResponse)
async def get_sync_state(manager: GitManager = Depends(get_git_manager)):
    """Get the current sync state of the project repositories."""
    try:
        status = manager.get_sync_status()
        return SyncStateResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sync state: {str(e)}")


@router.post("/push", response_model=Dict[str, Any])
async def push_sync(manager: GitManager = Depends(get_git_manager)):
    """Push local commits to the remote repository."""
    try:
        if not manager.repo:
            raise HTTPException(status_code=400, detail="Repository not initialized")
        if not manager.repo.remotes:
            return {"status": "success", "message": "No remotes configured. Changes remain locally synced."}
            
        remote = manager.repo.remotes[0]
        result = remote.push()
        
        return {"status": "success", "message": "Successfully pushed changes to remote"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to push: {str(e)}")

@router.post("/pull", response_model=Dict[str, Any])
async def pull_sync(manager: GitManager = Depends(get_git_manager)):
    """Pull remote commits to the local repository."""
    try:
        if not manager.repo:
            raise HTTPException(status_code=400, detail="Repository not initialized")
        if not manager.repo.remotes:
            return {"status": "success", "message": "No remotes configured."}
            
        remote = manager.repo.remotes[0]
        remote.pull()
        
        return {"status": "success", "message": "Successfully pulled latest changes"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull: {str(e)}")
