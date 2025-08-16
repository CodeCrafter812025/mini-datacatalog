from flask import render_template, request, jsonify
from app import app
from .models import db, ETL, Table
import csv
import io

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.csv'):
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        csv_reader = csv.reader(stream)
        next(csv_reader)  # Skip header
        
        for row in csv_reader:
            if len(row) > 0:
                etl_name = row[0]
                existing_etl = ETL.query.filter_by(name=etl_name).first()
                if not existing_etl:
                    new_etl = ETL(name=etl_name)
                    db.session.add(new_etl)
        
        db.session.commit()
        return jsonify({"message": "File uploaded successfully"}), 200
    
    return jsonify({"error": "Invalid file format"}), 400

@app.route('/etls', methods=['GET'])
def get_etls():
    etls = ETL.query.all()
    result = {}
    for etl in etls:
        tables = [table.name for table in etl.tables]
        result[etl.name] = tables
    return jsonify(result)
