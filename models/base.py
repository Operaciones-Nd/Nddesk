from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = db.Column(db.DateTime)
    
    def soft_delete(self):
        self.deleted_at = datetime.now()
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    
    @classmethod
    def get_active(cls):
        return cls.query.filter(cls.deleted_at.is_(None))
