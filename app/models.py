# app/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime , Table , UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# جدول واسط many-to-many بین ETL و Table
etl_tables = Table(
    "etl_tables",
    Base.metadata,
    Column("etl_id", Integer, ForeignKey("etls.id", ondelete="CASCADE"), primary_key=True),
    Column("table_id", Integer, ForeignKey("tables.id", ondelete="CASCADE"), primary_key=True),
)

class ETL(Base):
    __tablename__ = "etls"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), unique=True, nullable=False)
    tables = relationship("Table", secondary=etl_tables, back_populates="etls")

class Schema(Base):
    __tablename__ = "schemas"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    tables = relationship("Table", back_populates="schema")

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    schema_id = Column(Integer, ForeignKey("schemas.id"), nullable=False)
    schema = relationship("Schema", back_populates="tables")
    etls = relationship("ETL", secondary=etl_tables, back_populates="tables")
    __table_args__ = (UniqueConstraint("schema_id", "name", name="uq_schema_table"),)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    data_sources = relationship("DataSource", back_populates="owner")

class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), nullable=True)
    connection_string = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="data_sources")
    tables = relationship("TableMeta", back_populates="datasource", cascade="all, delete-orphan")

class TableMeta(Base):
    __tablename__ = "table_meta"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    datasource_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)

    datasource = relationship("DataSource", back_populates="tables")

class DatabaseConnection(Base):
    __tablename__ = "database_connections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    database_name = Column(String(255), nullable=True)
    connection_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
