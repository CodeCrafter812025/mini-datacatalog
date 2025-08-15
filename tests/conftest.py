import pytest
from app.database import engine, SessionLocal
from app import models

@pytest.fixture(scope="function")
def db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)
