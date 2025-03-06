from abc import ABC, abstractmethod
from typing import Dict, Any
from app.services.openai_service import get_llm
from app.services.mongodb_service import MongoDBService

class BaseSubAgent(ABC):
    """
    คลาสพื้นฐานสำหรับ Sub-Agents ทั้งหมด
    กำหนดโครงสร้างและวิธีการทำงานพื้นฐานที่ Sub-Agents ทุกตัวต้องมี
    """
    
    def __init__(self, name: str):
        """
        กำหนดค่าเริ่มต้นสำหรับ Sub-Agent
        
        Args:
            name (str): ชื่อของ Sub-Agent
        """
        self.name = name
        self.llm = get_llm()
        self.db_service = MongoDBService()
        
    @abstractmethod
    async def process(self, message: str, analysis: Dict[str, Any]) -> str:
        """
        ประมวลผลข้อความที่ได้รับจาก AI Manager
        
        Args:
            message (str): ข้อความจากผู้ใช้
            analysis (Dict[str, Any]): ผลการวิเคราะห์จาก AI Manager
            
        Returns:
            str: ข้อความตอบกลับไปยังผู้ใช้
        """
        pass
        
    def _get_context(self, message: str) -> Dict[str, Any]:
        """
        ดึงข้อมูลที่เกี่ยวข้องจากฐานข้อมูลเพื่อใช้ในการประมวลผล
        
        Args:
            message (str): ข้อความจากผู้ใช้
            
        Returns:
            Dict[str, Any]: ข้อมูลที่เกี่ยวข้องจากฐานข้อมูล
        """
        # ค้นหาข้อมูลที่เกี่ยวข้องจาก MongoDB
        return self.db_service.find_relevant_data(message)
        
    def _save_response(self, message: str, response: str, context: Dict[str, Any]) -> None:
        """
        บันทึกการตอบกลับลงฐานข้อมูล
        
        Args:
            message (str): ข้อความจากผู้ใช้
            response (str): ข้อความตอบกลับ
            context (Dict[str, Any]): ข้อมูลที่ใช้ในการประมวลผล
        """
        response_data = {
            "agent_name": self.name,
            "user_message": message,
            "bot_response": response,
            "context": context,
            "timestamp": self.db_service.get_current_timestamp()
        }
        self.db_service.save_agent_response(response_data)
        
    def _format_response(self, response: str) -> str:
        """
        จัดรูปแบบข้อความตอบกลับให้เหมาะสม
        
        Args:
            response (str): ข้อความตอบกลับที่ต้องการจัดรูปแบบ
            
        Returns:
            str: ข้อความตอบกลับที่จัดรูปแบบแล้ว
        """
        # สามารถเพิ่มการจัดรูปแบบข้อความตามต้องการ
        return response.strip()
