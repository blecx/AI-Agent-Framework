"""Artifacts router – upload and download."""
import os

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Artifact, Task
from schemas import ArtifactRead, ArtifactRegister

router = APIRouter(prefix="/artifacts", tags=["artifacts"])

ARTIFACT_DIR = os.environ.get("ARTIFACT_DIR", "/data/artifacts")


@router.post("/{task_id}/upload", response_model=ArtifactRead, status_code=201)
async def upload_artifact(
    task_id: str,
    artifact_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    dest_dir = os.path.join(ARTIFACT_DIR, str(task.run_id), task_id)
    os.makedirs(dest_dir, exist_ok=True)
    filename = file.filename or f"{artifact_type}.bin"
    dest_path = os.path.join(dest_dir, filename)

    content = await file.read()
    async with aiofiles.open(dest_path, "wb") as f:
        await f.write(content)

    artifact = Artifact(
        task_id=task_id,
        run_id=task.run_id,
        artifact_type=artifact_type,
        filename=filename,
        storage_path=dest_path,
        size_bytes=len(content),
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


@router.get("/{artifact_id}/download")
def download_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if not os.path.exists(artifact.storage_path):
        raise HTTPException(status_code=404, detail="Artifact file missing")
    return FileResponse(artifact.storage_path, filename=artifact.filename)


@router.get("/{artifact_id}", response_model=ArtifactRead)
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact
