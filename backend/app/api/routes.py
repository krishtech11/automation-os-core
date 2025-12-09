from flask import jsonify, request
from app.api import api_bp
from app import db
from app.models import Task, User, ExecutionLog
from datetime import datetime

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'UAOS API'
    })

@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    # For now, get all tasks (later add user filtering)
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    
    return jsonify({
        'tasks': [{
            'id': task.id,
            'raw_text': task.raw_text,
            'parsed_type': task.parsed_type,
            'schedule': task.schedule,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'log_count': len(task.logs)
        } for task in tasks]
    })

@api_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'raw_text' not in data:
        return jsonify({'error': 'raw_text is required'}), 400
    
    # For Week 1, create a default user if not exists
    user = User.query.first()
    if not user:
        user = User(email='demo@uaos.com', name='Demo User')
        db.session.add(user)
        db.session.commit()
    
    task = Task(
        user_id=user.id,
        raw_text=data['raw_text'],
        parsed_type=data.get('parsed_type', 'MANUAL'),
        schedule=data.get('schedule', 'manual'),
        config=data.get('config', {})
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'message': 'Task created successfully',
        'task': {
            'id': task.id,
            'raw_text': task.raw_text,
            'status': task.status
        }
    }), 201

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    logs = [{
        'id': log.id,
        'start_time': log.start_time.isoformat(),
        'end_time': log.end_time.isoformat() if log.end_time else None,
        'status': log.status,
        'message': log.message
    } for log in task.logs]
    
    return jsonify({
        'id': task.id,
        'raw_text': task.raw_text,
        'parsed_type': task.parsed_type,
        'schedule': task.schedule,
        'status': task.status,
        'created_at': task.created_at.isoformat(),
        'logs': logs
    })

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'})