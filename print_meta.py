# print_meta.py
from app.database import SessionLocal
from app import models

def main():
    db = SessionLocal()
    try:
        print("=== DataSources ===")
        ds_list = db.query(models.DataSource).all()
        for ds in ds_list:
            print(f"id={ds.id}  name={ds.name}  path={ds.path}  created_at={ds.created_at}")

        print("\n=== TableMeta ===")
        tm_list = db.query(models.TableMeta).all()
        for tm in tm_list:
            print(f"id={tm.id}  schema='{tm.schema_name}'  table='{tm.table_name}' description='{tm.description}' source_id={tm.source_id}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
