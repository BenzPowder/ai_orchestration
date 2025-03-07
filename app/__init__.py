from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import redis
from urllib.parse import quote_plus
from flask_redis import FlaskRedis

# โหลดค่าจากไฟล์ .env
load_dotenv()

# สร้าง extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
login_manager = LoginManager()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URL", "redis://localhost:6379/1")
)
redis_client = FlaskRedis()

def create_app():
    """สร้างและกำหนดค่า Flask application"""
    app = Flask(__name__)
    
    # ตั้งค่า Database URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # ถ้าไม่มี DATABASE_URL ให้สร้างจากค่าแยก
        db_user = quote_plus(os.environ.get('DB_USER', ''))
        db_password = quote_plus(os.environ.get('DB_PASSWORD', ''))
        db_host = os.environ.get('DB_HOST', '')
        db_name = os.environ.get('DB_NAME', '')
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
    elif not database_url.startswith('mysql+pymysql://'):
        # เพิ่ม driver prefix ถ้ายังไม่มี
        database_url = database_url.replace('mysql://', 'mysql+pymysql://')
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY'),
        RATELIMIT_STORAGE_URL=os.environ.get("RATELIMIT_STORAGE_URL", "redis://localhost:6379/1"),
        REDIS_URL=os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    )
    
    # กำหนดค่า extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    redis_client.init_app(app)
    
    # ตั้งค่า Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'กรุณาเข้าสู่ระบบก่อนเข้าใช้งาน'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    with app.app_context():
        # นำเข้า CLI commands
        from app.cli import create_admin
        app.cli.add_command(create_admin)
        
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
