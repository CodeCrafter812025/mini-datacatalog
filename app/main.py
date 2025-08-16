from fastapi import FastAPI
import time
import logging
import sys

from . import models
from .database import engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from fastapi import APIRouter
from sqlalchemy import text

logger = logging.getLogger("mini-datacatalog")

app = FastAPI(
    title="Mini DataCatalog",
    description="A mini data catalog with JWT authentication and pagination",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/health")
async def health():
    return {"status":"ok"}


@app.on_event("startup")
def on_startup():
    """
    Safe startup: retry connecting to DB a few times and then call create_all.
    This avoids failing the whole app if Postgres is still coming up (useful in docker-compose).
    """
    max_tries = 10
    base_delay = 1.0  # seconds
    for attempt in range(1, max_tries + 1):
        try:
            # quick noop query to check connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            # if connection ok -> create tables and break
            models.Base.metadata.create_all(bind=engine)
            logger.info("Database reachable - tables created/verified.")
            break
        except Exception as exc:
            # show more useful message for OperationalError (network/pg not ready)
            logger.warning(f"DB connection attempt {attempt}/{max_tries} failed: {exc}")
            if attempt == max_tries:
                logger.error("Could not connect to database after multiple attempts.")
                # Option A: don't exit, let app run (endpoints may fail later)
                # Option B: force exit so container restarts. Uncomment next line to enable:
                # sys.exit(1)
                break
            # sleep with exponential backoff (but bounded)
            delay = min(base_delay * (2 ** (attempt - 1)), 10)
            time.sleep(delay)


# include routers (keep same as before)
from .routers import etl, meta, auth, database

app.include_router(etl.router, prefix="/etl", tags=["ETL"])
app.include_router(database.router, prefix="/db", tags=["database"])
app.include_router(meta.router, prefix="/meta", tags=["Meta"])
app.include_router(auth.router, tags=["Authentication"])


@app.get("/")
async def root():
    return {"message": "Mini DataCatalog OK"}

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status":"ok"}
    except Exception as e:
        return {"status":"error","detail": str(e)}
# serve a minimal frontend (static files)
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")


