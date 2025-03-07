import os
import json
import uuid
from datetime import datetime

class WebhookLog:
    """คลาสสำหรับเก็บประวัติการทำงานของ webhook"""
    def __init__(self, webhook_id, status, message, details=None):
        self.id = str(uuid.uuid4())
        self.webhook_id = webhook_id
        self.timestamp = datetime.now().isoformat()
        self.status = status
        self.message = message
        self.details = details

    def to_dict(self):
        """แปลงข้อมูลเป็น dictionary"""
        return {
            'id': self.id,
            'webhook_id': self.webhook_id,
            'timestamp': self.timestamp,
            'status': self.status,
            'message': self.message,
            'details': self.details
        }

    @classmethod
    def from_dict(cls, data):
        """สร้าง WebhookLog object จาก dictionary"""
        log = cls(
            webhook_id=data['webhook_id'],
            status=data['status'],
            message=data['message'],
            details=data.get('details')
        )
        log.id = data['id']
        log.timestamp = data['timestamp']
        return log

class Webhook:
    """คลาสสำหรับจัดการ webhook"""
    def __init__(self, name, description=None, url_path=None, secret_key=None, is_active=True, id=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.url_path = url_path or f"webhook/{self.id}"
        self.secret_key = secret_key or str(uuid.uuid4())
        self.is_active = is_active
        self.agent_ids = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def to_dict(self):
        """แปลงข้อมูลเป็น dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url_path': self.url_path,
            'secret_key': self.secret_key,
            'is_active': self.is_active,
            'agent_ids': self.agent_ids,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """สร้าง Webhook object จาก dictionary"""
        webhook = cls(
            name=data['name'],
            description=data.get('description'),
            url_path=data.get('url_path'),
            secret_key=data.get('secret_key'),
            is_active=data.get('is_active', True),
            id=data['id']
        )
        webhook.agent_ids = data.get('agent_ids', [])
        webhook.created_at = data.get('created_at', webhook.created_at)
        webhook.updated_at = data.get('updated_at', webhook.updated_at)
        return webhook

    def add_agent(self, agent_id):
        """เพิ่ม agent เข้ากับ webhook"""
        if agent_id not in self.agent_ids:
            self.agent_ids.append(agent_id)
            self.updated_at = datetime.now().isoformat()

    def remove_agent(self, agent_id):
        """ลบ agent ออกจาก webhook"""
        if agent_id in self.agent_ids:
            self.agent_ids.remove(agent_id)
            self.updated_at = datetime.now().isoformat()

    def get_logs(self):
        """ดึงประวัติการทำงานของ webhook"""
        try:
            # โหลดข้อมูลจากไฟล์
            data_dir = 'data'
            log_file = os.path.join(data_dir, f"webhook_logs_{self.id}.json")
            
            if not os.path.exists(log_file):
                return []
                
            with open(log_file, 'r', encoding='utf-8') as f:
                logs_data = json.load(f)
                
            # แปลงข้อมูลเป็น WebhookLog objects
            logs = []
            for log_data in logs_data:
                logs.append(WebhookLog.from_dict(log_data))
                
            # เรียงลำดับตามเวลาล่าสุด
            logs.sort(key=lambda x: x.timestamp, reverse=True)
            return logs
        except Exception as e:
            print(f"Error loading logs for webhook {self.id}: {str(e)}")
            return []

    def add_log(self, status, message, details=None):
        """เพิ่มประวัติการทำงานใหม่"""
        try:
            # สร้าง log ใหม่
            log = WebhookLog(
                webhook_id=self.id,
                status=status,
                message=message,
                details=details
            )
            
            # โหลดข้อมูลเดิม
            data_dir = 'data'
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            log_file = os.path.join(data_dir, f"webhook_logs_{self.id}.json")
            logs_data = []
            
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs_data = json.load(f)
            
            # เพิ่ม log ใหม่
            logs_data.append(log.to_dict())
            
            # บันทึกลงไฟล์
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"Error adding log for webhook {self.id}: {str(e)}")
            return False
