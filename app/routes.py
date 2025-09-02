# app/routes.py
from flask import request, jsonify
from app import app, db
import csv
import io
from sqlalchemy import text

@app.route('/')
def index():
    return 'Mini Data Catalog — app is running'

@app.route('/upload', methods=['POST'])

def upload_file():
    if 'file' not in request.files:
        return jsonify({'error':'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error':'No selected file'}), 400
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error':'Invalid file format'}), 400

    # خواندن CSV
    stream = io.StringIO(file.stream.read().decode('utf-8'))
    csv_reader = csv.reader(stream)
    try:
        next(csv_reader)  # اگر هدر دارد، رد کن (در غیر اینصورت از try/except چشم‌پوشی)
    except StopIteration:
        pass

    try:
        # درج ایمن (Postgres) — اگر جدول etl وجود دارد استفاده می‌کنیم.
        # از ON CONFLICT برای جلوگیری از تکراری استفاده شده (درصورت وجود constraint)
        insert_stmt = text("""
            INSERT INTO etl(name) VALUES (:name)
            ON CONFLICT (name) DO NOTHING
        """)
        with app.app_context():
            for row in csv_reader:
                if not row:
                    continue
                etl_name = row[0].strip()
                if etl_name == '':
                    continue
                db.session.execute(insert_stmt, {"name": etl_name})
            db.session.commit()
        return jsonify({'message':'File uploaded successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/etls', methods=['GET'])
def get_etls():
    try:
        # اگر جدول etl یا etls دوتا هستند، می‌تونیم از union استفاده کنیم:
        rows = db.session.execute(text("SELECT name FROM etl UNION SELECT name FROM etls")).fetchall()
        names = [r[0] for r in rows]
        return jsonify({"etls": names}), 200
    except Exception:
        # موقتاً خالی برمی‌گردانیم اگر مشکلی بود
        return jsonify({"etls": []}), 200
