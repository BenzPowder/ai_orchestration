from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import redis

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
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=f"mysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}",
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
        
        # สร้างฐานข้อมูลถ้ายังไม่มี
        db.create_all()
    
    return app

# สร้าง application instance
app = create_app()
