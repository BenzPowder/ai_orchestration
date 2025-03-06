from flask import Flask
from dotenv import load_dotenv
import os

# โหลดค่าจากไฟล์ .env
load_dotenv()

def create_app():
    """สร้างและกำหนดค่า Flask application"""
    app = Flask(__name__)
    
    # ตั้งค่า configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        MONGODB_URI=os.environ.get('MONGODB_URI'),
        MONGODB_DB_NAME=os.environ.get('MONGODB_DB_NAME', 'ai_orchestration'),
        LINE_CHANNEL_SECRET=os.environ.get('LINE_CHANNEL_SECRET'),
        LINE_CHANNEL_ACCESS_TOKEN=os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'),
        OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY'),
    )
    
    # ลงทะเบียน blueprints
    from app.routes import line_webhook
    app.register_blueprint(line_webhook.bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
