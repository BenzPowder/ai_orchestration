from datetime import datetime
from typing import Dict, Any, Optional, List
from bson import ObjectId
from pymongo import MongoClient

class Agent:
    """
    คลาสสำหรับจัดการข้อมูล Sub-Agent
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
        self.agents = self.db.agents

    def create_agent(
        self,
        name: str,
        agent_type: str,
        description: str,
        endpoint: str,
        prompt_templates: List[Dict[str, str]] = None,
        active: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        สร้าง Sub-Agent ใหม่
        
        Args:
            name (str): ชื่อ Sub-Agent
            agent_type (str): ประเภทของ Agent (complaint/welfare/custom)
            description (str): คำอธิบาย
            endpoint (str): API Endpoint
            prompt_templates (List[Dict[str, str]], optional): รายการ Prompt Template
            active (bool): สถานะการใช้งาน
            metadata (Dict[str, Any], optional): ข้อมูลเพิ่มเติม
            
        Returns:
            str: ID ของ Agent ที่สร้าง
        """
        agent = {
            'name': name,
            'type': agent_type,
            'description': description,
            'endpoint': endpoint,
            'prompt_templates': prompt_templates or [],
            'active': active,
            'metadata': metadata or {},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.agents.insert_one(agent)
        return str(result.inserted_id)

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        ดึงข้อมูล Sub-Agent ตาม ID
        
        Args:
            agent_id (str): ID ของ Agent
            
        Returns:
            Optional[Dict[str, Any]]: ข้อมูล Agent ที่พบ หรือ None ถ้าไม่พบ
        """
        result = self.agents.find_one({'_id': ObjectId(agent_id)})
        if result:
            result['_id'] = str(result['_id'])
        return result

    def get_all_agents(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        ดึงรายการ Sub-Agent ทั้งหมด
        
        Args:
            active_only (bool): ดึงเฉพาะ Agent ที่เปิดใช้งานเท่านั้น
            
        Returns:
            List[Dict[str, Any]]: รายการ Agent
        """
        query = {'active': True} if active_only else {}
        cursor = self.agents.find(query).sort('name', 1)
        
        agents = []
        for agent in cursor:
            agent['_id'] = str(agent['_id'])
            agents.append(agent)
            
        return agents

    def update_agent(
        self,
        agent_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        อัปเดตข้อมูล Sub-Agent
        
        Args:
            agent_id (str): ID ของ Agent
            update_data (Dict[str, Any]): ข้อมูลที่ต้องการอัปเดต
            
        Returns:
            bool: True ถ้าอัปเดตสำเร็จ
        """
        update_data['updated_at'] = datetime.utcnow()
        result = self.agents.update_one(
            {'_id': ObjectId(agent_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def delete_agent(self, agent_id: str) -> bool:
        """
        ลบ Sub-Agent
        
        Args:
            agent_id (str): ID ของ Agent
            
        Returns:
            bool: True ถ้าลบสำเร็จ
        """
        result = self.agents.delete_one({'_id': ObjectId(agent_id)})
        return result.deleted_count > 0

    def get_agent_by_endpoint(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        ดึงข้อมูล Sub-Agent ตาม Endpoint
        
        Args:
            endpoint (str): Endpoint ของ Agent
            
        Returns:
            Optional[Dict[str, Any]]: ข้อมูล Agent ที่พบ หรือ None ถ้าไม่พบ
        """
        result = self.agents.find_one({'endpoint': endpoint, 'active': True})
        if result:
            result['_id'] = str(result['_id'])
        return result

    def get_agent_templates(self, agent_id: str) -> List[Dict[str, str]]:
        """
        ดึงรายการ Prompt Template ของ Sub-Agent
        
        Args:
            agent_id (str): ID ของ Agent
            
        Returns:
            List[Dict[str, str]]: รายการ Template
        """
        agent = self.get_agent(agent_id)
        return agent.get('prompt_templates', []) if agent else []

    def update_agent_templates(
        self,
        agent_id: str,
        templates: List[Dict[str, str]]
    ) -> bool:
        """
        อัปเดต Prompt Template ของ Sub-Agent
        
        Args:
            agent_id (str): ID ของ Agent
            templates (List[Dict[str, str]]): รายการ Template ใหม่
            
        Returns:
            bool: True ถ้าอัปเดตสำเร็จ
        """
        return self.update_agent(agent_id, {'prompt_templates': templates})
