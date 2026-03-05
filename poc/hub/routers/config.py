"""Config router – global settings (e.g. require_approvals)."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Config
from schemas import ConfigRead, ConfigSet

router = APIRouter(prefix="/config", tags=["config"])

KNOWN_KEYS = {"require_approvals", "default_model_policy", "lease_seconds"}


def _upsert(db: Session, key: str, value: str) -> Config:
    cfg = db.query(Config).filter(Config.key == key).first()
    if cfg:
        cfg.value = value
    else:
        cfg = Config(key=key, value=value)
        db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


@router.get("", response_model=list[ConfigRead])
def list_config(db: Session = Depends(get_db)):
    return db.query(Config).all()


@router.get("/{key}", response_model=ConfigRead)
def get_config(key: str, db: Session = Depends(get_db)):
    cfg = db.query(Config).filter(Config.key == key).first()
    if not cfg:
        return ConfigRead(key=key, value="", updated_at=datetime.now(timezone.utc))
    return cfg


@router.put("/{key}", response_model=ConfigRead)
def set_config(key: str, body: ConfigSet, db: Session = Depends(get_db)):
    if key not in KNOWN_KEYS:
        raise HTTPException(status_code=400, detail=f"Unknown config key. Valid keys: {sorted(KNOWN_KEYS)}")
    return _upsert(db, key, body.value)
