from flask import request, jsonify
from . import api
from models import AIAgent, TrainingData
from extensions import db
from ai import SubAgent
from datetime import datetime

@api.route('/agents', methods=['POST'])
def create_agent():
    """สร้าง AI Sub-agent ใหม่"""
    data = request.json
    
    # สร้าง agent ในฐานข้อมูล
    agent = AIAgent(
        name=data['name'],
        description=data.get('description', ''),
        type='sub_agent',
        project_id=data['project_id'],
        prompt_template=data.get('prompt_template', '')
    )
    
    db.session.add(agent)
    db.session.commit()
    
    return jsonify({
        'id': agent.id,
        'name': agent.name,
        'type': agent.type,
        'message': 'สร้าง AI Agent สำเร็จ'
    })

@api.route('/agents/<int:agent_id>/training-data', methods=['POST'])
def add_training_data(agent_id):
    """เพิ่มข้อมูลสำหรับการเทรน agent"""
    agent = AIAgent.query.get_or_404(agent_id)
    data = request.json
    
    # สร้าง training data
    training = TrainingData(
        agent_id=agent.id,
        input_text=data['input'],
        expected_output=data['output'],
        description=data.get('description', '')
    )
    
    db.session.add(training)
    db.session.commit()
    
    return jsonify({
        'id': training.id,
        'message': 'เพิ่มข้อมูลสำหรับการเทรนสำเร็จ'
    })

@api.route('/agents/<int:agent_id>/prompt', methods=['PUT'])
def update_agent_prompt(agent_id):
    """อัพเดท prompt template ของ agent"""
    agent = AIAgent.query.get_or_404(agent_id)
    data = request.json
    
    agent.prompt_template = data['prompt_template']
    db.session.commit()
    
    return jsonify({
        'message': 'อัพเดท prompt template สำเร็จ'
    })

@api.route('/agents/<int:agent_id>/training-data', methods=['GET'])
def get_training_data(agent_id):
    """ดูข้อมูลการเทรนทั้งหมดของ agent"""
    training_data = TrainingData.query.filter_by(agent_id=agent_id)\
        .order_by(TrainingData.created_at.desc())\
        .all()
        
    return jsonify([{
        'id': data.id,
        'input': data.input_text,
        'output': data.expected_output,
        'description': data.description,
        'created_at': data.created_at.isoformat()
    } for data in training_data])
