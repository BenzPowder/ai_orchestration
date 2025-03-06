from . import db, generate_uuid
from datetime import datetime

class Tenant(db.Model):
    """โมเดลสำหรับเก็บข้อมูลหน่วยงาน (Tenant)"""
    __tablename__ = 'tenants'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='tenant', lazy=True)
    webhooks = db.relationship('Webhook', backref='tenant', lazy=True)
    
    @classmethod
    def get_by_api_key(cls, api_key):
        """ค้นหา Tenant จาก API Key"""
        return cls.query.filter_by(api_key=api_key, status='active').first()

    def to_dict(self):
        """แปลงข้อมูลเป็น dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
