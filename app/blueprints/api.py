from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from datetime import datetime
import json

from app.models import db
from app.models.tenant import Tenant
from app.models.ai_agent import AIAgent, AgentTemplate, TenantAgentPermission
from app.models.logging import UsageLog
from app.services.ai_manager import AIManager

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def require_api_key(f):
    """Decorator สำหรับตรวจสอบ API Key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'error': 'API Key is required'
            }), 401
            
        tenant = Tenant.get_by_api_key(api_key)
        if not tenant:
            return jsonify({
                'error': 'Invalid API Key'
            }), 401
            
        return f(tenant, *args, **kwargs)
    return decorated

@api_bp.route('/process', methods=['POST'])
@require_api_key
def process_message(tenant):
    """
    ประมวลผลข้อความด้วย AI
    
    Request:
    {
        "message": "ข้อความที่ต้องการประมวลผล",
        "context": {
            "user_id": "รหัสผู้ใช้ (optional)",
            "metadata": {}
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Invalid request data'
            }), 400
            
        # สร้าง AI Manager
        ai_manager = AIManager(current_app.config['OPENAI_API_KEY'])
        
        # ประมวลผลข้อความ
        result = ai_manager.process_message(
            tenant_id=tenant.id,
            message=data['message'],
            context=data.get('context')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/agents', methods=['GET'])
@require_api_key
def list_agents(tenant):
    """ดึงรายการ AI Sub-Agent ที่มีสิทธิ์ใช้งาน"""
    try:
        agents = AIAgent.query.join(
            'tenant_permissions'
        ).filter(
            AIAgent.status == 'active',
            AIAgent.tenant_permissions.any(tenant_id=tenant.id)
        ).all()
        
        return jsonify([
            agent.to_dict() for agent in agents
        ])
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/agents/<agent_id>/templates', methods=['GET'])
@require_api_key
def get_agent_templates(tenant, agent_id):
    """ดึงรายการ Template ของ AI Sub-Agent"""
    try:
        # ตรวจสอบสิทธิ์
        permission = TenantAgentPermission.query.filter_by(
            tenant_id=tenant.id,
            agent_id=agent_id
        ).first()
        
        if not permission:
            return jsonify({
                'error': 'Permission denied'
            }), 403
            
        templates = AgentTemplate.query.filter_by(
            agent_id=agent_id
        ).all()
        
        return jsonify([
            template.to_dict() for template in templates
        ])
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@api_bp.route('/usage/stats', methods=['GET'])
@require_api_key
def get_usage_stats(tenant):
    """ดึงสถิติการใช้งาน AI"""
    try:
        # ดึงพารามิเตอร์
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        agent_id = request.args.get('agent_id')
        
        # สร้าง query
        query = UsageLog.query.filter_by(tenant_id=tenant.id)
        
        if start_date:
            query = query.filter(UsageLog.created_at >= start_date)
        if end_date:
            query = query.filter(UsageLog.created_at <= end_date)
        if agent_id:
            query = query.filter_by(agent_id=agent_id)
            
        # ดึงข้อมูล
        logs = query.all()
        
        # คำนวณสถิติ
        total_requests = len(logs)
        total_processing_time = sum(log.processing_time or 0 for log in logs)
        success_count = len([log for log in logs if log.status == 'success'])
        error_count = len([log for log in logs if log.status == 'error'])
        
        return jsonify({
            'total_requests': total_requests,
            'total_processing_time': total_processing_time,
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': (success_count / total_requests * 100) if total_requests > 0 else 0
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
