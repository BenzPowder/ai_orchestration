from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import uuid
from urllib.parse import urljoin
import os
import json
from pyngrok import ngrok
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# ตั้งค่า ngrok
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
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default if default is not None else [], f, ensure_ascii=False, indent=2)
            return default if default is not None else []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการโหลดข้อมูลจาก {file_path}: {str(e)}")
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
    # สร้างโฟลเดอร์เก็บข้อมูลถ้ายังไม่มี
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # โหลดข้อมูล agents
    global agents
    agents = load_data(AGENTS_FILE, [])
    
    # โหลดข้อมูล webhooks
    global webhooks
    webhooks = load_data(WEBHOOKS_FILE, [])
    
    # โหลดข้อมูล training data
    global training_data
    training_data = load_data(TRAINING_DATA_FILE, [])

# เรียกใช้ฟังก์ชันเตรียมข้อมูลเมื่อเริ่มต้นแอพ
init_data()

def load_agents():
    """โหลดข้อมูล agents จากไฟล์"""
    return agents

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
        agents_data = load_agents()
        return render_template('agents.html', agents=agents_data)
    except Exception as e:
        flash(f'เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}', 'error')
        return redirect(url_for('index'))

# สร้าง Agent ใหม่
@app.route('/agents/new', methods=['GET', 'POST'])
def new_agent():
    """สร้าง AI Agent ใหม่"""
    if request.method == 'POST':
        try:
            agents_data = load_agents()
            new_id = len(agents_data) + 1
            agent = {
                'id': new_id,
                'name': request.form['name'],
                'description': request.form['description'],
                'type': request.form['type']
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
def webhook_endpoint(path):
    """รับข้อมูลจาก webhook"""
    try:
        # หา webhook จาก path
        webhook = next((w for w in webhooks if w['url_path'] == f"webhook/{path}"), None)
        if not webhook:
            return jsonify({'error': 'Webhook ไม่ถูกต้อง'}), 404
        
        if not webhook['is_active']:
            return jsonify({'error': 'Webhook ถูกปิดใช้งาน'}), 403
        
        # บันทึก webhook log
        log = {
            'id': str(uuid.uuid4()),
            'webhook_id': webhook['id'],
            'request_data': request.json,
            'created_at': datetime.now().isoformat()
        }
        
        # โหลดและบันทึก logs
        logs = load_data(os.path.join(DATA_DIR, f"webhook_logs_{webhook['id']}.json"), [])
        logs.append(log)
        save_data(os.path.join(DATA_DIR, f"webhook_logs_{webhook['id']}.json"), logs)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/logs/<webhook_id>')
def webhook_logs(webhook_id):
    """ดูประวัติการทำงานของ webhook"""
    try:
        logs = load_data(os.path.join(DATA_DIR, f"webhook_logs_{webhook_id}.json"), [])
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
