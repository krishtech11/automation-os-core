from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    raw_text = db.Column(db.Text, nullable=False)
    parsed_type = db.Column(db.String(50))  # NEWS_DIGEST, FILE_CLEANUP, etc.
    schedule = db.Column(db.String(100))  # "daily", "every monday", etc.
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, PAUSED, FAILED
    config = db.Column(db.JSON)  # Additional workflow config
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    logs = db.relationship('ExecutionLog', backref='task', lazy=True, cascade='all, delete-orphan')

class Workflow(db.Model):
    __tablename__ = 'workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    workflow_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    config_schema = db.Column(db.JSON)  # Expected config structure
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExecutionLog(db.Model):
    __tablename__ = 'execution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20))  # RUNNING, SUCCESS, FAILED
    message = db.Column(db.Text)
    error_details = db.Column(db.Text)