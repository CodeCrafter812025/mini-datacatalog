from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import DataSource, TableMeta
import csv
import os

router = APIRouter()

def tm_to_dict(tm: TableMeta):
    return {
        "id": tm.id,
        "schema_name": tm.schema_name,
        "table_name": tm.table_name,
        "description": tm.description,
        "source_id": tm.source_id
    }

@router.get("/names")
def get_etl_names():
    etl_names = []
    csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "etl_names.csv")
    with open(csv_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            etl_names.append(row['name'])
    return etl_names

@router.get("/{name}/tables", response_model=list)
def get_etl_tables(name: str, db: Session = Depends(get_db)):
    data_sources = db.query(DataSource).filter(DataSource.etl_name == name).all()
    source_ids = [ds.id for ds in data_sources]
    tables = db.query(TableMeta).filter(TableMeta.source_id.in_(source_ids)).all()
    return [tm_to_dict(tm) for tm in tables]

@router.post("/{name}/execute")
def execute_etl(name: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return {"message": f"ETL process '{name}' started successfully."}
