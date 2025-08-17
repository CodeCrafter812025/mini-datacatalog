from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), nullable=True)
    connection_string = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    tables = relationship("TableMeta", back_populates="datasource", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="data_sources")

    def __repr__(self):
        return f"<DataSource id={self.id} name={self.name}>"

class TableMeta(Base):
    __tablename__ = "table_meta"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    datasource_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)

    datasource = relationship("DataSource", back_populates="tables")

    def __repr__(self):
        return f"<TableMeta id={self.id} name={self.name} datasource_id={self.datasource_id}>"

# افزودن رابطه معکوس برای کاربر
User.data_sources = relationship("DataSource", order_by=DataSource.id, back_populates="owner")

