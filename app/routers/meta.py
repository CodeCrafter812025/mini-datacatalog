# app/routers/meta.py
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .. import models
from ..auth import get_current_active_user
from ..database import get_db
from fastapi import Depends



router = APIRouter()


class DSCreate(BaseModel):
    name: str
    type: str | None = None
    connection_string: str | None = None
    description: str | None = None

class DSUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    connection_string: str | None = None
    description: str | None = None

class TMCreate(BaseModel):
    name: str
    description: str | None = None
    datasource_id: int | None = None

class TMUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    datasource_id: int | None = None

def _ds_to_dict(ds: models.DataSource):
    return {
        "id": ds.id,
        "name": ds.name,
        "type": ds.type,
        "connection_string": ds.connection_string,
        "description": ds.description,
        "owner_id": ds.owner_id,
    }

def _tm_to_dict(tm: models.TableMeta):
    return {
        "id": tm.id,
        "name": tm.name,
        "description": tm.description,
        "datasource_id": tm.datasource_id,
    }

# ---------- DataSources ----------
@router.post("/datasources")
def create_datasource(payload: DSCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    ds = models.DataSource(
        name=payload.name,
        type=payload.type,
        connection_string=payload.connection_string,
        description=payload.description,
        owner_id=getattr(current_user, "id", None),
    )
    db.add(ds); db.commit(); db.refresh(ds)
    return _ds_to_dict(ds)

@router.get("/datasources")
def list_datasources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    total = db.query(models.DataSource).count()
    items = db.query(models.DataSource).order_by(models.DataSource.id).offset(skip).limit(limit).all()
    return {"items": [_ds_to_dict(d) for d in items], "total": total, "skip": skip, "limit": limit}

@router.get("/datasources/{ds_id}")
def get_datasource(ds_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    ds = db.query(models.DataSource).filter(models.DataSource.id == ds_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="DataSource not found")
    return _ds_to_dict(ds)

@router.put("/datasources/{ds_id}")
def update_datasource(ds_id: int, payload: DSUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    ds = db.query(models.DataSource).filter(models.DataSource.id == ds_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="DataSource not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(ds, k, v)
    db.commit(); db.refresh(ds)
    return _ds_to_dict(ds)

@router.delete("/datasources/{ds_id}")
def delete_datasource(ds_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    ds = db.query(models.DataSource).filter(models.DataSource.id == ds_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="DataSource not found")
    db.delete(ds); db.commit()
    return {"detail": "deleted"}

# ---------- TableMeta ----------
@router.post("/tablemeta")
def create_tablemeta(payload: TMCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    tm = models.TableMeta(
        name=payload.name,
        description=payload.description,
        datasource_id=payload.datasource_id,
    )
    db.add(tm); db.commit(); db.refresh(tm)
    return _tm_to_dict(tm)

@router.get("/tablemeta")
def list_tablemeta(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    total = db.query(models.TableMeta).count()
    items = db.query(models.TableMeta).order_by(models.TableMeta.id).offset(skip).limit(limit).all()
    return {"items": [_tm_to_dict(t) for t in items], "total": total, "skip": skip, "limit": limit}

@router.get("/tablemeta/{tm_id}")
def get_tablemeta(tm_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    tm = db.query(models.TableMeta).filter(models.TableMeta.id == tm_id).first()
    if not tm:
        raise HTTPException(status_code=404, detail="TableMeta not found")
    return _tm_to_dict(tm)

@router.put("/tablemeta/{tm_id}")
def update_tablemeta(tm_id: int, payload: TMUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    tm = db.query(models.TableMeta).filter(models.TableMeta.id == tm_id).first()
    if not tm:
        raise HTTPException(status_code=404, detail="TableMeta not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(tm, k, v)
    db.commit(); db.refresh(tm)
    return _tm_to_dict(tm)

@router.delete("/tablemeta/{tm_id}")
def delete_tablemeta(tm_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    tm = db.query(models.TableMeta).filter(models.TableMeta.id == tm_id).first()
    if not tm:
        raise HTTPException(status_code=404, detail="TableMeta not found")
    db.delete(tm); db.commit()
    return {"detail": "deleted"}

from sqlalchemy.exc import IntegrityError

@router.post("/datasources")
def create_datasource(payload: DSCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    # اگر از قبل وجود داشت، 409 بده یا حتی می‌توانی همان مورد را برگردانی (idempotent)
    existing = db.query(models.DataSource).filter(models.DataSource.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="DataSource with this name already exists")
        # یا: return _ds_to_dict(existing)

    ds = models.DataSource(
        name=payload.name,
        type=payload.type,
        connection_string=payload.connection_string,
        description=payload.description,
        owner_id=getattr(current_user, "id", None),
    )
    try:
        db.add(ds); db.commit(); db.refresh(ds)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="DataSource with this name already exists")
    return _ds_to_dict(ds)

