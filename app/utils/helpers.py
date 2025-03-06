from datetime import datetime
from typing import Dict, Any, List
import re
import logging

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_contact_info(text: str) -> Dict[str, str]:
    """
    แยกข้อมูลการติดต่อจากข้อความ
    
    Args:
        text (str): ข้อความที่ต้องการแยกข้อมูล
        
    Returns:
        Dict[str, str]: ข้อมูลการติดต่อที่พบ
    """
    contact_info = {
        'phone': None,
        'email': None,
        'line_id': None
    }
    
    # ค้นหาเบอร์โทรศัพท์
    phone_pattern = r'(?:โทร|เบอร์|tel|phone|เบอร์โทร)[:\s]*([0-9-]{9,})'
    phone_match = re.search(phone_pattern, text, re.IGNORECASE)
    if phone_match:
        contact_info['phone'] = phone_match.group(1)
    
    # ค้นหาอีเมล
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info['email'] = email_match.group()
    
    # ค้นหา LINE ID
    line_pattern = r'(?:line|ไลน์)[:\s]*([a-zA-Z0-9_.-]+)'
    line_match = re.search(line_pattern, text, re.IGNORECASE)
    if line_match:
        contact_info['line_id'] = line_match.group(1)
    
    return contact_info

def extract_location(text: str) -> Dict[str, Any]:
    """
    แยกข้อมูลสถานที่จากข้อความ
    
    Args:
        text (str): ข้อความที่ต้องการแยกข้อมูล
        
    Returns:
        Dict[str, Any]: ข้อมูลสถานที่ที่พบ
    """
    location_info = {
        'address': None,
        'district': None,
        'coordinates': None
    }
    
    # ค้นหาพิกัด
    coord_pattern = r'(?:พิกัด|location)[:\s]*([\d.,]+)'
    coord_match = re.search(coord_pattern, text, re.IGNORECASE)
    if coord_match:
        location_info['coordinates'] = coord_match.group(1)
    
    # ค้นหาเขต/อำเภอ
    district_pattern = r'(?:เขต|อำเภอ)[:\s]*([ก-๙\s]+)'
    district_match = re.search(district_pattern, text)
    if district_match:
        location_info['district'] = district_match.group(1).strip()
    
    # ค้นหาที่อยู่ทั่วไป
    address_pattern = r'(?:ที่อยู่|บ้านเลขที่|เลขที่)[:\s]*([ก-๙0-9/\s]+)'
    address_match = re.search(address_pattern, text)
    if address_match:
        location_info['address'] = address_match.group(1).strip()
    
    return location_info

def format_complaint_response(complaint_type: str, urgency: str, department: str) -> str:
    """
    สร้างข้อความตอบกลับสำหรับเรื่องร้องเรียน
    
    Args:
        complaint_type (str): ประเภทของเรื่องร้องเรียน
        urgency (str): ระดับความเร่งด่วน
        department (str): หน่วยงานที่รับผิดชอบ
        
    Returns:
        str: ข้อความตอบกลับที่จัดรูปแบบแล้ว
    """
    return f"""ขอบคุณที่แจ้งปัญหา {complaint_type}

เราได้รับเรื่องของท่านแล้ว
- ระดับความเร่งด่วน: {urgency}
- หน่วยงานที่รับผิดชอบ: {department}

เจ้าหน้าที่จะรีบดำเนินการแก้ไขปัญหาโดยเร็วที่สุด
หากมีข้อสงสัยเพิ่มเติม สามารถติดต่อได้ที่เบอร์ 1234 (ตลอด 24 ชั่วโมง)"""

def format_welfare_response(welfare_type: str, requirements: List[str], documents: List[str]) -> str:
    """
    สร้างข้อความตอบกลับสำหรับการสอบถามสวัสดิการ
    
    Args:
        welfare_type (str): ประเภทของสวัสดิการ
        requirements (List[str]): คุณสมบัติที่ต้องมี
        documents (List[str]): เอกสารที่ต้องใช้
        
    Returns:
        str: ข้อความตอบกลับที่จัดรูปแบบแล้ว
    """
    return f"""ข้อมูลเกี่ยวกับ{welfare_type}

คุณสมบัติที่ต้องมี:
{chr(10).join(f'- {req}' for req in requirements)}

เอกสารที่ต้องใช้:
{chr(10).join(f'- {doc}' for doc in documents)}

สามารถติดต่อขอรับบริการได้ที่:
สำนักงานเขต/อำเภอใกล้บ้านท่าน
วันจันทร์-ศุกร์ เวลา 08:30-16:30 น.
สอบถามข้อมูลเพิ่มเติม โทร. 1234"""

def log_conversation(user_id: str, message: str, response: str, analysis: Dict[str, Any]) -> None:
    """
    บันทึก log การสนทนา
    
    Args:
        user_id (str): ID ของผู้ใช้
        message (str): ข้อความจากผู้ใช้
        response (str): ข้อความตอบกลับ
        analysis (Dict[str, Any]): ผลการวิเคราะห์ข้อความ
    """
    logger.info(f"""
    User ID: {user_id}
    Message: {message}
    Analysis: {analysis}
    Response: {response}
    Timestamp: {datetime.now().isoformat()}
    """)
