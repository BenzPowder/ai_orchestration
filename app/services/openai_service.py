from typing import List, Dict, Any
import openai
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
import os

class OpenAIService:
    """
    บริการจัดการการเชื่อมต่อและทำงานกับ OpenAI API
    รองรับการสร้าง embeddings และการใช้งาน AI models
    """
    
    def __init__(self):
        """
        กำหนดค่าเริ่มต้นสำหรับ OpenAI API
        """
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
        self.model = "gpt-4"  # สามารถเปลี่ยนเป็นรุ่นอื่นได้ตามต้องการ
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        สร้างการตอบกลับโดยใช้ OpenAI API
        
        Args:
            prompt (str): คำถามหรือข้อความที่ต้องการให้ AI ตอบ
            context (Dict[str, Any], optional): ข้อมูลเพิ่มเติมสำหรับการตอบ
            
        Returns:
            str: ข้อความตอบกลับจาก AI
        """
        messages = []
        
        # เพิ่ม context ถ้ามี
        if context:
            messages.append({
                "role": "system",
                "content": f"Context: {str(context)}"
            })
            
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        สร้าง embeddings สำหรับข้อความ
        
        Args:
            texts (List[str]): รายการข้อความที่ต้องการสร้าง embeddings
            
        Returns:
            List[List[float]]: รายการ embeddings vectors
        """
        embeddings = []
        for text in texts:
            embedding = await self.embeddings.aembed_query(text)
            embeddings.append(embedding)
        return embeddings
        
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        วิเคราะห์ความรู้สึกของข้อความ
        
        Args:
            text (str): ข้อความที่ต้องการวิเคราะห์
            
        Returns:
            Dict[str, Any]: ผลการวิเคราะห์ความรู้สึก
        """
        prompt = f"""วิเคราะห์ความรู้สึกของข้อความต่อไปนี้:
        "{text}"
        โปรดระบุ:
        1. ความรู้สึกหลัก (เชิงบวก/เชิงลบ/เป็นกลาง)
        2. ระดับความเข้มข้นของความรู้สึก (1-5)
        3. อารมณ์ที่เด่นชัด"""
        
        response = await self.generate_response(prompt)
        
        # แปลงการตอบกลับเป็นรูปแบบ dictionary
        # (ในที่นี้เป็นตัวอย่างอย่างง่าย ควรมีการ parse ที่ซับซ้อนกว่านี้)
        return {
            "text": text,
            "analysis": response
        }
        
def get_llm(temperature: float = 0.7) -> OpenAI:
    """
    สร้างและคืนค่า LangChain LLM instance
    
    Args:
        temperature (float): ค่า temperature สำหรับ model
        
    Returns:
        OpenAI: LangChain LLM instance
    """
    return OpenAI(
        temperature=temperature,
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
