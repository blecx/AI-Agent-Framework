from pydantic import BaseModel, Field

class SyncStateResponse(BaseModel):
    is_synced: bool = Field(..., description="Whether local changes are pushed to remote")
    unsynced_commits: int = Field(0, description="Number of commits ahead of remote")
    untracked_changes: int = Field(0, description="Number of modified/untracked files")
    has_conflicts: bool = Field(False, description="Whether there are merge conflicts")
    branch: str = Field("main", description="Current branch")
    message: str = Field("", description="Human readable status message")
