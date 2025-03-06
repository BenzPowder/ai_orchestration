from datetime import datetime
from app import db

class Tenant(db.Model):
    """โมเดลสำหรับจัดการข้อมูลผู้เช่า"""
    __tablename__ = 'tenants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ความสัมพันธ์กับตาราง users
    users = db.relationship('User', backref='tenant', lazy=True)

    def __repr__(self):
        return f'<Tenant {self.name}>'
