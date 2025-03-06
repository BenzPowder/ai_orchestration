from . import db, generate_uuid
from datetime import datetime

class AIAgent(db.Model):
    """โมเดลสำหรับเก็บข้อมูล AI Sub-Agent"""
    __tablename__ = 'ai_agents'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    templates = db.relationship('AgentTemplate', backref='agent', lazy=True)
    tenant_permissions = db.relationship('TenantAgentPermission', backref='agent', lazy=True)

    def get_default_template(self):
        """ดึง template เริ่มต้นของ Agent"""
        return AgentTemplate.query.filter_by(
            agent_id=self.id,
            is_default=True
        ).first()

    def to_dict(self):
        """แปลงข้อมูลเป็น dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'endpoint': self.endpoint,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AgentTemplate(db.Model):
    """โมเดลสำหรับเก็บ Prompt Template ของ AI Sub-Agent"""
    __tablename__ = 'agent_templates'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    agent_id = db.Column(db.String(36), db.ForeignKey('ai_agents.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """แปลงข้อมูลเป็น dictionary"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'name': self.name,
            'content': self.content,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class TenantAgentPermission(db.Model):
    """โมเดลสำหรับเก็บสิทธิ์การใช้งาน AI Sub-Agent ของแต่ละ Tenant"""
    __tablename__ = 'tenant_agent_permissions'

    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), primary_key=True)
    agent_id = db.Column(db.String(36), db.ForeignKey('ai_agents.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """แปลงข้อมูลเป็น dictionary"""
        return {
            'tenant_id': self.tenant_id,
            'agent_id': self.agent_id,
            'created_at': self.created_at.isoformat()
        }
