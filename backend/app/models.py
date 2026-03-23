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
    parsed_type = db.Column(db.String(50))
    schedule = db.Column(db.String(100))
    status = db.Column(db.String(20), default='ACTIVE')
    config = db.Column(db.JSON)
    
    # NEW FIELDS FOR WEEK 2
    next_run = db.Column(db.DateTime)
    last_run = db.Column(db.DateTime)
    total_executions = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    logs = db.relationship('ExecutionLog', backref='task', lazy=True, 
                          cascade='all, delete-orphan', order_by='ExecutionLog.start_time.desc()')

class Workflow(db.Model):
    __tablename__ = 'workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    workflow_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    config_schema = db.Column(db.JSON)
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

# ... existing models ...

class WorkflowPlan(db.Model):
    """
    Stores LLM-generated workflow plans
    """
    __tablename__ = 'workflow_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(
    db.Integer,
    db.ForeignKey('tasks.id', ondelete='CASCADE'),
    nullable=False
    )
    
    # LLM analysis
    analysis = db.Column(db.Text)
    confidence = db.Column(db.Float)
    
    # Plan structure (JSON)
    plan_json = db.Column(db.JSON, nullable=False)
    
    # Metadata
    llm_provider = db.Column(db.String(50))  # 'openai' or 'anthropic'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    task = db.relationship(
    'Task',
    backref=db.backref('workflow_plan', cascade='all, delete-orphan', uselist=False)
    )