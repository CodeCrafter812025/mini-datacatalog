import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # از متغیر محیطی استفاده می‌کنیم (fallback برای توسعه محلی)
    db_uri = os.environ.get('DATABASE_URL', 'postgresql://test_user:test_password@localhost:5432/test_db')
    # اگر کسی از host نام db استفاده کرده بود آن را به localhost تبدیل کن
    db_uri = db_uri.replace('db', 'localhost')

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

    db.init_app(app)

    # import مدل‌ها/روت‌ها داخل کانتکست اپ تا از import-time side-effects جلوگیری شود
    with app.app_context():
        from app import routes, models  # فرض بر این است که models مسیرها را تعریف می‌کنند

    return app
