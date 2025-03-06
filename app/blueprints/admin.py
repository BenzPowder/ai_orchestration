from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.models.agent import Agent
from app.models.training_data import TrainingData
from app.config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# สร้าง instance ของโมเดล
agent_model = Agent(Config.MONGODB_URI, Config.MONGODB_DB_NAME)
training_data_model = TrainingData(Config.MONGODB_URI, Config.MONGODB_DB_NAME)

@admin_bp.route('/agents')
def agent_list():
    """หน้าแสดงรายการ Sub-Agent"""
    agents = agent_model.get_all_agents()
    return render_template('admin/agent_list.html', agents=agents)

@admin_bp.route('/agents/create', methods=['GET', 'POST'])
def create_agent():
    """หน้าสร้าง Sub-Agent ใหม่"""
    if request.method == 'POST':
        try:
            # รับข้อมูลจากฟอร์ม
            name = request.form['name']
            agent_type = request.form['type']
            description = request.form.get('description', '')
            endpoint = request.form['endpoint']
            active = request.form.get('active', '1') == '1'
            
            # สร้าง prompt templates
            templates = []
            template_names = request.form.getlist('template_names[]')
            template_contents = request.form.getlist('template_contents[]')
            for name, content in zip(template_names, template_contents):
                if name and content:
                    templates.append({
                        'name': name,
                        'content': content
                    })
            
            # สร้าง Sub-Agent
            agent_model.create_agent(
                name=name,
                agent_type=agent_type,
                description=description,
                endpoint=endpoint,
                prompt_templates=templates,
                active=active
            )
            
            flash('สร้าง Sub-Agent สำเร็จ', 'success')
            return redirect(url_for('admin.agent_list'))
            
        except Exception as e:
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
            
    return render_template('admin/agent_form.html')

@admin_bp.route('/agents/<agent_id>/edit', methods=['GET', 'POST'])
def edit_agent(agent_id):
    """หน้าแก้ไข Sub-Agent"""
    agent = agent_model.get_agent(agent_id)
    if not agent:
        flash('ไม่พบ Sub-Agent', 'error')
        return redirect(url_for('admin.agent_list'))
        
    if request.method == 'POST':
        try:
            # รับข้อมูลจากฟอร์ม
            update_data = {
                'name': request.form['name'],
                'type': request.form['type'],
                'description': request.form.get('description', ''),
                'endpoint': request.form['endpoint'],
                'active': request.form.get('active', '1') == '1'
            }
            
            # อัปเดต prompt templates
            templates = []
            template_names = request.form.getlist('template_names[]')
            template_contents = request.form.getlist('template_contents[]')
            for name, content in zip(template_names, template_contents):
                if name and content:
                    templates.append({
                        'name': name,
                        'content': content
                    })
            update_data['prompt_templates'] = templates
            
            # อัปเดต Sub-Agent
            if agent_model.update_agent(agent_id, update_data):
                flash('อัปเดต Sub-Agent สำเร็จ', 'success')
                return redirect(url_for('admin.agent_list'))
            else:
                flash('ไม่สามารถอัปเดต Sub-Agent ได้', 'error')
                
        except Exception as e:
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
            
    return render_template('admin/agent_form.html', agent=agent)

@admin_bp.route('/agents/<agent_id>/delete', methods=['POST'])
def delete_agent(agent_id):
    """ลบ Sub-Agent"""
    try:
        if agent_model.delete_agent(agent_id):
            flash('ลบ Sub-Agent สำเร็จ', 'success')
        else:
            flash('ไม่สามารถลบ Sub-Agent ได้', 'error')
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
        
    return redirect(url_for('admin.agent_list'))

@admin_bp.route('/training-data')
def training_data():
    """หน้าแสดงรายการ Training Data"""
    agents = agent_model.get_all_agents()
    
    # ดึงข้อมูลทั้งหมดของแต่ละ Agent
    all_data = []
    for agent in agents:
        data_list = training_data_model.get_agent_data(agent['_id'])
        for data in data_list:
            data['agent_name'] = agent['name']
            data['type_display'] = {
                'text': 'ข้อความ',
                'qa': 'คำถาม-คำตอบ',
                'conversation': 'บทสนทนา'
            }.get(data['type'], data['type'])
            all_data.append(data)
            
    # เรียงตามวันที่สร้างล่าสุด
    all_data.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template(
        'admin/training_data.html',
        agents=agents,
        training_data=all_data
    )

@admin_bp.route('/training-data/upload', methods=['POST'])
def upload_training_data():
    """อัปโหลด Training Data"""
    try:
        agent_id = request.form['agent_id']
        data_type = request.form['type']
        
        if 'file' not in request.files:
            flash('ไม่พบไฟล์', 'error')
            return redirect(url_for('admin.training_data'))
            
        file = request.files['file']
        if file.filename == '':
            flash('ไม่ได้เลือกไฟล์', 'error')
            return redirect(url_for('admin.training_data'))
            
        if file:
            # ตรวจสอบนามสกุลไฟล์
            filename = secure_filename(file.filename)
            file_type = filename.rsplit('.', 1)[1].lower()
            if file_type not in ['txt', 'csv', 'json']:
                flash('นามสกุลไฟล์ไม่ถูกต้อง', 'error')
                return redirect(url_for('admin.training_data'))
                
            # อ่านเนื้อหาไฟล์
            file_content = file.read().decode('utf-8')
            
            # นำเข้าข้อมูล
            imported_ids = training_data_model.import_from_file(
                agent_id=agent_id,
                file_content=file_content,
                file_type=file_type,
                data_type=data_type
            )
            
            flash(f'นำเข้าข้อมูลสำเร็จ {len(imported_ids)} รายการ', 'success')
            
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
        
    return redirect(url_for('admin.training_data'))

@admin_bp.route('/training-data/<data_id>/delete', methods=['POST'])
def delete_training_data(data_id):
    """ลบ Training Data"""
    try:
        if training_data_model.delete_data(data_id):
            flash('ลบข้อมูลสำเร็จ', 'success')
        else:
            flash('ไม่สามารถลบข้อมูลได้', 'error')
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
        
    return redirect(url_for('admin.training_data'))

@admin_bp.route('/training-data/export', methods=['POST'])
def export_training_data():
    """ส่งออก Training Data"""
    try:
        agent_id = request.form.get('agent_id')
        data_type = request.form.get('type')
        
        # ส่งออกเป็น JSON
        json_data = training_data_model.export_to_json(
            agent_id=agent_id,
            data_type=data_type
        )
        
        # สร้างชื่อไฟล์
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'training_data_{timestamp}.json'
        
        # ส่งไฟล์กลับ
        return jsonify({
            'filename': filename,
            'data': json_data
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
