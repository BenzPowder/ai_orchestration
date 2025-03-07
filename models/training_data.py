from extensions import db
from datetime import datetime

class TrainingData(db.Model):
    __tablename__ = 'training_data'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('ai_agents.id'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TrainingData {self.id} for Agent {self.agent_id}>'
