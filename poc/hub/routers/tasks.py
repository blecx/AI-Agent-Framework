"""Tasks router – poll, claim, heartbeat, complete/fail."""
import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Config, Task
from schemas import (
    TaskClaim,
    TaskComplete,
    TaskFail,
    TaskHeartbeat,
    TaskRead,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _now():
    return datetime.now(timezone.utc)


def _approval_required(db: Session) -> bool:
    cfg = db.query(Config).filter(Config.key == "require_approvals").first()
    return cfg is not None and cfg.value.lower() in ("true", "1", "on", "yes")


def _deps_satisfied(task: Task, db: Session) -> bool:
    """Return True if all dependency tasks are completed."""
    if not task.depends_on:
        return True
    dep_ids = json.loads(task.depends_on)
    if not dep_ids:
        return True
    completed = (
        db.query(Task)
        .filter(Task.id.in_(dep_ids), Task.status == "completed")
        .count()
    )
    return completed == len(dep_ids)


@router.get("/poll", response_model=list[TaskRead])
def poll_tasks(task_type: str, limit: int = 5, db: Session = Depends(get_db)):
    """Return available (pending, deps satisfied) tasks of given type."""
    now = _now()
    candidates = (
        db.query(Task)
        .filter(
            Task.task_type == task_type,
            Task.status.in_(["pending", "claimed"]),
        )
        .order_by(Task.created_at)
        .limit(50)
        .all()
    )
    available = []
    for t in candidates:
        if t.status == "claimed" and t.lease_expires_at and t.lease_expires_at > now:
            continue  # active lease
        if not _deps_satisfied(t, db):
            continue
        if _approval_required(db) and not t.approved:
            continue
        available.append(t)
        if len(available) >= limit:
            break
    return available


@router.post("/{task_id}/claim", response_model=TaskRead)
def claim_task(task_id: str, body: TaskClaim, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status not in ("pending",) and not (
        task.status == "claimed"
        and task.lease_expires_at
        and task.lease_expires_at <= _now()
    ):
        raise HTTPException(status_code=409, detail=f"Task is not claimable (status={task.status})")

    if not _deps_satisfied(task, db):
        raise HTTPException(status_code=409, detail="Task dependencies not yet satisfied")

    if _approval_required(db) and not task.approved:
        raise HTTPException(status_code=403, detail="Task requires manual approval")

    task.status = "claimed"
    task.worker_id = body.worker_id
    task.lease_expires_at = _now() + timedelta(seconds=body.lease_seconds)
    task.started_at = task.started_at or _now()
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/heartbeat", response_model=TaskRead)
def heartbeat(task_id: str, body: TaskHeartbeat, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "claimed":
        raise HTTPException(status_code=409, detail="Task is not claimed")
    if task.worker_id != body.worker_id:
        raise HTTPException(status_code=403, detail="Worker ID mismatch")

    task.lease_expires_at = _now() + timedelta(seconds=body.lease_seconds)
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(task_id: str, body: TaskComplete, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status not in ("claimed", "pending"):
        raise HTTPException(status_code=409, detail="Task cannot be completed from its current state")

    task.status = "completed"
    task.output_data = json.dumps(body.output_data) if body.output_data else None
    task.completed_at = _now()
    task.lease_expires_at = None
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/fail", response_model=TaskRead)
def fail_task(task_id: str, body: TaskFail, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "failed"
    task.error_message = body.error_message
    task.completed_at = _now()
    task.lease_expires_at = None
    task.retry_count += 1
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/approve", response_model=TaskRead)
def approve_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.approved = True
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
