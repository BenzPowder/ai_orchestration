from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import redis
from urllib.parse import quote_plus

# โหลดค่าจากไฟล์ .env
load_dotenv()

# สร้าง extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URL", "redis://localhost:6379/1")
)

def create_app():
    """สร้างและกำหนดค่า Flask application"""
    app = Flask(__name__)
    
    # ตั้งค่า configuration
    db_user = quote_plus(os.environ.get('DB_USER', ''))
    db_password = quote_plus(os.environ.get('DB_PASSWORD', ''))
    db_host = os.environ.get('DB_HOST', '')
    db_name = os.environ.get('DB_NAME', '')
    
    # สร้าง Database URL ที่สมบูรณ์ โดยใช้ pymysql driver และ URL encoding
    db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY'),
    )
    
    # กำหนดค่า extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    
    with app.app_context():
        # ลงทะเบียน blueprints
        from app.blueprints import admin, api
        app.register_blueprint(admin.admin_bp)
        app.register_blueprint(api.api_bp, url_prefix='/api')
        
        try:
            # สร้างฐานข้อมูลถ้ายังไม่มี
            db.create_all()
        except Exception as e:
            app.logger.error(f"Database initialization error: {str(e)}")
            # ไม่ raise error เพื่อให้แอพยังทำงานต่อได้
            pass
    
    return app

# สร้าง application instance
app = create_app()
