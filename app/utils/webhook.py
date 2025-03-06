import requests
from typing import Dict, Any
from datetime import datetime
import json

def send_webhook_event(webhook_url: str, event_type: str, data: Dict[Any, Any]) -> bool:
    """
    ส่ง webhook event ไปยัง URL ที่กำหนด
    
    Args:
        webhook_url (str): URL สำหรับส่ง webhook
        event_type (str): ประเภทของ event เช่น 'agent.created', 'agent.deleted'
        data (Dict): ข้อมูลที่จะส่งไปกับ webhook
        
    Returns:
        bool: True ถ้าส่งสำเร็จ, False ถ้าล้มเหลว
    """
    try:
        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5  # timeout 5 วินาที
        )
        
        return response.status_code in (200, 201, 202)
    except Exception:
        return False
