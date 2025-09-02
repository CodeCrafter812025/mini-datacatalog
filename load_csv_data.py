# fastapi_app.py
from fastapi import FastAPI
from app.database import Base, engine
from app.models import ETL, Schema, TableModel  # اطمینان از ساخت جداول
from app.routers.etl import router as etl_router

# ایجاد برنامه FastAPI
app = FastAPI(
    title="Mini DataCatalog API",
    description="A minimal FastAPI app for ETL operations",
    version="1.0.0"
)

# ساخت جداول (اگر موجود نبودند)
Base.metadata.create_all(bind=engine)

# افزودن روتر ETL
app.include_router(etl_router, prefix="/etl", tags=["ETL"])

# یک مسیر ساده برای تست
@app.get("/")
def read_root():
    return {"message": "FastAPI running"}
