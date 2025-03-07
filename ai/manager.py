from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List, Dict, Any
import os

class AIManager:
    def __init__(self):
        self.llm = OpenAI(
            temperature=0.7,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.sub_agents = {}
        
    def register_sub_agent(self, agent_id: str, agent):
        """ลงทะเบียน Sub-agent"""
        self.sub_agents[agent_id] = agent
        
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """วิเคราะห์ข้อความและเลือก Sub-agent ที่เหมาะสม"""
        prompt = PromptTemplate(
            input_variables=["message"],
            template="""วิเคราะห์ข้อความต่อไปนี้และระบุ:
            1. ประเภทของคำถาม/คำสั่ง
            2. Sub-agent ที่ควรจะจัดการ
            3. ข้อมูลสำคัญที่ต้องใช้ในการประมวลผล
            
            ข้อความ: {message}
            
            กรุณาตอบในรูปแบบ JSON ที่มีโครงสร้างดังนี้:
            {{
                "type": "ประเภทของคำถาม/คำสั่ง",
                "target_agent": "รหัสของ Sub-agent ที่เหมาะสม",
                "data": {{
                    "key": "value"
                }}
            }}"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(message=message)
        return response
        
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """ประมวลผลข้อมูลจาก Webhook"""
        # วิเคราะห์ข้อความ
        analysis = self.analyze_message(webhook_data.get('message', ''))
        
        # เลือก Sub-agent ที่เหมาะสม
        target_agent = self.sub_agents.get(analysis['target_agent'])
        if not target_agent:
            return {
                'status': 'error',
                'message': f'ไม่พบ Sub-agent ที่เหมาะสม ({analysis["target_agent"]})'
            }
            
        # ส่งข้อมูลไปยัง Sub-agent
        result = target_agent.process(analysis['data'])
        return {
            'status': 'success',
            'data': result
        }
        
    def handle_line_message(self, line_event) -> str:
        """จัดการข้อความจาก LINE"""
        message = line_event.message.text
        analysis = self.analyze_message(message)
        
        target_agent = self.sub_agents.get(analysis['target_agent'])
        if not target_agent:
            return "ขออภัย ไม่สามารถประมวลผลคำขอของคุณได้ในขณะนี้"
            
        result = target_agent.process(analysis['data'])
        return result.get('response', 'ขออภัย เกิดข้อผิดพลาดในการประมวลผล')
