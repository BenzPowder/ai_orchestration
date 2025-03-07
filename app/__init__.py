from flask import Flask
from config import Config
from extensions import init_extensions, db
from api import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ตั้งค่า extensions
    init_extensions(app)
    
    # ลงทะเบียน blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    return app
