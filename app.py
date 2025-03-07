from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import uuid
from urllib.parse import urljoin
import os
import json
from pyngrok import ngrok
import secrets
from extensions import db, init_extensions
from flask_login import LoginManager, UserMixin, login_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# เริ่มต้น extensions
init_extensions(app)

# สร้างฐานข้อมูลถ้ายังไม่มี
with app.app_context():
    db.create_all()

# ตั้งค่า Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@login_manager.request_loader
def load_user_from_request(request):
    # ตรวจสอบ API key ใน header
    api_key = request.headers.get('Authorization')
    if api_key:
        # ตรวจสอบความถูกต้องของ API key
        if api_key == os.getenv('API_KEY', 'your-api-key-here'):
            return User("api_user")
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ตรวจสอบ API key จาก form
        api_key = request.form.get('api_key')
        if api_key == os.getenv('API_KEY', 'your-api-key-here'):
            user = User("web_user")
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('API Key ไม่ถูกต้อง', 'danger')
    return render_template('login.html')

# เริ่มต้น ngrok
def setup_ngrok():
    """ตั้งค่า ngrok สำหรับทดสอบ webhook"""
    try:
        # เปิด tunnel ไปที่ port 5000
        public_url = ngrok.connect(5000).public_url
        print(f"\n🌐 HTTPS URL สำหรับ Line Webhook: {public_url}\n")
        return public_url
    except Exception as e:
        print(f"⚠️ ไม่สามารถเชื่อมต่อ ngrok ได้: {str(e)}")
        return None

# เริ่มต้น ngrok เมื่อรันในโหมด debug
if app.debug:
    ngrok_url = setup_ngrok()
    if ngrok_url:
        print("✨ คำแนะนำการตั้งค่า Line Webhook:")
        print("1. ไปที่ Line Developer Console")
        print("2. เลือก Channel ที่ต้องการ")
        print("3. ไปที่ Messaging API > Webhook settings")
        print(f"4. วาง URL นี้: {ngrok_url}/webhook/<your-path>")
        print("5. กด Verify และ Update")

# นำเข้าโมเดลหลังจากสร้าง app
from models.webhook import Webhook, WebhookLog
from models.agent import Agent
from models.training_data import TrainingData

# ตั้งค่าพาธสำหรับไฟล์ข้อมูล
DATA_DIR = 'data'
AGENTS_FILE = os.path.join(DATA_DIR, 'agents.json')
WEBHOOKS_FILE = os.path.join(DATA_DIR, 'webhooks.json')
TRAINING_DATA_FILE = os.path.join(DATA_DIR, 'training_data.json')

# ฟังก์ชันสำหรับโหลดข้อมูล
def load_data(file_path, default=None):
    """โหลดข้อมูลจากไฟล์ JSON"""
    try:
        if not os.path.exists(file_path):
            # สร้างไฟล์ใหม่ถ้ายังไม่มี
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            data = default if default is not None else []
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # ตรวจสอบว่าข้อมูลเป็น list หรือไม่
            if not isinstance(data, list):
                print(f"Warning: Data from {file_path} is not a list, initializing empty list")
                return []
            return data
    except json.JSONDecodeError as e:
        print(f"JSON decode error in {file_path}: {str(e)}")
        return default if default is not None else []
    except Exception as e:
        print(f"Error loading data from {file_path}: {str(e)}")
        return default if default is not None else []

def save_data(file_path, data):
    """บันทึกข้อมูลลงไฟล์ JSON"""
    try:
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการบันทึกข้อมูลไปที่ {file_path}: {str(e)}")
        return False

# โหลดข้อมูลเมื่อเริ่มต้นแอพ
def init_data():
    """เตรียมข้อมูลเริ่มต้น"""
    try:
        # สร้างโฟลเดอร์เก็บข้อมูลถ้ายังไม่มี
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            print(f"Created data directory: {DATA_DIR}")
        
        # โหลดข้อมูล agents
        global agents
        try:
            print("Loading agents data...")
            agents = load_data(AGENTS_FILE, [])
            if not isinstance(agents, list):
                print("Warning: agents data is not a list, initializing empty list")
                agents = []
            else:
                print(f"Successfully loaded {len(agents)} agents")
                # แสดงรายละเอียดของแต่ละ agent
                for agent in agents:
                    print(f"- {agent.get('name', 'Unnamed')} ({agent.get('type', 'No type')})")
        except Exception as e:
            print(f"Error loading agents: {str(e)}")
            agents = []
        
        # โหลดข้อมูล webhooks
        global webhooks
        try:
            print("\nLoading webhooks data...")
            webhooks = load_data(WEBHOOKS_FILE, [])
            print(f"Successfully loaded {len(webhooks)} webhooks")
        except Exception as e:
            print(f"Error loading webhooks: {str(e)}")
            webhooks = []
        
        # โหลดข้อมูล training data
        global training_data
        try:
            print("\nLoading training data...")
            training_data = load_data(TRAINING_DATA_FILE, [])
            print(f"Successfully loaded {len(training_data)} training data items")
        except Exception as e:
            print(f"Error loading training data: {str(e)}")
            training_data = []

        print("\nInitialization complete!")
        print("=" * 50)

    except Exception as e:
        print(f"Critical error during initialization: {str(e)}")
        # ตั้งค่าเริ่มต้นเป็น list ว่างเพื่อป้องกันข้อผิดพลาด
        agents = []
        webhooks = []
        training_data = []

# เรียกใช้ฟังก์ชันเตรียมข้อมูลเมื่อเริ่มต้นแอพ
init_data()

class Agent:
    """คลาสสำหรับจัดการข้อมูล AI Agent"""
    def __init__(self):
        self._id = None
        self._name = None
        self._description = None
        self._type = None
        self._type_display = None
        self._training_data = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def type_display(self):
        return self._type_display

    @type_display.setter
    def type_display(self, value):
        self._type_display = value

    @property
    def training_data(self):
        return self._training_data

    @training_data.setter
    def training_data(self, value):
        self._training_data = value

def load_agents():
    """โหลดข้อมูล agents จากไฟล์และแปลงเป็น Agent objects"""
    try:
        agents_data = load_data(AGENTS_FILE, [])
        agent_objects = []
        
        if not isinstance(agents_data, list):
            print("Warning: agents_data is not a list")
            return []
            
        for agent_data in agents_data:
            if not isinstance(agent_data, dict):
                continue
                
            agent = Agent()
            agent.id = agent_data.get('id')
            agent.name = agent_data.get('name')
            agent.description = agent_data.get('description')
            agent.type = agent_data.get('type')
            agent.type_display = agent_data.get('type_display', agent.type)
            
            if 'training_data' in agent_data and isinstance(agent_data['training_data'], list):
                agent.training_data = agent_data['training_data']
            else:
                agent.training_data = []
                
            agent_objects.append(agent)
            
        return agent_objects
    except Exception as e:
        print(f"Error loading agents: {str(e)}")
        return []

def save_agents(agents_data):
    """บันทึกข้อมูล agents ลงไฟล์"""
    global agents
    agents = agents_data
    return save_data(AGENTS_FILE, agents)

def load_webhooks():
    """โหลดข้อมูล webhooks"""
    return webhooks

def save_webhooks(webhooks_data):
    """บันทึกข้อมูล webhooks"""
    global webhooks
    webhooks = webhooks_data
    return save_data(WEBHOOKS_FILE, webhooks)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # บันทึก error ลง log
    app.logger.error(f"Unhandled exception: {str(e)}")
    return render_template('500.html'), 500

# หน้าแรก
@app.route('/')
def index():
    """แสดงหน้าแรกของระบบ"""
    return render_template('index.html')

# แสดงรายการ Agents ทั้งหมด
@app.route('/agents')
def agents():
    """แสดงรายการ AI Agents ทั้งหมด"""
    try:
        agent_list = load_agents()
        
        # จัดกลุ่ม agents ตามประเภท
        agents_by_type = {}
        for agent in agent_list:
            agent_type = agent.type or 'ไม่ระบุประเภท'
            if agent_type not in agents_by_type:
                agents_by_type[agent_type] = []
            agents_by_type[agent_type].append(agent)
            
        # นับจำนวน agents ทั้งหมด
        total_agents = len(agent_list)
            
        return render_template('agents.html', agents_by_type=agents_by_type, total_agents=total_agents)
    except Exception as e:
        print(f"Error in agents route: {str(e)}")
        flash('เกิดข้อผิดพลาดในการโหลดข้อมูล Agents', 'error')
        return redirect(url_for('index'))

@app.route('/agents/<id>')
def view_agent(id):
    """แสดงรายละเอียดของ Agent"""
    try:
        agent_list = load_agents()
        agent = next((a for a in agent_list if a.id == id), None)
        
        if not agent:
            flash('ไม่พบข้อมูล Agent ที่ต้องการ', 'error')
            return redirect(url_for('agents'))
            
        return render_template('agent_detail.html', agent=agent)
    except Exception as e:
        print(f"Error in view_agent route: {str(e)}")
        flash('เกิดข้อผิดพลาดในการโหลดข้อมูล Agent', 'error')
        return redirect(url_for('agents'))

# สร้าง Agent ใหม่
@app.route('/agents/new', methods=['GET', 'POST'])
def new_agent():
    """สร้าง AI Agent ใหม่"""
    if request.method == 'POST':
        try:
            agents_data = load_agents()
            if not isinstance(agents_data, list):
                agents_data = []
            new_id = len(agents_data) + 1
            agent = {
                'id': new_id,
                'name': request.form['name'],
                'description': request.form['description'],
                'type': request.form['type'],
                'training_data': []
            }
            agents_data.append(agent)
            save_agents(agents_data)
            flash('สร้าง Agent สำเร็จ', 'success')
            return redirect(url_for('agents'))
        except Exception as e:
            flash(f'เกิดข้อผิดพลาดในการสร้าง Agent: {str(e)}', 'error')
            return redirect(url_for('agents'))
    
    return render_template('agent_form.html')

# แก้ไข Agent
@app.route('/agents/<int:id>/edit', methods=['GET', 'POST'])
def edit_agent(id):
    """แก้ไขข้อมูล AI Agent"""
    try:
        agents_data = load_agents()
        agent = next((a for a in agents_data if a['id'] == id), None)
        
        if agent is None:
            flash('ไม่พบ Agent ที่ต้องการแก้ไข', 'error')
            return redirect(url_for('agents'))
        
        if request.method == 'POST':
            agent.update({
                'name': request.form['name'],
                'description': request.form['description'],
                'type': request.form['type']
            })
            save_agents(agents_data)
            flash('แก้ไข Agent สำเร็จ', 'success')
            return redirect(url_for('agents'))
        
        return render_template('agent_form.html', id=id, agent=agent)
    except Exception as e:
        flash(f'เกิดข้อผิดพลาดในการแก้ไข Agent: {str(e)}', 'error')
        return redirect(url_for('agents'))

# ลบ Agent
@app.route('/agents/<int:id>/delete', methods=['POST'])
def delete_agent(id):
    """ลบ AI Agent"""
    try:
        agents_data = load_agents()
        agents_data = [a for a in agents_data if a['id'] != id]
        save_agents(agents_data)
        flash('ลบ Agent สำเร็จ', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# เพิ่มฟังก์ชันสำหรับสร้าง URL Path
def generate_webhook_path():
    """สร้าง URL path สำหรับ webhook"""
    return f"webhook/{uuid.uuid4()}"

@app.route('/agents/<id>/webhooks/new', methods=['GET', 'POST'])
def new_webhook(id):
    """สร้าง webhook ใหม่"""
    try:
        if request.method == 'POST':
            # สร้าง webhook ใหม่
            webhook = {
                'id': str(uuid.uuid4()),
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'url_path': generate_webhook_path(),
                'agent_id': id,
                'is_active': True,
                'secret_key': secrets.token_urlsafe(32),
                'created_at': datetime.now().isoformat()
            }
            
            # เพิ่ม webhook ใหม่
            webhooks.append(webhook)
            save_webhooks(webhooks)
            
            flash('สร้าง Webhook สำเร็จ', 'success')
            return redirect(url_for('agents'))
            
        # สร้าง URL ตัวอย่าง
        sample_webhook_url = urljoin(request.host_url, generate_webhook_path())
        
        # ส่ง ngrok URL ไปแสดงผล (ถ้ามี)
        ngrok_url = None
        if app.debug:
            try:
                tunnels = ngrok.get_tunnels()
                if tunnels:
                    ngrok_url = tunnels[0].public_url
            except:
                pass
                
        return render_template(
            'webhook_form.html',
            agent_id=id,
            sample_webhook_url=sample_webhook_url,
            ngrok_url=ngrok_url
        )
        
    except Exception as e:
        flash(f'เกิดข้อผิดพลาดในการสร้าง webhook: {str(e)}', 'error')
        return redirect(url_for('agents'))

# เพิ่มข้อมูลเทรน
@app.route('/agents/<int:id>/training-data/add', methods=['GET', 'POST'])
def add_training_data(id):
    """เพิ่มข้อมูลเทรนสำหรับ Agent"""
    try:
        agents_data = load_agents()
        agent = next((a for a in agents_data if a['id'] == id), None)
        
        if agent is None:
            flash('ไม่พบ Agent ที่ต้องการเพิ่มข้อมูลเทรน', 'error')
            return redirect(url_for('agents'))
        
        if request.method == 'POST':
            training_data = {
                'id': len(agent.get('training_data', [])) + 1,
                'prompt': request.form['prompt'],
                'description': request.form.get('description', ''),
                'created_at': datetime.now().isoformat()
            }
            
            if 'training_data' not in agent:
                agent['training_data'] = []
            agent['training_data'].append(training_data)
            save_agents(agents_data)
            
            flash('เพิ่มข้อมูลเทรนสำเร็จ', 'success')
            return redirect(url_for('agents'))
        
        return render_template('training_data_form.html', agent=agent)
    except Exception as e:
        flash(f'เกิดข้อผิดพลาดในการเพิ่มข้อมูลเทรน: {str(e)}', 'error')
        return redirect(url_for('agents'))

@app.route('/webhook/<path>', methods=['POST'])
def webhook(path):
    """รับข้อมูลจาก webhook"""
    try:
        # ตรวจสอบ webhook จาก path
        webhooks_data = load_data(WEBHOOKS_FILE, [])
        webhook_data = next((w for w in webhooks_data if w['url_path'] == path), None)
        
        if not webhook_data:
            error_message = f"ไม่พบ webhook สำหรับ path: {path}"
            return jsonify({'error': error_message}), 404
            
        webhook = Webhook.from_dict(webhook_data)
        
        if not webhook.is_active:
            error_message = "Webhook นี้ถูกปิดการใช้งาน"
            webhook.add_log('error', error_message)
            return jsonify({'error': error_message}), 400
            
        # ตรวจสอบ secret key
        secret_key = request.headers.get('X-Webhook-Secret')
        if not secret_key or secret_key != webhook.secret_key:
            error_message = "Secret key ไม่ถูกต้อง"
            webhook.add_log('error', error_message)
            return jsonify({'error': error_message}), 401
            
        # รับข้อมูล
        data = request.get_json()
        if not data:
            error_message = "ไม่พบข้อมูลที่ส่งมา"
            webhook.add_log('error', error_message)
            return jsonify({'error': error_message}), 400
            
        # ส่งข้อมูลไปยัง agents ที่เชื่อมต่อ
        results = []
        for agent_id in webhook.agent_ids:
            agent = next((a for a in agents if a['id'] == agent_id), None)
            if agent:
                try:
                    # TODO: ส่งข้อมูลไปยัง agent
                    results.append({
                        'agent_id': agent_id,
                        'agent_name': agent['name'],
                        'status': 'success'
                    })
                except Exception as e:
                    results.append({
                        'agent_id': agent_id,
                        'agent_name': agent['name'],
                        'status': 'error',
                        'error': str(e)
                    })
        
        # บันทึกประวัติการทำงาน
        webhook.add_log(
            status='success',
            message='ได้รับข้อมูลและส่งต่อไปยัง agents เรียบร้อย',
            details={
                'request_data': data,
                'results': results
            }
        )
        
        return jsonify({
            'message': 'ดำเนินการสำเร็จ',
            'results': results
        }), 200
        
    except Exception as e:
        error_message = f"เกิดข้อผิดพลาด: {str(e)}"
        if 'webhook' in locals():
            webhook.add_log('error', error_message)
        return jsonify({'error': error_message}), 500

@app.route('/webhook/<webhook_id>/logs')
def webhook_logs(webhook_id):
    """แสดงประวัติการทำงานของ webhook"""
    try:
        # โหลดข้อมูล webhook
        webhooks_data = load_data(WEBHOOKS_FILE, [])
        webhook_data = next((w for w in webhooks_data if w['id'] == webhook_id), None)
        if not webhook_data:
            flash('ไม่พบ Webhook ที่ต้องการ', 'error')
            return redirect(url_for('list_webhooks'))
        
        webhook = Webhook.from_dict(webhook_data)
        
        # โหลดประวัติการทำงาน
        logs = webhook.get_logs()
        
        return render_template('webhook_logs.html', webhook=webhook, logs=logs)
    except Exception as e:
        print(f"Error in webhook_logs: {str(e)}")
        flash('เกิดข้อผิดพลาดในการโหลดประวัติการทำงาน', 'error')
        return redirect(url_for('list_webhooks'))

@app.route('/webhook/toggle/<webhook_id>')
def toggle_webhook(webhook_id):
    """เปิด/ปิดการใช้งาน webhook"""
    try:
        webhook = next((w for w in webhooks if w['id'] == webhook_id), None)
        if webhook:
            webhook['is_active'] = not webhook['is_active']
            save_webhooks(webhooks)
            return jsonify({'status': 'success', 'is_active': webhook['is_active']}), 200
        return jsonify({'error': 'ไม่พบ webhook'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhooks')
def list_webhooks():
    """แสดงรายการ Webhooks ทั้งหมด"""
    try:
        # โหลดข้อมูล webhooks จากไฟล์
        webhooks_data = load_data(WEBHOOKS_FILE, [])
        webhook_list = []
        
        # แปลงข้อมูลเป็น Webhook objects
        for data in webhooks_data:
            webhook = Webhook.from_dict(data)
            # หา agents ที่เชื่อมต่อกับ webhook นี้
            webhook_agents = []
            for agent in agents:
                if agent['id'] in webhook.agent_ids:
                    webhook_agents.append(agent)
            webhook_list.append({
                'webhook': webhook,
                'agents': webhook_agents
            })
        
        return render_template('webhooks.html', webhooks=webhook_list)
    except Exception as e:
        print(f"Error in webhooks route: {str(e)}")
        flash('เกิดข้อผิดพลาดในการโหลดข้อมูล Webhook', 'error')
        return redirect(url_for('index'))

@app.route('/webhook/create', methods=['GET', 'POST'])
def create_webhook():
    """สร้าง Webhook ใหม่"""
    if request.method == 'POST':
        try:
            # สร้าง Webhook ใหม่
            webhook = Webhook(
                name=request.form['name'],
                description=request.form.get('description'),
                url_path=request.form.get('url_path'),
                secret_key=request.form.get('secret_key'),
                is_active=bool(request.form.get('is_active'))
            )
            
            # เพิ่ม agents ที่เลือก
            agent_ids = request.form.getlist('agent_ids')
            for agent_id in agent_ids:
                webhook.add_agent(agent_id)
            
            # บันทึกลงไฟล์
            webhooks_data = load_data(WEBHOOKS_FILE, [])
            webhooks_data.append(webhook.to_dict())
            save_data(WEBHOOKS_FILE, webhooks_data)
            
            flash('สร้าง Webhook สำเร็จ', 'success')
            return redirect(url_for('list_webhooks'))
        except Exception as e:
            print(f"Error creating webhook: {str(e)}")
            flash('เกิดข้อผิดพลาดในการสร้าง Webhook', 'error')
    
    return render_template('webhook_form.html', agents=agents)

@app.route('/webhook/<webhook_id>/edit', methods=['GET', 'POST'])
def edit_webhook(webhook_id):
    """แก้ไข Webhook"""
    # โหลดข้อมูล webhook
    webhooks_data = load_data(WEBHOOKS_FILE, [])
    webhook_data = next((w for w in webhooks_data if w['id'] == webhook_id), None)
    if not webhook_data:
        flash('ไม่พบ Webhook ที่ต้องการแก้ไข', 'error')
        return redirect(url_for('list_webhooks'))
    
    webhook = Webhook.from_dict(webhook_data)
    
    if request.method == 'POST':
        try:
            # อัพเดตข้อมูล webhook
            webhook.name = request.form['name']
            webhook.description = request.form.get('description')
            webhook.url_path = request.form.get('url_path')
            webhook.secret_key = request.form.get('secret_key')
            webhook.is_active = bool(request.form.get('is_active'))
            
            # อัพเดต agents
            webhook.agent_ids = []
            agent_ids = request.form.getlist('agent_ids')
            for agent_id in agent_ids:
                webhook.add_agent(agent_id)
            
            # บันทึกการเปลี่ยนแปลง
            webhook_idx = next((i for i, w in enumerate(webhooks_data) if w['id'] == webhook_id), None)
            if webhook_idx is not None:
                webhooks_data[webhook_idx] = webhook.to_dict()
                save_data(WEBHOOKS_FILE, webhooks_data)
                flash('อัพเดต Webhook สำเร็จ', 'success')
            return redirect(url_for('list_webhooks'))
        except Exception as e:
            print(f"Error updating webhook: {str(e)}")
            flash('เกิดข้อผิดพลาดในการอัพเดต Webhook', 'error')
    
    return render_template('webhook_form.html', webhook=webhook, agents=agents)

@app.route('/webhook/<webhook_id>/delete', methods=['POST'])
def delete_webhook(webhook_id):
    """ลบ Webhook"""
    try:
        webhooks_data = load_data(WEBHOOKS_FILE, [])
        webhooks_data = [w for w in webhooks_data if w['id'] != webhook_id]
        save_data(WEBHOOKS_FILE, webhooks_data)
        flash('ลบ Webhook สำเร็จ', 'success')
    except Exception as e:
        print(f"Error deleting webhook: {str(e)}")
        flash('เกิดข้อผิดพลาดในการลบ Webhook', 'error')
    return redirect(url_for('list_webhooks'))

@app.route('/training_data')
def training_data_list():
    """แสดงรายการข้อมูลเทรนทั้งหมด"""
    try:
        data_list = []
        agents_data = load_agents()
        
        if not isinstance(agents_data, list):
            agents_data = []
            
        for agent in agents_data:
            if isinstance(agent, dict) and 'training_data' in agent:
                for data in agent['training_data']:
                    data_list.append({
                        'id': data.get('id'),
                        'prompt': data.get('prompt'),
                        'agent_name': agent.get('name'),
                        'description': data.get('description', ''),
                        'created_at': data.get('created_at')
                    })
                    
        # จัดเรียงตามวันที่สร้าง (ล่าสุดขึ้นก่อน)
        data_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        if not data_list:
            flash('ยังไม่มีข้อมูลเทรนในระบบ', 'info')
            
        return render_template('training_data.html', training_data=data_list)
    except Exception as e:
        print(f"Error in training_data route: {str(e)}")
        flash('เกิดข้อผิดพลาดในการโหลดข้อมูลเทรน', 'error')
        return redirect(url_for('index'))

@app.template_filter('datetime')
def format_datetime(value):
    """แปลงวันที่เป็นรูปแบบที่อ่านง่าย"""
    if not value:
        return ''
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return value

@app.context_processor
def utility_processor():
    """เพิ่มฟังก์ชันที่ใช้งานในเทมเพลต"""
    def format_date(date_str):
        """แปลงวันที่เป็นรูปแบบที่อ่านง่าย"""
        if not date_str:
            return ''
        try:
            date = datetime.fromisoformat(date_str)
            return date.strftime('%d/%m/%Y %H:%M')
        except:
            return date_str
    
    return dict(
        now=datetime.now(),
        format_date=format_date
    )

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
