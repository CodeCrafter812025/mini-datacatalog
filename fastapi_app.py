# fastapi_app.py
from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import os, pathlib, logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

from app.database import get_db, Base, engine
from app.auth import authenticate_user, create_access_token, get_current_active_user
from app.email_utils import send_error_email
from app.routers import meta as meta_router
from app.routers import database as db_router
from app.routers import etl as etl_router
from app.routers import csv as csv_router
from app.routers import upload as upload_router

# NEW
from app.middleware import RequestIDMiddleware, RateLimitMiddleware
from app import audit as audit_mod

load_dotenv()

app = FastAPI(
    title="Mini DataCatalog API",
    description="FastAPI app with ETL, authentication and CSV analysis",
    version="1.0.0",
)

# Static UI
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/ui")
def ui():
    return FileResponse("app/static/index.html")

# Logging
log_dir = pathlib.Path("logs"); log_dir.mkdir(exist_ok=True)
handler = RotatingFileHandler(log_dir / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
level_name = (os.getenv("LOG_LEVEL") or "INFO").upper()
logging.basicConfig(level=getattr(logging, level_name, logging.INFO), handlers=[handler, logging.StreamHandler()])
logger = logging.getLogger("app")

# CORS
raw_origins = (os.getenv("CORS_ALLOW_ORIGINS") or "*").strip()
if raw_origins in ("", "*"):
    allow_origins = ["*"]; allow_creds = False
else:
    allow_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    allow_creds = True
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NEW: Middlewareها
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    rate_per_sec=float(os.getenv("RATE_LIMIT_RPS", "5")),
    burst=int(os.getenv("RATE_LIMIT_BURST", "15")),
    skip_paths={"/healthz", "/openapi.json", "/docs", "/redoc"},
)

# DB init (مهم: قبل از create_all مطمئنیم audit_mod import شده تا مدل ثبت شود)
@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)

# Global error handler (+ آدیت)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    subject = "Mini DataCatalog - Unhandled Exception"
    body = f"{request.method} {request.url}\n\n{repr(exc)}"
    try:
        send_error_email(subject, body)
        logger.exception(exc)
    except Exception:
        pass
    # آدیت فایل (و DB اگر تونستیم session تزریق کنیم؛ اینجا نداریم → فقط فایل)
    try:
        audit_mod.log_event(
            None,
            actor="unknown",
            action="exception",
            status="error",
            ip=getattr(request.client, "host", None),
            path=str(request.url.path),
            method=request.method,
            req_id=getattr(request.state, "request_id", None),
            user_agent=request.headers.get("user-agent"),
            meta={"detail": str(exc)},
        )
    except Exception:
        pass
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/")
def root():
    return {"message": "FastAPI running"}

# Auth (با آدیت)
@app.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # آدیت لاگین ناموفق
        try:
            audit_mod.log_event(
                db,
                actor=form_data.username,
                action="login",
                status="failed",
                ip=getattr(request.client, "host", None),
                path=str(request.url.path),
                method=request.method,
                req_id=getattr(request.state, "request_id", None),
                user_agent=request.headers.get("user-agent"),
                meta={"reason": "bad_credentials"},
            )
        except Exception:
            pass
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token({"sub": user.username})

    # آدیت لاگین موفق
    try:
        audit_mod.log_event(
            db,
            actor=user.username,
            action="login",
            status="success",
            ip=getattr(request.client, "host", None),
            path=str(request.url.path),
            method=request.method,
            req_id=getattr(request.state, "request_id", None),
            user_agent=request.headers.get("user-agent"),
        )
    except Exception:
        pass
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user = Depends(get_current_active_user)):
    return {"username": current_user.username, "is_active": bool(current_user.is_active)}

# Routers
app.include_router(meta_router.router, prefix="/meta", tags=["Meta"])
app.include_router(db_router.router, prefix="/db", tags=["Database"])
app.include_router(etl_router.router, tags=["ETL"])
app.include_router(csv_router.router)
app.include_router(upload_router.router)
app.include_router(audit_mod.router)  # NEW

# Health (no auth)
health_router = APIRouter()

@health_router.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}

app.include_router(health_router)

@app.get("/debug/crash")
def debug_crash():
    raise RuntimeError("Boom! Test error for email/logs")
