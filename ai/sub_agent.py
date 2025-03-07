from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any, List
import os

class SubAgent:
    def __init__(self, agent_id: str, name: str, prompt_template: str = None):
        self.agent_id = agent_id
        self.name = name
        self.llm = OpenAI(
            temperature=0.7,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.prompt_template = prompt_template or self._default_prompt_template()
        self.training_data = []
        
    def _default_prompt_template(self) -> str:
        """สร้าง default prompt template"""
        return """คำถาม/คำสั่ง: {input}

ข้อมูลเพิ่มเติม:
{context}

กรุณาตอบคำถามหรือดำเนินการตามคำสั่งข้างต้น โดยใช้ข้อมูลที่มีให้"""
        
    def add_training_data(self, input_text: str, expected_output: str):
        """เพิ่มข้อมูลสำหรับการเทรน"""
        self.training_data.append({
            'input': input_text,
            'output': expected_output
        })
        
    def update_prompt_template(self, new_template: str):
        """อัพเดท prompt template"""
        self.prompt_template = new_template
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """ประมวลผลข้อมูลที่ได้รับ"""
        # สร้าง prompt จาก template
        prompt = PromptTemplate(
            input_variables=["input", "context"],
            template=self.prompt_template
        )
        
        # สร้าง chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # ประมวลผล
        context = self._prepare_context(data)
        response = chain.run(input=data.get('input', ''), context=context)
        
        return {
            'agent_id': self.agent_id,
            'response': response,
            'status': 'success'
        }
        
    def _prepare_context(self, data: Dict[str, Any]) -> str:
        """เตรียมข้อมูล context สำหรับ prompt"""
        context_parts = []
        
        # เพิ่มข้อมูลเพิ่มเติมจาก data
        for key, value in data.items():
            if key != 'input':
                context_parts.append(f"{key}: {value}")
                
        # เพิ่มตัวอย่างการใช้งานจาก training data
        if self.training_data:
            context_parts.append("\nตัวอย่างการใช้งาน:")
            for example in self.training_data[:3]:  # แสดงแค่ 3 ตัวอย่าง
                context_parts.append(f"Input: {example['input']}")
                context_parts.append(f"Output: {example['output']}\n")
                
        return "\n".join(context_parts)
