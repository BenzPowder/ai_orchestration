from datetime import datetime
from typing import Dict, Any, Optional, List
from bson import ObjectId
from pymongo import MongoClient
import json
import csv
from io import StringIO

class TrainingData:
    """
    คลาสสำหรับจัดการข้อมูล Training Data
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
        self.training_data = self.db.training_data

    def create_data(
        self,
        agent_id: str,
        data_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        สร้าง Training Data ใหม่
        
        Args:
            agent_id (str): ID ของ Sub-Agent
            data_type (str): ประเภทข้อมูล (text/qa/conversation)
            content (Any): เนื้อหาข้อมูล
            metadata (Dict[str, Any], optional): ข้อมูลเพิ่มเติม
            
        Returns:
            str: ID ของข้อมูลที่สร้าง
        """
        data = {
            'agent_id': agent_id,
            'type': data_type,
            'content': content,
            'metadata': metadata or {},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.training_data.insert_one(data)
        return str(result.inserted_id)

    def get_data(self, data_id: str) -> Optional[Dict[str, Any]]:
        """
        ดึงข้อมูล Training Data ตาม ID
        
        Args:
            data_id (str): ID ของข้อมูล
            
        Returns:
            Optional[Dict[str, Any]]: ข้อมูลที่พบ หรือ None ถ้าไม่พบ
        """
        result = self.training_data.find_one({'_id': ObjectId(data_id)})
        if result:
            result['_id'] = str(result['_id'])
        return result

    def get_agent_data(
        self,
        agent_id: str,
        data_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        ดึงข้อมูล Training Data ของ Sub-Agent
        
        Args:
            agent_id (str): ID ของ Sub-Agent
            data_type (str, optional): กรองตามประเภทข้อมูล
            
        Returns:
            List[Dict[str, Any]]: รายการข้อมูล
        """
        query = {'agent_id': agent_id}
        if data_type:
            query['type'] = data_type
            
        cursor = self.training_data.find(query).sort('created_at', -1)
        
        data_list = []
        for data in cursor:
            data['_id'] = str(data['_id'])
            data_list.append(data)
            
        return data_list

    def update_data(
        self,
        data_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        อัปเดต Training Data
        
        Args:
            data_id (str): ID ของข้อมูล
            update_data (Dict[str, Any]): ข้อมูลที่ต้องการอัปเดต
            
        Returns:
            bool: True ถ้าอัปเดตสำเร็จ
        """
        update_data['updated_at'] = datetime.utcnow()
        result = self.training_data.update_one(
            {'_id': ObjectId(data_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def delete_data(self, data_id: str) -> bool:
        """
        ลบ Training Data
        
        Args:
            data_id (str): ID ของข้อมูล
            
        Returns:
            bool: True ถ้าลบสำเร็จ
        """
        result = self.training_data.delete_one({'_id': ObjectId(data_id)})
        return result.deleted_count > 0

    def import_from_file(
        self,
        agent_id: str,
        file_content: str,
        file_type: str,
        data_type: str
    ) -> List[str]:
        """
        นำเข้าข้อมูลจากไฟล์
        
        Args:
            agent_id (str): ID ของ Sub-Agent
            file_content (str): เนื้อหาของไฟล์
            file_type (str): ประเภทไฟล์ (txt/csv/json)
            data_type (str): ประเภทข้อมูล (text/qa/conversation)
            
        Returns:
            List[str]: รายการ ID ของข้อมูลที่นำเข้า
        """
        data_list = []
        
        if file_type == 'txt':
            # แยกข้อมูลตามบรรทัด
            lines = file_content.strip().split('\n')
            for line in lines:
                if line.strip():
                    data_list.append({'content': line.strip()})
                    
        elif file_type == 'csv':
            # อ่านไฟล์ CSV
            csv_reader = csv.DictReader(StringIO(file_content))
            for row in csv_reader:
                data_list.append(row)
                
        elif file_type == 'json':
            # แปลง JSON เป็น dict
            data_list = json.loads(file_content)
            if not isinstance(data_list, list):
                data_list = [data_list]
                
        # นำเข้าข้อมูล
        imported_ids = []
        for data in data_list:
            data_id = self.create_data(
                agent_id=agent_id,
                data_type=data_type,
                content=data.get('content') or data,
                metadata=data.get('metadata')
            )
            imported_ids.append(data_id)
            
        return imported_ids

    def export_to_json(
        self,
        agent_id: Optional[str] = None,
        data_type: Optional[str] = None
    ) -> str:
        """
        ส่งออกข้อมูลเป็น JSON
        
        Args:
            agent_id (str, optional): กรองตาม Sub-Agent
            data_type (str, optional): กรองตามประเภทข้อมูล
            
        Returns:
            str: ข้อมูลในรูปแบบ JSON
        """
        query = {}
        if agent_id:
            query['agent_id'] = agent_id
        if data_type:
            query['type'] = data_type
            
        cursor = self.training_data.find(query)
        
        data_list = []
        for data in cursor:
            data['_id'] = str(data['_id'])
            data_list.append(data)
            
        return json.dumps(data_list, ensure_ascii=False, indent=2)

    def get_data_for_rag(
        self,
        agent_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        ดึงข้อมูลสำหรับ Retrieval Augmented Generation
        
        Args:
            agent_id (str): ID ของ Sub-Agent
            query (str): คำค้นหา
            limit (int): จำนวนข้อมูลที่ต้องการ
            
        Returns:
            List[Dict[str, Any]]: รายการข้อมูลที่เกี่ยวข้อง
        """
        # TODO: ใช้ vector database หรือ embedding search
        # สำหรับตอนนี้ใช้การค้นหาแบบง่ายๆ ก่อน
        pipeline = [
            {'$match': {
                'agent_id': agent_id,
                '$text': {'$search': query}
            }},
            {'$limit': limit}
        ]
        
        cursor = self.training_data.aggregate(pipeline)
        
        results = []
        for data in cursor:
            data['_id'] = str(data['_id'])
            results.append(data)
            
        return results
