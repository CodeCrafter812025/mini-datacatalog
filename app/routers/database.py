from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import DatabaseConnection

router = APIRouter()

class DatabaseConnectionCreate(BaseModel):
    name: str
    host: str
    port: int
    username: str
    password: str
    database_name: str
    connection_type: str

@router.post("/connections")
def create_database_connection(connection: DatabaseConnectionCreate, db: Session = Depends(get_db)):
    db_connection = DatabaseConnection(
        name=connection.name,
        host=connection.host,
        port=connection.port,
        username=connection.username,
        password=connection.password,
        database_name=connection.database_name,
        connection_type=connection.connection_type
    )
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return {"message": "Database connection created successfully", "id": db_connection.id}

@router.get("/connections")
def get_database_connections(db: Session = Depends(get_db)):
    connections = db.query(DatabaseConnection).all()
    return [
        {
            "id": conn.id,
            "name": conn.name,
            "host": conn.host,
            "port": conn.port,
            "database_name": conn.database_name,
            "connection_type": conn.connection_type,
            "created_at": conn.created_at
        }
        for conn in connections
    ]
