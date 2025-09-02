# app/routers/upload.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from app.auth import get_current_active_user
from app.database import get_db
from sqlalchemy.orm import Session
from app import audit as audit_mod
import os, shutil, uuid

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/dump")
async def upload_dump(
    request: Request,
    file: UploadFile = File(...),
    user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    filename = (file.filename or "").lower()
    if not (filename.endswith(".sql") or filename.endswith(".dump")):
        raise HTTPException(status_code=400, detail="فقط فایل‌های .sql یا .dump مجاز هستند.")

    dest_dir = os.path.join("samples", "uploads")
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(
        dest_dir,
        f"{uuid.uuid4().hex}_{os.path.basename(file.filename or 'dump.sql')}"
    )
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # آدیت
    try:
        audit_mod.log_event(
            db,
            actor=user.username,
            action="upload.dump",
            status="success",
            ip=getattr(request.client, "host", None),
            path=str(request.url.path),
            method=request.method,
            req_id=getattr(request.state, "request_id", None),
            user_agent=request.headers.get("user-agent"),
            meta={"saved_as": dest_path, "size": os.path.getsize(dest_path)},
        )
    except Exception:
        pass

    return {"ok": True, "saved_as": dest_path}
