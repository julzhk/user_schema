from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


class Der(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    validation_schema = db.Column(db.Integer, nullable=False, default=1)
    data = db.Column(JSON, nullable=True)  # JSONB field

    def __repr__(self):
        return f'<Der {self.name}>'


class Schema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    data = db.Column(JSON, nullable=True)  # JSONB field
    rules = db.Column(db.String(2048), nullable=True, default='')

    def __repr__(self):
        return f'<Schema {self.name}>'
