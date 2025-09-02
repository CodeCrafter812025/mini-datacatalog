# app/seed_etl.py
import csv, pathlib
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

SAMPLES = pathlib.Path("samples")

def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def main():
    db: Session = SessionLocal()
    try:
        # 1) schemas.csv : header => name
        schemas = read_csv(SAMPLES / "schemas.csv")
        name_to_schema = {}
        for row in schemas:
            name = row["name"].strip()
            sc = db.query(models.Schema).filter(models.Schema.name == name).first()
            if not sc:
                sc = models.Schema(name=name)
                db.add(sc); db.commit(); db.refresh(sc)
            name_to_schema[name] = sc

        # 2) tables.csv : header => schema_name,table_name
        tables = read_csv(SAMPLES / "tables.csv")
        full_to_table = {}
        for row in tables:
            schema_name = row["schema_name"].strip()
            table_name  = row["table_name"].strip()
            sc = name_to_schema[schema_name]
            tb = db.query(models.Table).filter(
                models.Table.schema_id == sc.id,
                models.Table.name == table_name
            ).first()
            if not tb:
                tb = models.Table(name=table_name, schema_id=sc.id)
                db.add(tb); db.commit(); db.refresh(tb)
            full_to_table[(schema_name, table_name)] = tb

        # 3) etl_names.csv : header => etl_name
        etl_names = read_csv(SAMPLES / "etl_names.csv")
        name_to_etl = {}
        for row in etl_names:
            etl_name = row["etl_name"].strip()
            e = db.query(models.ETL).filter(models.ETL.name == etl_name).first()
            if not e:
                e = models.ETL(name=etl_name)
                db.add(e); db.commit(); db.refresh(e)
            name_to_etl[etl_name] = e

        # 4) etl_tables.csv : header => etl_name,schema_name,table_name
        mappings = read_csv(SAMPLES / "etl_tables.csv")
        for row in mappings:
            etl_name    = row["etl_name"].strip()
            schema_name = row["schema_name"].strip()
            table_name  = row["table_name"].strip()

            e  = name_to_etl[etl_name]
            tb = full_to_table[(schema_name, table_name)]
            if tb not in e.tables:
                e.tables.append(tb)
        db.commit()

        print("Seeding done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
