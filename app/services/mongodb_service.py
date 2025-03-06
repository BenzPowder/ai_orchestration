from typing import Dict, Any, List
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os

class MongoDBService:
    """
    บริการจัดการการเชื่อมต่อและทำงานกับ MongoDB
    รองรับการค้นหาด้วย Full-Text Search และ Vector Search
    """
    
    def __init__(self):
        """
        เชื่อมต่อกับ MongoDB และกำหนดค่าเริ่มต้น
        """
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('MONGODB_DB_NAME', 'ai_orchestration')]
        
        # สร้าง collections
        self.conversations = self.db['conversations']
        self.agent_responses = self.db['agent_responses']
        self.project_data = self.db['project_data']
        
        # สร้าง indexes
        self._create_indexes()
        
    def _create_indexes(self) -> None:
        """
        สร้าง indexes สำหรับการค้นหาที่มีประสิทธิภาพ
        """
        # Text index สำหรับ Full-Text Search
        self.conversations.create_index([
            ('user_message', 'text'),
            ('bot_response', 'text')
        ])
        
        # Index ตามเวลา
        self.conversations.create_index('timestamp')
        self.agent_responses.create_index('timestamp')
        
    def save_conversation(self, data: Dict[str, Any]) -> str:
        """
        บันทึกข้อมูลการสนทนาใหม่
        
        Args:
            data (Dict[str, Any]): ข้อมูลการสนทนา
            
        Returns:
            str: ID ของเอกสารที่ถูกบันทึก
        """
        result = self.conversations.insert_one(data)
        return str(result.inserted_id)
        
    def save_agent_response(self, data: Dict[str, Any]) -> str:
        """
        บันทึกการตอบกลับของ Agent
        
        Args:
            data (Dict[str, Any]): ข้อมูลการตอบกลับ
            
        Returns:
            str: ID ของเอกสารที่ถูกบันทึก
        """
        result = self.agent_responses.insert_one(data)
        return str(result.inserted_id)
        
    def find_relevant_data(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        ค้นหาข้อมูลที่เกี่ยวข้องโดยใช้ Full-Text Search
        
        Args:
            query (str): คำค้นหา
            limit (int): จำนวนผลลัพธ์สูงสุด
            
        Returns:
            List[Dict[str, Any]]: รายการข้อมูลที่เกี่ยวข้อง
        """
        results = self.conversations.find(
            {'$text': {'$search': query}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})]).limit(limit)
        
        return list(results)
        
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        ดึงประวัติการสนทนาล่าสุด
        
        Args:
            limit (int): จำนวนการสนทนาที่ต้องการ
            
        Returns:
            List[Dict[str, Any]]: รายการประวัติการสนทนา
        """
        return list(self.conversations.find().sort('timestamp', -1).limit(limit))
        
    def save_project_data(self, data: Dict[str, Any]) -> str:
        """
        บันทึกข้อมูลโปรเจกต์
        
        Args:
            data (Dict[str, Any]): ข้อมูลโปรเจกต์
            
        Returns:
            str: ID ของเอกสารที่ถูกบันทึก
        """
        result = self.project_data.insert_one(data)
        return str(result.inserted_id)
        
    def get_project_data(self, project_id: str) -> Dict[str, Any]:
        """
        ดึงข้อมูลโปรเจกต์
        
        Args:
            project_id (str): ID ของโปรเจกต์
            
        Returns:
            Dict[str, Any]: ข้อมูลโปรเจกต์
        """
        return self.project_data.find_one({'_id': project_id})
        
    def get_current_timestamp(self) -> datetime:
        """
        สร้าง timestamp ปัจจุบัน
        
        Returns:
            datetime: เวลาปัจจุบัน
        """
        return datetime.utcnow()
