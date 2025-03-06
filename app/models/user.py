from datetime import datetime
from typing import Dict, Any, Optional, List
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Tenant(db.Model):
    """โมเดลสำหรับจัดการข้อมูลผู้เช่า"""
    __tablename__ = 'tenants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ความสัมพันธ์กับตาราง users
    users = db.relationship('User', backref='tenant', lazy=True)

class User(db.Model):
    """โมเดลสำหรับจัดการข้อมูลผู้ใช้งาน"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='active')
    preferences = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """ตั้งค่ารหัสผ่านโดยการเข้ารหัส"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """ตรวจสอบรหัสผ่าน"""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_user(
        cls,
        tenant_id: int,
        username: str,
        password: str,
        role: str = 'user',
        status: str = 'active'
    ) -> 'User':
        """สร้างผู้ใช้งานใหม่"""
        user = cls(
            tenant_id=tenant_id,
            username=username,
            role=role,
            status=status
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_user(cls, user_id: int) -> Optional['User']:
        """ดึงข้อมูลผู้ใช้ตาม ID"""
        return cls.query.get(user_id)

    def update(self, update_data: Dict[str, Any]) -> bool:
        """อัปเดตข้อมูลผู้ใช้"""
        for key, value in update_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return True

    def get_preferences(self) -> Dict[str, Any]:
        """ดึงการตั้งค่าของผู้ใช้"""
        return self.preferences or {}

    def update_preferences(self, preferences: Dict[str, Any]) -> bool:
        """อัปเดตการตั้งค่าของผู้ใช้"""
        self.preferences = preferences
        db.session.commit()
        return True

    @classmethod
    def get_active_users(
        cls,
        minutes: int = 30,
        tenant_id: Optional[int] = None
    ) -> List['User']:
        """ดึงรายชื่อผู้ใช้ที่กำลังใช้งานอยู่"""
        cutoff_time = datetime.utcnow().replace(
            minute=datetime.utcnow().minute - minutes
        )
        query = cls.query.filter(cls.updated_at >= cutoff_time)
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
            
        return query.all()
