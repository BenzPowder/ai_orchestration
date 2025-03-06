from flask import Blueprint, request, abort
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import StringPromptTemplate
from typing import List, Dict, Any
from app.services.openai_service import get_llm
from app.services.mongodb_service import MongoDBService
from app.agents.sub_agents.ea_service_agent import EAServiceAgent

class AIManager:
    """
    AI Manager (Main Agent) ทำหน้าที่เป็นผู้จัดการหลักในการวิเคราะห์และจัดการข้อความจากผู้ใช้
    """
    
    def __init__(self):
        """
        กำหนดค่าเริ่มต้นและลงทะเบียน Sub-Agents
        """
        self.llm = get_llm()
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.db_service = MongoDBService()
        self.sub_agents = {}
        
        # ลงทะเบียน Sub-Agents
        self.ea_service = EAServiceAgent()
        self.register_sub_agent('ea_service', self.ea_service)
        
    def register_sub_agent(self, name: str, agent: Any) -> None:
        """
        ลงทะเบียน Sub-Agent ใหม่
        """
        self.sub_agents[name] = agent
        
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """
        วิเคราะห์ข้อความจากผู้ใช้และตัดสินใจว่าจะส่งไปยัง Sub-Agent ใด
        """
        # ใช้ LangChain ในการวิเคราะห์ข้อความ
        analysis_prompt = f"""วิเคราะห์ข้อความต่อไปนี้และระบุว่าเกี่ยวข้องกับประเภทใด:
        
        ข้อความ: {message}
        
        ประเภทที่เป็นไปได้:
        1. เรื่องร้องเรียน (ไฟถนน, น้ำท่วม, ขยะ, เสียงดัง, ทางเท้า, สัตว์รบกวน, ความปลอดภัย)
        2. สวัสดิการสังคม (ผู้สูงอายุ, คนพิการ, เงินสงเคราะห์, ผู้มีรายได้น้อย, ช่วยเหลือฉุกเฉิน)
        3. อื่นๆ
        
        โปรดวิเคราะห์:
        1. ประเภทหลัก
        2. ประเภทย่อย (ถ้ามี)
        3. ระดับความเร่งด่วน (สูง/กลาง/ต่ำ)
        """
        
        analysis = self.llm.predict(analysis_prompt)
        
        return {
            "original_message": message,
            "analysis": analysis,
            "recommended_agent": self._select_agent(analysis)
        }
        
    def _select_agent(self, analysis: str) -> str:
        """
        เลือก Sub-Agent ที่เหมาะสมจากผลการวิเคราะห์
        """
        # ตรวจสอบว่าเป็นเรื่องร้องเรียนหรือสวัสดิการ
        if any(keyword in analysis.lower() for keyword in ['ร้องเรียน', 'ไฟถนน', 'น้ำท่วม', 'ขยะ', 'เสียง', 'ทางเท้า', 'สัตว์', 'ปลอดภัย']):
            return 'ea_service'
        elif any(keyword in analysis.lower() for keyword in ['สวัสดิการ', 'ผู้สูงอายุ', 'คนพิการ', 'เงินสงเคราะห์', 'รายได้น้อย', 'ฉุกเฉิน']):
            return 'ea_service'
        return 'default'
        
    async def process_message(self, message: str) -> str:
        """
        ประมวลผลข้อความและส่งต่อไปยัง Sub-Agent ที่เหมาะสม
        """
        # วิเคราะห์ข้อความ
        analysis = self.analyze_message(message)
        
        # เลือก Sub-Agent
        agent_name = analysis["recommended_agent"]
        if agent_name not in self.sub_agents:
            return "ขออภัย ไม่พบ Agent ที่เหมาะสมสำหรับคำขอนี้"
            
        # ส่งข้อความไปยัง Sub-Agent
        agent = self.sub_agents[agent_name]
        response = await agent.process(message, analysis)
        
        # บันทึกการสนทนาลงฐานข้อมูล
        self._save_conversation(message, response, analysis)
        
        return response
        
    def _save_conversation(self, message: str, response: str, analysis: Dict[str, Any]) -> None:
        """
        บันทึกประวัติการสนทนาลงฐานข้อมูล
        """
        conversation_data = {
            "user_message": message,
            "bot_response": response,
            "analysis": analysis,
            "timestamp": self.db_service.get_current_timestamp()
        }
        self.db_service.save_conversation(conversation_data)
