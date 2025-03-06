from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

from app.models import db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.ai_agent import AIAgent, AgentTemplate, TenantAgentPermission
from app.models.logging import UsageLog, Webhook

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """หน้าเข้าสู่ระบบ"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.index'))
        
        flash('อีเมลหรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """ออกจากระบบ"""
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def index():
    """หน้าแดชบอร์ดหลัก"""
    # ดึงข้อมูลสถิติ
    tenant_id = current_user.tenant_id
    last_24h = datetime.utcnow() - timedelta(hours=24)
    
    # จำนวนคำขอใน 24 ชั่วโมง
    total_requests = UsageLog.query.filter(
        UsageLog.tenant_id == tenant_id,
        UsageLog.created_at >= last_24h
    ).count()
    
    # อัตราความสำเร็จ
    success_count = UsageLog.query.filter(
        UsageLog.tenant_id == tenant_id,
        UsageLog.created_at >= last_24h,
        UsageLog.status == 'success'
    ).count()
    
    success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
    
    # AI Agent ที่ใช้งานมากที่สุด
    top_agents = db.session.query(
        AIAgent,
        db.func.count(UsageLog.id).label('usage_count')
    ).join(
        UsageLog,
        UsageLog.agent_id == AIAgent.id
    ).filter(
        UsageLog.tenant_id == tenant_id,
        UsageLog.created_at >= last_24h
    ).group_by(
        AIAgent.id
    ).order_by(
        db.desc('usage_count')
    ).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        total_requests=total_requests,
        success_rate=success_rate,
        top_agents=top_agents
    )

@admin_bp.route('/agents')
@login_required
def list_agents():
    """แสดงรายการ AI Sub-Agent"""
    tenant_id = current_user.tenant_id
    agents = AIAgent.query.join(
        'tenant_permissions'
    ).filter(
        AIAgent.tenant_permissions.any(tenant_id=tenant_id)
    ).all()
    
    return render_template(
        'admin/agents/list.html',
        agents=agents
    )

@admin_bp.route('/agents/new', methods=['GET', 'POST'])
@login_required
def create_agent():
    """สร้าง AI Sub-Agent ใหม่"""
    if request.method == 'POST':
        try:
            # สร้าง Agent
            agent = AIAgent(
                name=request.form['name'],
                description=request.form['description'],
                type=request.form['type'],
                endpoint=request.form['endpoint']
            )
            db.session.add(agent)
            
            # สร้าง Template
            template = AgentTemplate(
                agent=agent,
                name='Default Template',
                content=request.form['template'],
                is_default=True
            )
            db.session.add(template)
            
            # ให้สิทธิ์ Tenant
            permission = TenantAgentPermission(
                tenant_id=current_user.tenant_id,
                agent=agent
            )
            db.session.add(permission)
            
            db.session.commit()
            flash('สร้าง AI Sub-Agent สำเร็จ', 'success')
            return redirect(url_for('admin.list_agents'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    return render_template('admin/agents/form.html')

@admin_bp.route('/agents/<agent_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_agent(agent_id):
    """แก้ไข AI Sub-Agent"""
    agent = AIAgent.query.get_or_404(agent_id)
    
    # ตรวจสอบสิทธิ์
    permission = TenantAgentPermission.query.filter_by(
        tenant_id=current_user.tenant_id,
        agent_id=agent_id
    ).first_or_404()
    
    if request.method == 'POST':
        try:
            agent.name = request.form['name']
            agent.description = request.form['description']
            agent.type = request.form['type']
            agent.endpoint = request.form['endpoint']
            
            # อัปเดต Template
            template = agent.get_default_template()
            if template:
                template.content = request.form['template']
            
            db.session.commit()
            flash('แก้ไข AI Sub-Agent สำเร็จ', 'success')
            return redirect(url_for('admin.list_agents'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    return render_template(
        'admin/agents/form.html',
        agent=agent,
        template=agent.get_default_template()
    )

@admin_bp.route('/agents/<agent_id>/delete', methods=['POST'])
@login_required
def delete_agent(agent_id):
    """ลบ AI Sub-Agent"""
    agent = AIAgent.query.get_or_404(agent_id)
    
    # ตรวจสอบสิทธิ์
    permission = TenantAgentPermission.query.filter_by(
        tenant_id=current_user.tenant_id,
        agent_id=agent_id
    ).first_or_404()
    
    try:
        # ลบ Template
        AgentTemplate.query.filter_by(agent_id=agent_id).delete()
        
        # ลบสิทธิ์
        TenantAgentPermission.query.filter_by(agent_id=agent_id).delete()
        
        # ลบ Agent
        db.session.delete(agent)
        db.session.commit()
        
        flash('ลบ AI Sub-Agent สำเร็จ', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    return redirect(url_for('admin.list_agents'))

@admin_bp.route('/webhooks')
@login_required
def list_webhooks():
    """แสดงรายการ Webhook"""
    webhooks = Webhook.query.filter_by(
        tenant_id=current_user.tenant_id
    ).all()
    
    return render_template(
        'admin/webhooks/list.html',
        webhooks=webhooks
    )

@admin_bp.route('/webhooks/new', methods=['GET', 'POST'])
@login_required
def create_webhook():
    """สร้าง Webhook ใหม่"""
    if request.method == 'POST':
        try:
            webhook = Webhook(
                tenant_id=current_user.tenant_id,
                name=request.form['name'],
                url=request.form['url'],
                events=request.form.getlist('events'),
                headers=json.loads(request.form.get('headers', '{}'))
            )
            db.session.add(webhook)
            db.session.commit()
            
            flash('สร้าง Webhook สำเร็จ', 'success')
            return redirect(url_for('admin.list_webhooks'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    return render_template('admin/webhooks/form.html')

@admin_bp.route('/webhooks/<webhook_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_webhook(webhook_id):
    """แก้ไข Webhook"""
    webhook = Webhook.query.filter_by(
        id=webhook_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()
    
    if request.method == 'POST':
        try:
            webhook.name = request.form['name']
            webhook.url = request.form['url']
            webhook.events = request.form.getlist('events')
            webhook.headers = json.loads(request.form.get('headers', '{}'))
            
            db.session.commit()
            flash('แก้ไข Webhook สำเร็จ', 'success')
            return redirect(url_for('admin.list_webhooks'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    return render_template(
        'admin/webhooks/form.html',
        webhook=webhook
    )

@admin_bp.route('/webhooks/<webhook_id>/delete', methods=['POST'])
@login_required
def delete_webhook(webhook_id):
    """ลบ Webhook"""
    webhook = Webhook.query.filter_by(
        id=webhook_id,
        tenant_id=current_user.tenant_id
    ).first_or_404()
    
    try:
        db.session.delete(webhook)
        db.session.commit()
        flash('ลบ Webhook สำเร็จ', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
    
    return redirect(url_for('admin.list_webhooks'))

@admin_bp.route('/stats')
@login_required
def view_stats():
    """แสดงสถิติการใช้งาน"""
    # ดึงพารามิเตอร์
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    agent_id = request.args.get('agent_id')
    
    # ตั้งค่าเริ่มต้น
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.utcnow().strftime('%Y-%m-%d')
        
    # ดึงข้อมูลสถิติ
    query = UsageLog.query.filter(
        UsageLog.tenant_id == current_user.tenant_id,
        UsageLog.created_at >= start_date,
        UsageLog.created_at <= end_date
    )
    
    if agent_id:
        query = query.filter_by(agent_id=agent_id)
        
    logs = query.all()
    
    # คำนวณสถิติ
    stats = {
        'total_requests': len(logs),
        'total_processing_time': sum(log.processing_time or 0 for log in logs),
        'success_count': len([log for log in logs if log.status == 'success']),
        'error_count': len([log for log in logs if log.status == 'error'])
    }
    
    stats['success_rate'] = (stats['success_count'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
    
    # ดึงรายการ Agent
    agents = AIAgent.query.join(
        'tenant_permissions'
    ).filter(
        AIAgent.tenant_permissions.any(tenant_id=current_user.tenant_id)
    ).all()
    
    return render_template(
        'admin/stats.html',
        stats=stats,
        agents=agents,
        start_date=start_date,
        end_date=end_date,
        selected_agent_id=agent_id
    )
