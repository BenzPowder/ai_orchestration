from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction
)
from typing import Dict, Any, List
import os

class LineService:
    """
    บริการจัดการการเชื่อมต่อและทำงานกับ LINE Messaging API
    """
    
    def __init__(self):
        """
        กำหนดค่าเริ่มต้นสำหรับ LINE API
        """
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.channel_secret = os.getenv('LINE_CHANNEL_SECRET')
        
        self.line_bot_api = LineBotApi(self.channel_access_token)
        self.handler = WebhookHandler(self.channel_secret)
        
    def verify_webhook(self, signature: str, body: str) -> bool:
        """
        ตรวจสอบความถูกต้องของ webhook request
        
        Args:
            signature (str): ลายเซ็นของ request
            body (str): เนื้อหาของ request
            
        Returns:
            bool: True ถ้า request ถูกต้อง
        """
        try:
            self.handler.verify(body, signature)
            return True
        except InvalidSignatureError:
            return False
            
    async def send_message(self, user_id: str, message: str, quick_replies: List[Dict[str, str]] = None) -> None:
        """
        ส่งข้อความไปยังผู้ใช้
        
        Args:
            user_id (str): ID ของผู้ใช้
            message (str): ข้อความที่ต้องการส่ง
            quick_replies (List[Dict[str, str]], optional): รายการปุ่มตอบกลับด่วน
        """
        messages = [TextSendMessage(text=message)]
        
        # เพิ่ม quick replies ถ้ามี
        if quick_replies:
            quick_reply_buttons = [
                QuickReplyButton(
                    action=MessageAction(label=reply['label'], text=reply['text'])
                )
                for reply in quick_replies
            ]
            messages[0].quick_reply = QuickReply(items=quick_reply_buttons)
        
        await self.line_bot_api.push_message(user_id, messages)
        
    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        ดึงข้อมูลโปรไฟล์ของผู้ใช้
        
        Args:
            user_id (str): ID ของผู้ใช้
            
        Returns:
            Dict[str, Any]: ข้อมูลโปรไฟล์ของผู้ใช้
        """
        profile = await self.line_bot_api.get_profile(user_id)
        return {
            'user_id': profile.user_id,
            'display_name': profile.display_name,
            'picture_url': profile.picture_url,
            'status_message': profile.status_message
        }
        
    def handle_message_event(self, event: MessageEvent) -> None:
        """
        จัดการกับ message event จาก LINE
        
        Args:
            event (MessageEvent): Event ที่ได้รับจาก LINE
        """
        if isinstance(event.message, TextMessage):
            # ส่งข้อความไปยัง AI Manager
            from app.agents.manager import AIManager
            manager = AIManager()
            response = await manager.process_message(event.message.text)
            
            # ส่งการตอบกลับไปยังผู้ใช้
            await self.send_message(event.source.user_id, response)
            
    def create_rich_menu(self, rich_menu_data: Dict[str, Any]) -> str:
        """
        สร้าง rich menu ใหม่
        
        Args:
            rich_menu_data (Dict[str, Any]): ข้อมูลสำหรับสร้าง rich menu
            
        Returns:
            str: ID ของ rich menu ที่สร้าง
        """
        rich_menu_id = self.line_bot_api.create_rich_menu(rich_menu_data)
        return rich_menu_id
        
    def set_default_rich_menu(self, rich_menu_id: str) -> None:
        """
        กำหนด rich menu เริ่มต้น
        
        Args:
            rich_menu_id (str): ID ของ rich menu ที่ต้องการตั้งเป็นค่าเริ่มต้น
        """
        self.line_bot_api.set_default_rich_menu(rich_menu_id)
