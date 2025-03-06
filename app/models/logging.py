from . import db, generate_uuid
from datetime import datetime
import json

class UsageLog(db.Model):
    """โมเดลสำหรับเก็บ Log การใช้งาน AI"""
    __tablename__ = 'usage_logs'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    agent_id = db.Column(db.String(36), db.ForeignKey('ai_agents.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    request_type = db.Column(db.String(50), nullable=False)
    request_data = db.Column(db.JSON)
    response_data = db.Column(db.JSON)
    processing_time = db.Column(db.Float)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """แปลงข้อมูลเป็น dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'agent_id': self.agent_id,
            'user_id': self.user_id,
            'request_type': self.request_type,
            'request_data': self.request_data,
            'response_data': self.response_data,
            'processing_time': self.processing_time,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Webhook(db.Model):
    """โมเดลสำหรับเก็บการตั้งค่า Webhook"""
    __tablename__ = 'webhooks'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    events = db.Column(db.JSON, nullable=False)
    headers = db.Column(db.JSON)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """แปลงข้อมูลเป็น dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'url': self.url,
            'events': self.events,
            'headers': self.headers,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
