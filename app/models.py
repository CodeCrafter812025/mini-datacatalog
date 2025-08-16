from app import db

class ETL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    tables = db.relationship('Table', backref='etl', lazy=True)

    def __repr__(self):
        return f'<ETL {self.name}>'

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    etl_id = db.Column(db.Integer, db.ForeignKey('etl.id'), nullable=False)

    def __repr__(self):
        return f'<Table {self.name}>'
