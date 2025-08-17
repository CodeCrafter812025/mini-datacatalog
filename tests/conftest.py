import time
import pytest
from sqlalchemy import text
from app import create_app, db as _db

@pytest.fixture(scope='session')
def app():
    # ساخت اپلیکیشن
    app = create_app()

    # انتظار برای آماده شدن دیتابیس (حداکثر 30 تلاش)
    engine = _db.get_engine(app)
    for i in range(30):
        try:
            with engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError('Database did not become available within timeout')

    # ایجاد جداول برای تست‌ها
    with app.app_context():
        _db.create_all()

    yield app

    # teardown: حذف جداول بعد از پایان session
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    return _db
