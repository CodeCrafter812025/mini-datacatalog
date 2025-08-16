﻿from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# استفاده از متغیرهای محیطی با مقادیر پیش‌فرض
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@db:5432/catalogdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
