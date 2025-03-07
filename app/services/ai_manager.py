from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.models import db
from app.models.ai_agent import AIAgent, AgentTemplate
from app.models.tenant import Tenant
from app.models.logging import UsageLog, Webhook
from app.utils.webhook import send_webhook_event

class AIManager:
    """
    AI Manager สำหรับจัดการ AI Sub-Agent
    """
    def __init__(self, openai_api_key: str):
        """
        กำหนดค่าเริ่มต้นสำหรับ AI Manager
        
        Args:
            openai_api_key (str): OpenAI API Key
        """
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )

    def process_message(
        self,
        tenant_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        ประมวลผลข้อความและเลือก AI Sub-Agent ที่เหมาะสม
        
        Args:
            tenant_id (str): ID ของ Tenant
            message (str): ข้อความที่ต้องการประมวลผล
            context (Dict[str, Any], optional): ข้อมูลเพิ่มเติม
            
        Returns:
            Dict[str, Any]: ผลลัพธ์การประมวลผล
        """
        # ตรวจสอบ Tenant
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            raise ValueError("Tenant not found")

        # เริ่มจับเวลา
        start_time = datetime.utcnow()
        
        try:
            # ดึงรายการ AI Sub-Agent ที่ Tenant มีสิทธิ์ใช้งาน
            available_agents = self._get_available_agents(tenant_id)
            
            # เลือก AI Sub-Agent ที่เหมาะสม
            selected_agent = self._select_agent(message, available_agents)
            
            # ประมวลผลด้วย AI Sub-Agent
            response = self._process_with_agent(selected_agent, message, context)
            
            # คำนวณเวลาที่ใช้
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # บันทึก Log
            log = UsageLog(
                tenant_id=tenant_id,
                agent_id=selected_agent.id,
                user_id=context.get('user_id') if context else None,
                request_type='message',
                request_data={'message': message, 'context': context},
                response_data=response,
                processing_time=processing_time,
                status='success'
            )
            db.session.add(log)
            db.session.commit()
            
            # ส่ง Webhook (ถ้ามี)
            self._send_webhooks(tenant_id, 'message_processed', {
                'agent_id': selected_agent.id,
                'message': message,
                'response': response,
                'processing_time': processing_time
            })
            
            return {
                'success': True,
                'agent': selected_agent.to_dict(),
                'response': response,
                'processing_time': processing_time
            }
            
        except Exception as e:
            # บันทึก Log กรณีเกิดข้อผิดพลาด
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            log = UsageLog(
                tenant_id=tenant_id,
                agent_id=None,
                user_id=context.get('user_id') if context else None,
                request_type='message',
                request_data={'message': message, 'context': context},
                response_data={'error': str(e)},
                processing_time=processing_time,
                status='error'
            )
            db.session.add(log)
            db.session.commit()
            
            # ส่ง Webhook กรณีเกิดข้อผิดพลาด
            self._send_webhooks(tenant_id, 'message_error', {
                'message': message,
                'error': str(e),
                'processing_time': processing_time
            })
            
            raise

    def _get_available_agents(self, tenant_id: str) -> List[AIAgent]:
        """
        ดึงรายการ AI Sub-Agent ที่ Tenant มีสิทธิ์ใช้งาน
        
        Args:
            tenant_id (str): ID ของ Tenant
            
        Returns:
            List[AIAgent]: รายการ AI Sub-Agent
        """
        return AIAgent.query.join(
            'tenant_permissions'
        ).filter(
            AIAgent.status == 'active',
            AIAgent.tenant_permissions.any(tenant_id=tenant_id)
        ).all()

    def _select_agent(self, message: str, agents: List[AIAgent]) -> AIAgent:
        """
        เลือก AI Sub-Agent ที่เหมาะสมกับข้อความ
        
        Args:
            message (str): ข้อความที่ต้องการประมวลผล
            agents (List[AIAgent]): รายการ AI Sub-Agent ที่มีให้เลือก
            
        Returns:
            AIAgent: AI Sub-Agent ที่เหมาะสม
        """
        if not agents:
            raise ValueError("No available agents")
            
        # TODO: ใช้ AI วิเคราะห์และเลือก Agent ที่เหมาะสม
        # ตอนนี้เลือกตัวแรกไปก่อน
        return agents[0]

    def _process_with_agent(
        self,
        agent: AIAgent,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        ประมวลผลข้อความด้วย AI Sub-Agent
        
        Args:
            agent (AIAgent): AI Sub-Agent ที่จะใช้
            message (str): ข้อความที่ต้องการประมวลผล
            context (Dict[str, Any], optional): ข้อมูลเพิ่มเติม
            
        Returns:
            Dict[str, Any]: ผลลัพธ์การประมวลผล
        """
        # ดึง Template
        template = agent.get_default_template()
        if not template:
            raise ValueError(f"No template found for agent {agent.name}")
            
        # สร้าง Prompt
        prompt = ChatPromptTemplate.from_template(template.content)
        
        # สร้าง Chain และประมวลผล
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({
            "message": message,
            "context": context or {}
        })
        
        return {
            'content': response,
            'agent_type': agent.type
        }

    def _send_webhooks(
        self,
        tenant_id: str,
        event: str,
        data: Dict[str, Any]
    ) -> None:
        """
        ส่ง Webhook ไปยัง URL ที่กำหนด
        
        Args:
            tenant_id (str): ID ของ Tenant
            event (str): ชื่อเหตุการณ์
            data (Dict[str, Any]): ข้อมูลที่จะส่ง
        """
        webhooks = Webhook.query.filter_by(
            tenant_id=tenant_id,
            event=event,
            status='active'
        ).all()
        
        for webhook in webhooks:
            try:
                send_webhook_event(webhook.url, event, data)
            except Exception as e:
                # บันทึก Log แต่ไม่ raise error
                print(f"Webhook error: {str(e)}")
