from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    path = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TableMeta(Base):
    __tablename__ = "table_meta"
    id = Column(Integer, primary_key=True, index=True)
    schema_name = Column(String, index=True)
    table_name = Column(String, index=True)
    description = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseConnection(Base):
    __tablename__ = "database_connections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    host = Column(String)
    port = Column(Integer)
    username = Column(String)
    password = Column(String)
    database_name = Column(String)
    connection_type = Column(String)  # postgresql, mysql, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
