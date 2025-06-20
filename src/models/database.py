from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    """Modelo base com campos comuns"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

