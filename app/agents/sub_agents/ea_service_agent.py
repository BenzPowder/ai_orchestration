from typing import Dict, Any, List
from app.agents.sub_agents.base import BaseSubAgent
from app.agents.sub_agents.templates.ea_service_templates import (
    COMPLAINT_TYPES, WELFARE_TYPES, BASIC_QUESTIONS,
    SPECIFIC_QUESTIONS, WELFARE_INFO, get_urgency_level,
    get_response_template
)
from app.services.openai_service import OpenAIService

class EAServiceAgent(BaseSubAgent):
    """
    Agent สำหรับจัดการเรื่องร้องเรียนและสวัสดิการสังคม
    """
    
    def __init__(self):
        super().__init__(name="ea_service")
        self.openai_service = OpenAIService()
        
    async def process(self, message: str, analysis: Dict[str, Any]) -> str:
        """
        ประมวลผลข้อความและให้การตอบสนองที่เหมาะสม
        
        Args:
            message (str): ข้อความจากผู้ใช้
            analysis (Dict[str, Any]): ผลการวิเคราะห์จาก AI Manager
            
        Returns:
            str: ข้อความตอบกลับ
        """
        # วิเคราะห์ประเภทของข้อความ
        message_type = await self._analyze_message_type(message)
        
        if message_type.get('category') == 'complaint':
            return await self._handle_complaint(message, message_type)
        elif message_type.get('category') == 'welfare':
            return await self._handle_welfare(message, message_type)
        else:
            return "ขออภัย ไม่สามารถระบุประเภทของคำขอได้ กรุณาระบุว่าต้องการแจ้งเรื่องร้องเรียน หรือสอบถามเรื่องสวัสดิการ"
            
    async def _analyze_message_type(self, message: str) -> Dict[str, Any]:
        """
        วิเคราะห์ประเภทของข้อความว่าเป็นการร้องเรียนหรือสอบถามสวัสดิการ
        """
        prompt = f"""วิเคราะห์ข้อความต่อไปนี้และระบุว่าเป็นการร้องเรียนหรือสอบถามสวัสดิการ:
        ข้อความ: {message}
        
        หากเป็นการร้องเรียน ให้ระบุประเภท:
        {', '.join(COMPLAINT_TYPES.values())}
        
        หากเป็นการสอบถามสวัสดิการ ให้ระบุประเภท:
        {', '.join(WELFARE_TYPES.values())}
        """
        
        analysis = await self.openai_service.analyze_sentiment(prompt)
        return self._parse_analysis_result(analysis)
        
    def _parse_analysis_result(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """
        แปลงผลการวิเคราะห์เป็นรูปแบบที่ใช้งานได้
        """
        # ตรรกะในการแปลงผลการวิเคราะห์
        # จะถูกพัฒนาตามความต้องการที่เพิ่มขึ้น
        return {
            'category': 'complaint',  # หรือ 'welfare'
            'type': 'street_light'  # หรือประเภทอื่นๆ
        }
        
    async def _handle_complaint(self, message: str, message_type: Dict[str, str]) -> str:
        """
        จัดการกับเรื่องร้องเรียน
        """
        complaint_type = message_type.get('type')
        
        # ตรวจสอบข้อมูลที่จำเป็น
        missing_info = await self._check_required_info(message, complaint_type)
        if missing_info:
            return self._create_info_request(missing_info, complaint_type)
            
        # สร้างการตอบกลับ
        response = get_response_template(complaint_type)
        urgency = get_urgency_level(complaint_type, {})
        
        # บันทึกข้อมูลการร้องเรียน
        complaint_data = {
            'type': complaint_type,
            'message': message,
            'urgency': urgency,
            'status': 'received'
        }
        self._save_complaint(complaint_data)
        
        return response
        
    async def _handle_welfare(self, message: str, message_type: Dict[str, str]) -> str:
        """
        จัดการกับการสอบถามสวัสดิการ
        """
        welfare_type = message_type.get('type')
        
        if welfare_type in WELFARE_INFO:
            info = WELFARE_INFO[welfare_type]
            response = f"""ข้อมูลเกี่ยวกับ{WELFARE_TYPES[welfare_type]}:
            
            คุณสมบัติที่ต้องมี:
            {chr(10).join(f'- {req}' for req in info['requirements'])}
            
            เอกสารที่ต้องเตรียม:
            {chr(10).join(f'- {doc}' for doc in info['documents'])}
            
            ต้องการทราบข้อมูลเพิ่มเติมหรือไม่?"""
        else:
            response = "ขออภัย ไม่พบข้อมูลสวัสดิการที่ต้องการ กรุณาระบุประเภทสวัสดิการที่ต้องการสอบถาม"
            
        return response
        
    async def _check_required_info(self, message: str, complaint_type: str) -> List[str]:
        """
        ตรวจสอบว่ามีข้อมูลที่จำเป็นครบถ้วนหรือไม่
        """
        missing_info = []
        
        # ตรวจสอบข้อมูลพื้นฐาน
        for key, question in BASIC_QUESTIONS.items():
            if not self._has_info(message, key):
                missing_info.append(question)
                
        # ตรวจสอบข้อมูลเฉพาะตามประเภท
        if complaint_type in SPECIFIC_QUESTIONS:
            for question in SPECIFIC_QUESTIONS[complaint_type]:
                if not self._has_specific_info(message, question):
                    missing_info.append(question)
                    
        return missing_info
        
    def _has_info(self, message: str, info_type: str) -> bool:
        """
        ตรวจสอบว่ามีข้อมูลที่ต้องการในข้อความหรือไม่
        """
        # ตรรกะในการตรวจสอบข้อมูล
        # จะถูกพัฒนาตามความต้องการที่เพิ่มขึ้น
        return False
        
    def _has_specific_info(self, message: str, question: str) -> bool:
        """
        ตรวจสอบว่ามีข้อมูลเฉพาะที่ต้องการในข้อความหรือไม่
        """
        # ตรรกะในการตรวจสอบข้อมูลเฉพาะ
        # จะถูกพัฒนาตามความต้องการที่เพิ่มขึ้น
        return False
        
    def _create_info_request(self, missing_info: List[str], complaint_type: str) -> str:
        """
        สร้างข้อความขอข้อมูลเพิ่มเติม
        """
        response = "เพื่อให้สามารถดำเนินการได้อย่างรวดเร็ว กรุณาให้ข้อมูลเพิ่มเติมดังนี้:\n\n"
        for info in missing_info:
            response += f"- {info}\n"
        return response
        
    def _save_complaint(self, complaint_data: Dict[str, Any]) -> None:
        """
        บันทึกข้อมูลการร้องเรียนลงฐานข้อมูล
        """
        self.db_service.save_project_data({
            'type': 'complaint',
            'data': complaint_data,
            'timestamp': self.db_service.get_current_timestamp()
        })
