from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import csv
import io
import os
import uuid
import logging
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models
from ..auth import get_current_active_user
from ..database import get_db

from ..auth import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/analyze")
async def analyze_etl(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
    ):
    try:
        # ??? ???????? CSV ???? ?????
        if not (file.filename and file.filename.lower().endswith(".csv")):
            raise HTTPException(status_code=400, detail="???? ???? CSV ????.")
        
        # ?????? ?????? ????
        contents = await file.read()
        
        # ???? ???? ???? ???? ?? UTF-8? ??? ??? ?? latin-1
        try:
            text = contents.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 decode failed, trying latin-1")
            text = contents.decode("latin-1")
        
        # ?????? CSV ?? pandas
        tokens = []
        seen = set()
        
        try:
            df = pd.read_csv(io.StringIO(text))
            logger.info(f"CSV columns: {df.columns.tolist()}")
            logger.info(f"CSV shape: {df.shape}")
            
            # ??????? ???? ?????? ????? ?? ??? ?? ???? ???????
            for col in df.columns:
                for val in df[col].dropna().unique():
                    val_str = str(val).strip().lstrip("\ufeff")
                    if val_str and val_str not in seen:
                        seen.add(val_str)
                        tokens.append(val_str)
                        
        except Exception as e:
            logger.error(f"Error processing CSV with pandas: {e}")
            raise HTTPException(status_code=400, detail=f"??? ?? ?????? CSV: {str(e)}")
        
        # ????? ???? ?? ??? ????? ?? ???
        unique_name = f"{uuid.uuid4().hex}.csv"
        path = os.path.join(UPLOAD_DIR, unique_name)
        
        try:
            with open(path, "wb") as out_f:
                out_f.write(contents)
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(status_code=500, detail=f"??? ?? ?????? ????: {e}")
        
        # ????? ?? ????? DataSource
        ds = db.query(models.DataSource).filter(models.DataSource.name == file.filename).first()
        if ds:
            ds.path = path
            db.add(ds)
            db.commit()
            db.refresh(ds)
        else:
            ds = models.DataSource(name=file.filename, path=path)
            db.add(ds)
            try:
                db.commit()
                db.refresh(ds)
            except IntegrityError as e:
                logger.error(f"IntegrityError creating DataSource: {e}")
                db.rollback()
                ds = db.query(models.DataSource).filter(models.DataSource.name == file.filename).first()
                if not ds:
                    raise HTTPException(status_code=500, detail="???? ????? ?? ???? DataSource")
        
        # ????? ???????? TableMeta
        created = []
        for t in tokens:
            exists = db.query(models.TableMeta).filter(
                models.TableMeta.table_name == t,
                models.TableMeta.source_id == ds.id
            ).first()
            if exists:
                continue
            
            new_tm = models.TableMeta(
                schema_name="", 
                table_name=t, 
                description=None, 
                source_id=ds.id
            )
            db.add(new_tm)
            try:
                db.commit()
                db.refresh(new_tm)
                created.append({"id": new_tm.id, "table_name": new_tm.table_name})
            except IntegrityError as e:
                logger.error(f"IntegrityError creating TableMeta: {e}")
                db.rollback()
                continue
        
        return {
            "filename": file.filename, 
            "items_count": len(tokens), 
            "created": created
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_etl: {e}")
        raise HTTPException(status_code=500, detail=f"???? ????? ????: {str(e)}")
