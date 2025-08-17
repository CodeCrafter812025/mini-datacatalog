from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), nullable=True)
    connection_string = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    tables = relationship("TableMeta", back_populates="datasource", cascade="all, delete-orphan")

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
