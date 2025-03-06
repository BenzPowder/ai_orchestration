from flask import Flask, redirect, url_for
from app.config import get_config
from app.blueprints.admin import admin_bp
from app.blueprints.api import api_bp
import os

def create_app():
    """
    สร้างและกำหนดค่า Flask Application
    """
    app = Flask(__name__)
    
    # โหลดการตั้งค่า
    config = get_config()
    app.config.from_object(config)
    
    # กำหนด SECRET_KEY จาก environment variable
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # ลงทะเบียน Blueprint
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    # สร้าง index route
    @app.route('/')
    def index():
        return redirect(url_for('admin.agent_list'))
    
    return app

# สร้าง application instance สำหรับ gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )
