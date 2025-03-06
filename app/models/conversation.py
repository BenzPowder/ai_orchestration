from datetime import datetime
from typing import Dict, Any, Optional
from pymongo import MongoClient
from bson import ObjectId

class Conversation:
    """
    คลาสสำหรับจัดการข้อมูลการสนทนา
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
        self.conversations = self.db.conversations

    def create_conversation(
        self,
        user_id: str,
        message: str,
        response: str,
        message_type: str,
        analysis: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        สร้างบันทึกการสนทนาใหม่
        
        Args:
            user_id (str): ID ของผู้ใช้
            message (str): ข้อความจากผู้ใช้
            response (str): ข้อความตอบกลับ
            message_type (str): ประเภทของข้อความ (complaint/welfare)
            analysis (Dict[str, Any]): ผลการวิเคราะห์ข้อความ
            metadata (Dict[str, Any], optional): ข้อมูลเพิ่มเติม
            
        Returns:
            str: ID ของบันทึกที่สร้าง
        """
        conversation = {
            'user_id': user_id,
            'message': message,
            'response': response,
            'message_type': message_type,
            'analysis': analysis,
            'metadata': metadata or {},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.conversations.insert_one(conversation)
        return str(result.inserted_id)

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        ดึงข้อมูลการสนทนาตาม ID
        
        Args:
            conversation_id (str): ID ของการสนทนา
            
        Returns:
            Optional[Dict[str, Any]]: ข้อมูลการสนทนาที่พบ หรือ None ถ้าไม่พบ
        """
        result = self.conversations.find_one({'_id': ObjectId(conversation_id)})
        if result:
            result['_id'] = str(result['_id'])
        return result

    def get_user_conversations(
        self,
        user_id: str,
        limit: int = 10,
        skip: int = 0
    ) -> list:
        """
        ดึงประวัติการสนทนาของผู้ใช้
        
        Args:
            user_id (str): ID ของผู้ใช้
            limit (int): จำนวนรายการที่ต้องการ
            skip (int): จำนวนรายการที่ต้องการข้าม
            
        Returns:
            list: รายการประวัติการสนทนา
        """
        cursor = self.conversations.find(
            {'user_id': user_id}
        ).sort(
            'created_at', -1
        ).skip(skip).limit(limit)
        
        conversations = []
        for conv in cursor:
            conv['_id'] = str(conv['_id'])
            conversations.append(conv)
        
        return conversations

    def update_conversation(
        self,
        conversation_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        อัปเดตข้อมูลการสนทนา
        
        Args:
            conversation_id (str): ID ของการสนทนา
            update_data (Dict[str, Any]): ข้อมูลที่ต้องการอัปเดต
            
        Returns:
            bool: True ถ้าอัปเดตสำเร็จ
        """
        update_data['updated_at'] = datetime.utcnow()
        result = self.conversations.update_one(
            {'_id': ObjectId(conversation_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        ลบข้อมูลการสนทนา
        
        Args:
            conversation_id (str): ID ของการสนทนา
            
        Returns:
            bool: True ถ้าลบสำเร็จ
        """
        result = self.conversations.delete_one({'_id': ObjectId(conversation_id)})
        return result.deleted_count > 0

    def get_conversation_stats(self, user_id: str) -> Dict[str, Any]:
        """
        ดึงสถิติการสนทนาของผู้ใช้
        
        Args:
            user_id (str): ID ของผู้ใช้
            
        Returns:
            Dict[str, Any]: สถิติการสนทนา
        """
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {
                '_id': '$message_type',
                'count': {'$sum': 1},
                'last_interaction': {'$max': '$created_at'}
            }}
        ]
        
        results = list(self.conversations.aggregate(pipeline))
        
        stats = {
            'total_conversations': sum(r['count'] for r in results),
            'by_type': {r['_id']: r['count'] for r in results},
            'last_interaction': max(r['last_interaction'] for r in results) if results else None
        }
        
        return stats
