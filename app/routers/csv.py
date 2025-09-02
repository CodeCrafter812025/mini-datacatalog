# app/routers/csv.py
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Request
from app.auth import get_current_active_user
from app.database import get_db
from sqlalchemy.orm import Session
from typing import Dict, Any
import os, io
import pandas as pd
import chardet
from sqlalchemy import create_engine, text

from app import audit as audit_mod

router = APIRouter(prefix="/csv", tags=["CSV"])

MAX_CSV_BYTES = int(os.getenv("MAX_CSV_BYTES", "10485760"))

PG_URL = os.getenv(
    "PG_URL",
    "postgresql+psycopg2://admin:admin@mini-pg:5432/catalogdb"
)

def _read_csv(upload: UploadFile) -> pd.DataFrame:
    raw = upload.file.read()
    if not raw or len(raw) == 0:
        raise HTTPException(status_code=400, detail="فایل خالی است.")
    if len(raw) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail=f"حجم فایل بیش از حد مجاز است (>{MAX_CSV_BYTES}).")

    enc = (chardet.detect(raw) or {}).get("encoding") or "utf-8"
    try:
        text_data = raw.decode(enc, errors="replace")
    except Exception:
        text_data = raw.decode("utf-8", errors="replace")

    try:
        df = pd.read_csv(io.StringIO(text_data))
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV بدون داده.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"خطا در خواندن CSV: {e}")
    finally:
        try:
            upload.file.close()
        except Exception:
            pass

    return df

@router.post("/preview")
async def preview_csv(
    request: Request,
    file: UploadFile = File(...),
    max_rows: int = 5,
    user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    df = _read_csv(file)
    head = df.head(max_rows)
    cols = [{"name": c, "dtype": str(head[c].dtype)} for c in head.columns]
    rows = head.to_dict(orient="records")

    # آدیت
    try:
        audit_mod.log_event(
            db,
            actor=user.username,
            action="csv.preview",
            status="success",
            ip=getattr(request.client, "host", None),
            path=str(request.url.path),
            method=request.method,
            req_id=getattr(request.state, "request_id", None),
            user_agent=request.headers.get("user-agent"),
            meta={"rows_total": int(len(df)), "rows_previewed": len(rows), "columns": [c["name"] for c in cols]},
        )
    except Exception:
        pass

    return {"columns": cols, "rows": rows, "row_count": int(len(df))}

@router.post("/load")
async def load_csv_to_db(
    request: Request,
    conn_id: int = Form(...),
    schema: str = Form(...),
    table_name: str = Form(...),
    if_exists: str = Form("append"),
    file: UploadFile = File(...),
    user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    df = _read_csv(file)
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV داده‌ای ندارد.")

    if not schema or not table_name:
        raise HTTPException(status_code=400, detail="schema و table_name الزامی هستند.")
    if_exists = (if_exists or "append").lower()
    if if_exists not in {"append", "replace", "fail"}:
        raise HTTPException(status_code=400, detail="مقدار نامعتبر برای if_exists.")

    try:
        engine = create_engine(PG_URL)
        with engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
            df.to_sql(
                name=table_name,
                con=conn,
                schema=schema,
                if_exists=if_exists,
                index=False,
                method="multi",
                chunksize=1000,
            )
        # آدیت موفق
        try:
            audit_mod.log_event(
                db,
                actor=user.username,
                action="csv.load",
                status="success",
                ip=getattr(request.client, "host", None),
                path=str(request.url.path),
                method=request.method,
                req_id=getattr(request.state, "request_id", None),
                user_agent=request.headers.get("user-agent"),
                meta={"schema": schema, "table": table_name, "rows_written": int(len(df)), "if_exists": if_exists},
            )
        except Exception:
            pass
        return {"ok": True, "rows_written": int(len(df))}
    except Exception as e:
        # آدیت خطا
        try:
            audit_mod.log_event(
                db,
                actor=user.username,
                action="csv.load",
                status="error",
                ip=getattr(request.client, "host", None),
                path=str(request.url.path),
                method=request.method,
                req_id=getattr(request.state, "request_id", None),
                user_agent=request.headers.get("user-agent"),
                meta={"schema": schema, "table": table_name, "error": str(e)},
            )
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"DB load failed: {e}")
