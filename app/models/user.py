from datetime import datetime
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from bson import ObjectId

class User:
    """
    คลาสสำหรับจัดการข้อมูลผู้ใช้งาน
    """
    def __init__(self, mongodb_uri: str, db_name: str):
        """
        เริ่มต้นการเชื่อมต่อกับ MongoDB
        
        Args:
            mongodb_uri (str): URI สำหรับเชื่อมต่อ MongoDB
            db_name (str): ชื่อฐานข้อมูล
        """
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.users = self.db.users

    def create_user(
        self,
        user_id: str,
        platform: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        สร้างผู้ใช้งานใหม่
        
        Args:
            user_id (str): ID ของผู้ใช้
            platform (str): แพลตฟอร์มที่ใช้งาน (LINE, Facebook, etc.)
            metadata (Dict[str, Any], optional): ข้อมูลเพิ่มเติม
            
        Returns:
            str: ID ของผู้ใช้ที่สร้าง
        """
        user = {
            'user_id': user_id,
            'platform': platform,
            'metadata': metadata or {},
            'preferences': {},
            'active_conversations': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_active': datetime.utcnow()
        }
        
        result = self.users.insert_one(user)
        return str(result.inserted_id)

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        ดึงข้อมูลผู้ใช้ตาม ID
        
        Args:
            user_id (str): ID ของผู้ใช้
            
        Returns:
            Optional[Dict[str, Any]]: ข้อมูลผู้ใช้ที่พบ หรือ None ถ้าไม่พบ
        """
        result = self.users.find_one({'user_id': user_id})
        if result:
            result['_id'] = str(result['_id'])
        return result

    def update_user(
        self,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        อัปเดตข้อมูลผู้ใช้
        
        Args:
            user_id (str): ID ของผู้ใช้
            update_data (Dict[str, Any]): ข้อมูลที่ต้องการอัปเดต
            
        Returns:
            bool: True ถ้าอัปเดตสำเร็จ
        """
        update_data['updated_at'] = datetime.utcnow()
        result = self.users.update_one(
            {'user_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def update_last_active(self, user_id: str) -> bool:
        """
        อัปเดตเวลาที่ผู้ใช้มีการทำงานล่าสุด
        
        Args:
            user_id (str): ID ของผู้ใช้
            
        Returns:
            bool: True ถ้าอัปเดตสำเร็จ
        """
        return self.update_user(user_id, {'last_active': datetime.utcnow()})

    def add_active_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> bool:
        """
        เพิ่มการสนทนาที่กำลังดำเนินอยู่
        
        Args:
            user_id (str): ID ของผู้ใช้
            conversation_id (str): ID ของการสนทนา
            
        Returns:
            bool: True ถ้าเพิ่มสำเร็จ
        """
        result = self.users.update_one(
            {'user_id': user_id},
            {
                '$push': {'active_conversations': conversation_id},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0

    def remove_active_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> bool:
        """
        ลบการสนทนาที่เสร็จสิ้นแล้ว
        
        Args:
            user_id (str): ID ของผู้ใช้
            conversation_id (str): ID ของการสนทนา
            
        Returns:
            bool: True ถ้าลบสำเร็จ
        """
        result = self.users.update_one(
            {'user_id': user_id},
            {
                '$pull': {'active_conversations': conversation_id},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        ดึงการตั้งค่าของผู้ใช้
        
        Args:
            user_id (str): ID ของผู้ใช้
            
        Returns:
            Dict[str, Any]: การตั้งค่าของผู้ใช้
        """
        user = self.get_user(user_id)
        return user.get('preferences', {}) if user else {}

    def update_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        อัปเดตการตั้งค่าของผู้ใช้
        
        Args:
            user_id (str): ID ของผู้ใช้
            preferences (Dict[str, Any]): การตั้งค่าที่ต้องการอัปเดต
            
        Returns:
            bool: True ถ้าอัปเดตสำเร็จ
        """
        return self.update_user(user_id, {'preferences': preferences})

    def get_active_users(
        self,
        minutes: int = 30,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        ดึงรายชื่อผู้ใช้ที่กำลังใช้งานอยู่
        
        Args:
            minutes (int): จำนวนนาทีย้อนหลังที่ถือว่ายังใช้งานอยู่
            platform (str, optional): กรองตามแพลตฟอร์ม
            
        Returns:
            List[Dict[str, Any]]: รายการผู้ใช้ที่กำลังใช้งาน
        """
        query = {
            'last_active': {
                '$gte': datetime.utcnow().replace(
                    minute=datetime.utcnow().minute - minutes
                )
            }
        }
        
        if platform:
            query['platform'] = platform
            
        cursor = self.users.find(query)
        
        users = []
        for user in cursor:
            user['_id'] = str(user['_id'])
            users.append(user)
            
        return users
