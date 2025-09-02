# app/routers/etl.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_active_user
from .. import models

router = APIRouter(
    prefix="/etl",
    tags=["ETL"],
    dependencies=[Depends(get_current_active_user)]  # همه‌ی مسیرها نیاز به لاگین دارند
)

@router.get("/names")
def get_etl_names(db: Session = Depends(get_db)):
    names = [e.name for e in db.query(models.ETL).order_by(models.ETL.name).all()]
    return names

@router.get("/{name}/tables")
def get_etl_tables(name: str, db: Session = Depends(get_db)):
    etl = db.query(models.ETL).filter(models.ETL.name == name).first()
    if not etl:
        raise HTTPException(status_code=404, detail="ETL not found")
    return [{"id": t.id, "name": t.name, "schema": t.schema.name} for t in etl.tables]
