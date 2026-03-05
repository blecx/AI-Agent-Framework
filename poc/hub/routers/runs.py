"""Runs router."""
import json
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import Run, Task
from schemas import RunCreate, RunRead, TaskCreate, TaskRead

router = APIRouter(prefix="/runs", tags=["runs"])

ARTIFACT_DIR = os.environ.get("ARTIFACT_DIR", "/data/artifacts")


@router.post("", response_model=RunRead, status_code=201)
def create_run(body: RunCreate, db: Session = Depends(get_db)):
    run = Run(
        repo=body.repo,
        ref=body.ref,
        spec_content=body.spec_content,
        status="pending",
    )
    db.add(run)
    db.flush()

    # Create default task DAG
    tasks = _create_default_dag(run.id, body.repo, body.ref)
    for t in tasks:
        db.add(t)

    db.commit()
    db.refresh(run)
    return run


def _create_default_dag(run_id, repo: str, ref: str) -> list[Task]:
    """Build the default task DAG for a run."""
    t_spec = Task(
        id=uuid.uuid4(),
        run_id=run_id,
        task_type="SPEC_NORMALIZE",
        status="pending",
        depends_on=json.dumps([]),
        input_data=json.dumps({"repo": repo, "ref": ref}),
        model_policy="default",
    )
    t_story = Task(
        id=uuid.uuid4(),
        run_id=run_id,
        task_type="STORY_SPLIT",
        status="pending",
        depends_on=json.dumps([str(t_spec.id)]),
        input_data=json.dumps({"repo": repo, "ref": ref}),
        model_policy="default",
    )
    t_decomp = Task(
        id=uuid.uuid4(),
        run_id=run_id,
        task_type="TASK_DECOMPOSE",
        status="pending",
        depends_on=json.dumps([str(t_story.id)]),
        input_data=json.dumps({"repo": repo, "ref": ref}),
        model_policy="default",
    )
    t_patch = Task(
        id=uuid.uuid4(),
        run_id=run_id,
        task_type="PATCH_IMPLEMENT",
        status="pending",
        depends_on=json.dumps([str(t_decomp.id)]),
        input_data=json.dumps({"repo": repo, "ref": ref}),
        model_policy="default",
    )
    t_tests = Task(
        id=uuid.uuid4(),
        run_id=run_id,
        task_type="RUN_TESTS_PYTHON",
        status="pending",
        depends_on=json.dumps([str(t_patch.id)]),
        input_data=json.dumps({"repo": repo, "ref": ref}),
        model_policy=None,
    )
    return [t_spec, t_story, t_decomp, t_patch, t_tests]


@router.get("", response_model=list[RunRead])
def list_runs(limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Run).order_by(Run.created_at.desc()).limit(limit).all()


@router.get("/{run_id}", response_model=RunRead)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/tasks", response_model=list[TaskRead])
def list_run_tasks(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return db.query(Task).filter(Task.run_id == run_id).order_by(Task.created_at).all()


@router.post("/{run_id}/tasks", response_model=TaskRead, status_code=201)
def create_task(run_id: str, body: TaskCreate, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    task = Task(
        run_id=run_id,
        task_type=body.task_type,
        status="pending",
        depends_on=json.dumps(body.depends_on),
        input_data=json.dumps(body.input_data) if body.input_data else None,
        model_policy=body.model_policy,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/{run_id}/spec", status_code=200)
async def upload_spec(run_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    spec_dir = os.path.join(ARTIFACT_DIR, str(run_id))
    os.makedirs(spec_dir, exist_ok=True)
    spec_path = os.path.join(spec_dir, "spec.md")
    content = await file.read()
    with open(spec_path, "wb") as f:
        f.write(content)

    run.spec_path = spec_path
    run.spec_content = content.decode("utf-8", errors="replace")
    db.commit()
    return {"spec_path": spec_path}
