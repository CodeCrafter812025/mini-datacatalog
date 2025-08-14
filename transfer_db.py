# transfer_db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.database import Base
from dotenv import load_dotenv

load_dotenv()

SRC_URL = "sqlite:///./test.db"
DEST_URL = os.getenv("DATABASE_URL", "postgresql://catalog:catalogpass@localhost:5432/gnaf")

# engines
src_engine = create_engine(SRC_URL, connect_args={"check_same_thread": False})
dest_engine = create_engine(DEST_URL)

SrcSession = sessionmaker(bind=src_engine)
DestSession = sessionmaker(bind=dest_engine)

# ensure destination tables exist (creates tables according to models if missing)
Base.metadata.create_all(bind=dest_engine)

def transfer():
    src = SrcSession()
    dest = DestSession()
    try:
        mapping = {}  # map src datasource id -> dest datasource id

        # Transfer DataSource rows
        for d in src.query(models.DataSource).all():
            existing = dest.query(models.DataSource).filter(models.DataSource.name == d.name).first()
            if existing:
                mapping[d.id] = existing.id
                continue
            nd = models.DataSource(name=d.name, path=d.path, created_at=d.created_at)
            dest.add(nd)
            dest.flush()   # flush to get id
            mapping[d.id] = nd.id
        dest.commit()

        # Transfer TableMeta rows
        for t in src.query(models.TableMeta).all():
            # prevent duplicates: check if same table_name + source already exists
            dst_source_id = mapping.get(t.source_id)
            exists = dest.query(models.TableMeta).filter(
                models.TableMeta.table_name == t.table_name,
                models.TableMeta.source_id == dst_source_id
            ).first()
            if exists:
                continue
            new_tm = models.TableMeta(
                schema_name = t.schema_name,
                table_name = t.table_name,
                description = t.description,
                source_id = dst_source_id
            )
            dest.add(new_tm)
        dest.commit()

        print("Transfer complete.")
    except Exception as e:
        dest.rollback()
        print("Transfer failed:", e)
        raise
    finally:
        src.close()
        dest.close()

if __name__ == '__main__':
    transfer()
