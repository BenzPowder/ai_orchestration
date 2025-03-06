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
        self.tenants = self.db.tenants

    def create_tenant(
        self,
        tenant_id: str,
        name: str
    ) -> str:
        """
        สร้างผู้เช่าใหม่
        
        Args:
            tenant_id (str): ID ของผู้เช่า
            name (str): ชื่อผู้เช่า
            
        Returns:
            str: ID ของผู้เช่าที่สร้าง
        """
        tenant = {
            '_id': ObjectId(tenant_id),
            'name': name,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.tenants.insert_one(tenant)
        return str(result.inserted_id)

    def create_user(
        self,
        user_id: str,
        tenant_id: str,
        username: str,
        password: str,
        role: str = 'user',
        status: str = 'active'
    ) -> str:
        """
        สร้างผู้ใช้งานใหม่
        
        Args:
            user_id (str): ID ของผู้ใช้
            tenant_id (str): ID ของผู้เช่า
            username (str): ชื่อผู้ใช้
            password (str): รหัสผ่าน
            role (str, optional): บทบาทของผู้ใช้ (admin หรือ user)
            status (str, optional): สถานะของผู้ใช้ (active หรือ inactive)
            
        Returns:
            str: ID ของผู้ใช้ที่สร้าง
        """
        user = {
            '_id': ObjectId(user_id),
            'tenant_id': ObjectId(tenant_id),
            'username': username,
            'password_hash': self._generate_password_hash(password),
            'role': role,
            'status': status,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.users.insert_one(user)
        return str(result.inserted_id)

    def _generate_password_hash(self, password: str) -> str:
        """
        เข้ารหัสรหัสผ่าน
        
        Args:
            password (str): รหัสผ่าน
            
        Returns:
            str: รหัสผ่านเข้ารหัส
        """
        # implement password hashing algorithm here
        pass

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        ดึงข้อมูลผู้ใช้ตาม ID
        
        Args:
            user_id (str): ID ของผู้ใช้
            
        Returns:
            Optional[Dict[str, Any]]: ข้อมูลผู้ใช้ที่พบ หรือ None ถ้าไม่พบ
        """
        result = self.users.find_one({'_id': ObjectId(user_id)})
        if result:
            result['_id'] = str(result['_id'])
            result['tenant_id'] = str(result['tenant_id'])
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
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
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
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        ดึงรายชื่อผู้ใช้ที่กำลังใช้งานอยู่
        
        Args:
            minutes (int): จำนวนนาทีย้อนหลังที่ถือว่ายังใช้งานอยู่
            tenant_id (str, optional): กรองตามผู้เช่า
            
        Returns:
            List[Dict[str, Any]]: รายการผู้ใช้ที่กำลังใช้งาน
        """
        query = {
            'updated_at': {
                '$gte': datetime.utcnow().replace(
                    minute=datetime.utcnow().minute - minutes
                )
            }
        }
        
        if tenant_id:
            query['tenant_id'] = ObjectId(tenant_id)
            
        cursor = self.users.find(query)
        
        users = []
        for user in cursor:
            user['_id'] = str(user['_id'])
            user['tenant_id'] = str(user['tenant_id'])
            users.append(user)
            
        return users
