import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

class Config:
    """
    การตั้งค่าพื้นฐานของแอปพลิเคชัน
    """
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    PORT = int(os.getenv('PORT', 5000))

    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'ai_orchestration')

    # LINE Configuration
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # LangChain Configuration
    LANGCHAIN_VERBOSE = os.getenv('LANGCHAIN_VERBOSE', 'True') == 'True'
    LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')

    # EA Service Configuration
    COMPLAINT_CATEGORIES = {
        'street_light': {
            'name': 'ไฟถนนดับ',
            'urgency': 'medium',
            'department': 'ไฟฟ้าสาธารณะ'
        },
        'flooding': {
            'name': 'น้ำท่วม',
            'urgency': 'high',
            'department': 'ระบายน้ำ'
        },
        'garbage': {
            'name': 'ขยะไม่ได้เก็บ',
            'urgency': 'medium',
            'department': 'รักษาความสะอาด'
        },
        'noise': {
            'name': 'เสียงดังรบกวน',
            'urgency': 'low',
            'department': 'เทศกิจ'
        },
        'sidewalk': {
            'name': 'ทางเท้าเสียหาย',
            'urgency': 'medium',
            'department': 'โยธา'
        },
        'stray_dogs': {
            'name': 'สัตว์รบกวน',
            'urgency': 'medium',
            'department': 'สาธารณสุข'
        },
        'safety': {
            'name': 'ความปลอดภัย',
            'urgency': 'high',
            'department': 'เทศกิจ'
        }
    }

    WELFARE_CATEGORIES = {
        'elderly': {
            'name': 'ลงทะเบียนผู้สูงอายุ',
            'department': 'สวัสดิการสังคม'
        },
        'disabled': {
            'name': 'ลงทะเบียนคนพิการ',
            'department': 'สวัสดิการสังคม'
        },
        'financial_aid': {
            'name': 'ขอรับเงินสงเคราะห์',
            'department': 'สวัสดิการสังคม'
        },
        'low_income': {
            'name': 'สวัสดิการผู้มีรายได้น้อย',
            'department': 'สวัสดิการสังคม'
        },
        'emergency': {
            'name': 'ช่วยเหลือฉุกเฉิน',
            'department': 'สวัสดิการสังคม'
        }
    }

    # ระดับความเร่งด่วน
    URGENCY_LEVELS = {
        'high': {
            'name': 'เร่งด่วนมาก',
            'response_time': '24 ชั่วโมง'
        },
        'medium': {
            'name': 'เร่งด่วนปานกลาง',
            'response_time': '3 วัน'
        },
        'low': {
            'name': 'ไม่เร่งด่วน',
            'response_time': '7 วัน'
        }
    }

class DevelopmentConfig(Config):
    """
    การตั้งค่าสำหรับการพัฒนา
    """
    DEBUG = True

class ProductionConfig(Config):
    """
    การตั้งค่าสำหรับการใช้งานจริง
    """
    DEBUG = False
    FLASK_ENV = 'production'

# เลือกการตั้งค่าตามสภาพแวดล้อม
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """
    ดึงการตั้งค่าตามสภาพแวดล้อม
    """
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
