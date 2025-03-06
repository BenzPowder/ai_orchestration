import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app.models import db
from app.models.user import User
from app.models.tenant import Tenant

@click.command('create-admin')
@click.option('--email', prompt='อีเมลแอดมิน', help='อีเมลสำหรับผู้ดูแลระบบ')
@click.option('--username', prompt='ชื่อผู้ใช้', help='ชื่อผู้ใช้สำหรับผู้ดูแลระบบ')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='รหัสผ่านสำหรับผู้ดูแลระบบ')
@with_appcontext
def create_admin(email, username, password):
    """สร้างผู้ใช้แอดมินและ tenant เริ่มต้น"""
    try:
        # สร้าง tenant เริ่มต้น
        tenant = Tenant.query.filter_by(name='admin').first()
        if not tenant:
            tenant = Tenant(name='admin', description='ผู้ดูแลระบบ')
            db.session.add(tenant)
            db.session.flush()

        # ตรวจสอบว่ามีผู้ใช้นี้อยู่แล้วหรือไม่
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            click.echo('มีผู้ใช้นี้อยู่ในระบบแล้ว')
            return

        # สร้างผู้ใช้ใหม่
        user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=True,
            tenant_id=tenant.id,
            role='admin',
            status='active'
        )
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'สร้างผู้ดูแลระบบ {email} เรียบร้อยแล้ว')
        
    except Exception as e:
        db.session.rollback()
        click.echo(f'เกิดข้อผิดพลาด: {str(e)}')
