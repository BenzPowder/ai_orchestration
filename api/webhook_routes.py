from flask import request, jsonify
from . import api
from models import Webhook, WebhookLog
from extensions import db
from ai import AIManager
from datetime import datetime

ai_manager = AIManager()

@api.route('/webhook/<path:url_path>', methods=['POST'])
def handle_webhook(url_path):
    """จัดการ request ที่เข้ามาทาง webhook"""
    # ค้นหา webhook จาก url_path
    webhook = Webhook.query.filter_by(url_path=url_path, is_active=True).first()
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
        
    # ตรวจสอบ secret key
    if webhook.secret_key != request.headers.get('X-Webhook-Secret'):
        return jsonify({'error': 'Invalid secret key'}), 401
        
    # บันทึก webhook log
    log = WebhookLog(
        webhook_id=webhook.id,
        request_data=request.json,
        status_code=200
    )
    
    try:
        # ประมวลผลข้อมูลผ่าน AI Manager
        result = ai_manager.process_webhook({
            'agent_id': webhook.agent_id,
            'message': request.json.get('message', ''),
            'data': request.json
        })
        
        # บันทึกผลลัพธ์
        log.response_data = result
        db.session.add(log)
        db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        log.status_code = 500
        log.response_data = {'error': str(e)}
        db.session.add(log)
        db.session.commit()
        return jsonify({'error': str(e)}), 500
        
@api.route('/webhook/logs/<int:webhook_id>', methods=['GET'])
def get_webhook_logs(webhook_id):
    """ดูประวัติการเรียกใช้ webhook"""
    logs = WebhookLog.query.filter_by(webhook_id=webhook_id)\
        .order_by(WebhookLog.created_at.desc())\
        .limit(100)\
        .all()
        
    return jsonify([{
        'id': log.id,
        'request_data': log.request_data,
        'response_data': log.response_data,
        'status_code': log.status_code,
        'created_at': log.created_at.isoformat()
    } for log in logs])
