from flask import Blueprint, request, abort
from app.services.line_service import LineService
import os

bp = Blueprint('line_webhook', __name__)
line_service = LineService()

@bp.route("/webhook", methods=['POST'])
async def webhook():
    """
    รับและจัดการ webhook events จาก LINE
    """
    # ตรวจสอบ signature
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    if not line_service.verify_webhook(signature, body):
        abort(400)
        
    try:
        # จัดการกับ webhook event
        await line_service.handler.handle(body, signature)
        return 'OK'
    except Exception as e:
        print(f"Error: {str(e)}")
        abort(500)
        
@bp.route("/", methods=['GET'])
def index():
    """
    หน้าแรกสำหรับตรวจสอบสถานะเซิร์ฟเวอร์
    """
    return {
        'status': 'running',
        'version': '1.0.0'
    }

# Event handlers
@line_service.handler.add(MessageEvent)
def handle_message(event):
    """
    จัดการกับ message events
    """
    line_service.handle_message_event(event)
