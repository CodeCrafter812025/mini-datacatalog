# app/audit.py
from __future__ import annotations

import os, json, uuid, pathlib, logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from typing import Any, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.auth import get_current_active_user

# ---------- Logger (JSON lines) ----------
log_dir = pathlib.Path("logs"); log_dir.mkdir(exist_ok=True)
_audit_logger = logging.getLogger("audit")
if not _audit_logger.handlers:
    fh = RotatingFileHandler(log_dir / "audit.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    _audit_logger.addHandler(fh)
    _audit_logger.addHandler(logging.StreamHandler())
    level_name = (os.getenv("LOG_LEVEL") or "INFO").upper()
    _audit_logger.setLevel(getattr(logging, level_name, logging.INFO))

def _j(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        return json.dumps({"_str": str(obj)}, ensure_ascii=False)

# ---------- Model ----------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_utc = Column(DateTime(timezone=False), default=lambda: datetime.now(timezone.utc), nullable=False)

    actor = Column(String(100), nullable=False)     # username یا "ip:..." اگر ناشناس
    ip = Column(String(64), nullable=True)
    path = Column(String(256), nullable=True)
    method = Column(String(10), nullable=True)

    action = Column(String(100), nullable=False)    # login, csv.preview, csv.load, upload.dump, exception
    status = Column(String(32), nullable=False)     # success / failed / error

    req_id = Column(String(64), nullable=True)
    user_agent = Column(String(256), nullable=True)

    meta = Column(Text, nullable=True)              # JSON string

# ---------- API router ----------
router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/recent")
def recent_audit(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _user = Depends(get_current_active_user),
):
    rows: List[AuditLog] = (
        db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    )
    return [
        {
            "id": r.id,
            "ts_utc": r.ts_utc.isoformat(),
            "actor": r.actor,
            "ip": r.ip,
            "method": r.method,
            "path": r.path,
            "action": r.action,
            "status": r.status,
            "req_id": r.req_id,
            "user_agent": r.user_agent,
            "meta": r.meta and json.loads(r.meta),
        }
        for r in rows
    ]

# ---------- log helper ----------
def log_event(
    session: Optional[Session],
    *,
    actor: str,
    action: str,
    status: str,
    ip: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    req_id: Optional[str] = None,
    user_agent: Optional[str] = None,
    meta: Optional[Any] = None,
) -> None:
    payload = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "actor": actor or "-",
        "ip": ip,
        "path": path,
        "method": method,
        "action": action,
        "status": status,
        "req_id": req_id,
        "user_agent": user_agent,
        "meta": meta,
    }

    # فایل‌لاگ (همیشه)
    try:
        _audit_logger.info(_j(payload))
    except Exception:
        pass

    # DB (اگر session داریم)
    if session is None:
        return
    try:
        row = AuditLog(
            actor=payload["actor"],
            ip=ip,
            path=path,
            method=method,
            action=action,
            status=status,
            req_id=req_id,
            user_agent=user_agent,
            meta=_j(meta) if meta is not None else None,
        )
        session.add(row)
        session.commit()
    except Exception:
        try:
            session.rollback()
        except Exception:
            pass
