from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import DatabaseConnection
from ..auth import get_current_active_user
from sqlalchemy import text
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.exc import SQLAlchemyError
import socket

# همه مسیرهای /db با توکن محافظت می‌شوند
router = APIRouter(dependencies=[Depends(get_current_active_user)])

class DatabaseConnectionCreate(BaseModel):
    name: str
    host: str
    port: int
    username: str | None = None
    password: str | None = None
    database_name: str | None = None
    connection_type: str | None = None

@router.post("/connections")
def create_database_connection(connection: DatabaseConnectionCreate, db: Session = Depends(get_db)):
    db_connection = DatabaseConnection(**connection.dict())
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return {"message": "Database connection created successfully", "id": db_connection.id}

@router.get("/connections")
def get_database_connections(db: Session = Depends(get_db)):
    connections = db.query(DatabaseConnection).order_by(DatabaseConnection.id).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "host": c.host,
            "port": c.port,
            "database_name": c.database_name,
            "connection_type": c.connection_type,
            "created_at": c.created_at,
        }
        for c in connections
    ]

def _build_sqlalchemy_url(conn: DatabaseConnection) -> str | None:
    t = (conn.connection_type or "").lower()
    if t in ("postgres", "postgresql"):
        return f"postgresql+psycopg2://{conn.username}:{conn.password}@{conn.host}:{conn.port}/{conn.database_name}"
    if t in ("mysql", "mariadb"):
        return f"mysql+pymysql://{conn.username}:{conn.password}@{conn.host}:{conn.port}/{conn.database_name}"
    if t in ("mssql", "sqlserver"):
        return f"mssql+pyodbc://{conn.username}:{conn.password}@{conn.host}:{conn.port}/{conn.database_name}?driver=ODBC+Driver+17+for+SQL+Server"
    return None

@router.post("/connections/{conn_id}/test")
def test_db_connection(conn_id: int, db: Session = Depends(get_db)):
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # 1) تست شبکه (TCP)
    reachable = False
    try:
        with socket.create_connection((conn.host, int(conn.port)), timeout=3):
            reachable = True
    except OSError:
        reachable = False

    result = {"reachable": reachable, "sql_ok": False, "driver_required": None}

    # 2) تلاش SELECT 1
    url = _build_sqlalchemy_url(conn)
    if url:
        try:
            eng = sa_create_engine(url)
            with eng.connect() as c:
                c.execute(text("SELECT 1"))
            result["sql_ok"] = True
        except ModuleNotFoundError as e:
            result["driver_required"] = str(e)
        except SQLAlchemyError as e:
            result["error"] = str(e)

    return result
