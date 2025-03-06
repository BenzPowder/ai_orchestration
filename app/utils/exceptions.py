class AIOrchestrationError(Exception):
    """
    คลาสหลักสำหรับข้อผิดพลาดในระบบ AI Orchestration
    """
    def __init__(self, message: str = "เกิดข้อผิดพลาดในระบบ AI Orchestration"):
        self.message = message
        super().__init__(self.message)

class AIManagerError(AIOrchestrationError):
    """
    ข้อผิดพลาดที่เกิดจาก AI Manager
    """
    def __init__(self, message: str = "เกิดข้อผิดพลาดใน AI Manager"):
        super().__init__(message)

class SubAgentError(AIOrchestrationError):
    """
    ข้อผิดพลาดที่เกิดจาก Sub-Agent
    """
    def __init__(self, message: str = "เกิดข้อผิดพลาดใน Sub-Agent"):
        super().__init__(message)

class MessageAnalysisError(AIManagerError):
    """
    ข้อผิดพลาดในการวิเคราะห์ข้อความ
    """
    def __init__(self, message: str = "ไม่สามารถวิเคราะห์ข้อความได้"):
        super().__init__(message)

class AgentSelectionError(AIManagerError):
    """
    ข้อผิดพลาดในการเลือก Agent
    """
    def __init__(self, message: str = "ไม่สามารถเลือก Agent ที่เหมาะสมได้"):
        super().__init__(message)

class InvalidMessageTypeError(AIOrchestrationError):
    """
    ข้อผิดพลาดเมื่อประเภทข้อความไม่ถูกต้อง
    """
    def __init__(self, message: str = "ประเภทข้อความไม่ถูกต้อง"):
        super().__init__(message)

class DatabaseError(AIOrchestrationError):
    """
    ข้อผิดพลาดในการเชื่อมต่อหรือจัดการฐานข้อมูล
    """
    def __init__(self, message: str = "เกิดข้อผิดพลาดในการจัดการฐานข้อมูล"):
        super().__init__(message)

class ConfigurationError(AIOrchestrationError):
    """
    ข้อผิดพลาดในการตั้งค่าระบบ
    """
    def __init__(self, message: str = "เกิดข้อผิดพลาดในการตั้งค่าระบบ"):
        super().__init__(message)

class AuthenticationError(AIOrchestrationError):
    """
    ข้อผิดพลาดในการยืนยันตัวตน
    """
    def __init__(self, message: str = "เกิดข้อผิดพลาดในการยืนยันตัวตน"):
        super().__init__(message)

class ValidationError(AIOrchestrationError):
    """
    ข้อผิดพลาดในการตรวจสอบความถูกต้องของข้อมูล
    """
    def __init__(self, message: str = "ข้อมูลไม่ถูกต้องหรือไม่ครบถ้วน"):
        super().__init__(message)

class ExternalServiceError(AIOrchestrationError):
    """
    ข้อผิดพลาดในการเชื่อมต่อกับบริการภายนอก
    """
    def __init__(self, message: str = "เกิดข้อผิดพลาดในการเชื่อมต่อกับบริการภายนอก"):
        super().__init__(message)

class RateLimitError(AIOrchestrationError):
    """
    ข้อผิดพลาดเมื่อเกินขีดจำกัดการใช้งาน
    """
    def __init__(self, message: str = "เกินขีดจำกัดการใช้งาน กรุณาลองใหม่ในภายหลัง"):
        super().__init__(message)

class TimeoutError(AIOrchestrationError):
    """
    ข้อผิดพลาดเมื่อการดำเนินการใช้เวลานานเกินไป
    """
    def __init__(self, message: str = "การดำเนินการใช้เวลานานเกินไป"):
        super().__init__(message)

class ResourceNotFoundError(AIOrchestrationError):
    """
    ข้อผิดพลาดเมื่อไม่พบทรัพยากรที่ต้องการ
    """
    def __init__(self, message: str = "ไม่พบทรัพยากรที่ต้องการ"):
        super().__init__(message)

class PermissionError(AIOrchestrationError):
    """
    ข้อผิดพลาดเกี่ยวกับสิทธิ์การเข้าถึง
    """
    def __init__(self, message: str = "ไม่มีสิทธิ์ในการเข้าถึง"):
        super().__init__(message)
