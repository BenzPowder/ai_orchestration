from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # ความสัมพันธ์กับโมเดลอื่นๆ
    projects = db.relationship('Project', backref='owner', lazy=True)
    webhooks = db.relationship('Webhook', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
