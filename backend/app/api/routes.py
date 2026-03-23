from flask import jsonify, request
from app.api import api_bp
from app import db
from app.models import Task, User, ExecutionLog
from app.core.celery_scheduler import get_celery_scheduler
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    scheduler = get_celery_scheduler()
    jobs = scheduler.get_scheduled_jobs() if scheduler else []

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'UAOS API',
        'scheduler': {
            'running': True if scheduler else False,
            'jobs_count': len(jobs)
        }
    })


@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()

    return jsonify({
        'tasks': [{
            'id': task.id,
            'raw_text': task.raw_text,
            'parsed_type': task.parsed_type,
            'schedule': task.schedule,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'next_run': task.next_run.isoformat() if task.next_run else None,
            'last_run': task.last_run.isoformat() if task.last_run else None,
            'total_executions': task.total_executions,
            'log_count': len(task.logs)
        } for task in tasks]
    })


@api_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    if not data or 'raw_text' not in data:
        return jsonify({'error': 'raw_text is required'}), 400

    # demo user
    user = User.query.filter_by(email="demo@uaos.com").first()
    if not user:
        user = User(email='demo@uaos.com', name='Demo User')
        db.session.add(user)
        db.session.commit()

    raw_text = data['raw_text']
    use_llm = data.get('use_llm', True)

    workflow_type = None
    config = {}
    schedule = "manual"
    confidence = 0.0
    plan = None

    # -------------------------
    # TRY LLM PLANNER
    # -------------------------

    if use_llm:
        try:
            from app.core.llm_planner_free import get_free_llm_planner

            planner = get_free_llm_planner()

            if planner and planner.check_ollama_available():

                logger.info("Using FREE Ollama LLM planner")

                plan, confidence = planner.plan_workflow(raw_text)

                workflow_type, config, schedule = planner.simplify_plan_for_single_task(plan)
                schedule = schedule or ""

        except Exception as e:
            logger.warning(f"LLM planner failed: {str(e)}")

    # -------------------------
    # FALLBACK PARSER
    # -------------------------

    if not workflow_type:

        from app.core.intent_parser import parse_task_intent_v2, extract_schedule

        workflow_type, config, explanation, confidence = parse_task_intent_v2(raw_text)

        schedule = extract_schedule(raw_text) or ""

        print("PARSED:", workflow_type, confidence, explanation)

        ALLOWED_WORKFLOWS = [
            "NEWS_DIGEST",
            "FILE_CLEANUP",
            "INVOICE_SYNC",
            "DOCUMENT_SUMMARY",
            "EMAIL_REPORT"
        ]

        if workflow_type not in ALLOWED_WORKFLOWS or confidence < 0.65:
            return jsonify({
                "error": "Could not understand the task clearly. Try being more specific."
            }), 400

    # -------------------------
    # CREATE TASK
    # -------------------------

    task = Task(
        user_id=user.id,
        raw_text=raw_text,
        parsed_type=workflow_type,
        schedule=schedule,
        config=config,
        status='ACTIVE'
    )

    db.session.add(task)
    db.session.flush()

    # -------------------------
    # CALCULATE NEXT RUN
    # -------------------------

    from datetime import timedelta
    from pytz import timezone

    IST = timezone("Asia/Kolkata")
    now = datetime.now(IST)

    next_run = None
    if not isinstance(schedule, str):
        schedule = ""

    # EVERY MINUTE
    if schedule and "every minute" in schedule:

        next_run = now + timedelta(minutes=1)

    # EVERY HOUR
    elif schedule and "every hour" in schedule:

        next_run = now + timedelta(hours=1)

    # DAILY
    elif schedule and "daily" in schedule:

        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)

        if next_run <= now:
            next_run += timedelta(days=1)


    # WEEKLY
    elif schedule and ("every_" in schedule or "every " in schedule):
    
        # normalize format
        normalized = schedule.replace("every ", "every_").lower()
        
        day_name = normalized.replace("every_", "")

        days_map = {
            "monday":0,
            "tuesday":1,
            "wednesday":2,
            "thursday":3,
            "friday":4,
            "saturday":5,
            "sunday":6
        }

        if day_name in days_map:

            target_day = days_map[day_name]

            days_ahead = target_day - now.weekday()

            if days_ahead <= 0:
                days_ahead += 7

            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=9, minute=0, second=0, microsecond=0)


    # MANUAL → no schedule
    if next_run:
        task.next_run = next_run

    # -------------------------
    # SAVE LLM PLAN IF EXISTS
    # -------------------------

    if plan:

        from app.models import WorkflowPlan

        workflow_plan = WorkflowPlan(
            task_id=task.id,
            analysis=plan['analysis'],
            confidence=confidence,
            plan_json=plan,
            llm_provider='ollama'
        )

        db.session.add(workflow_plan)

    db.session.commit()

    # -------------------------
    # REGISTER SCHEDULER
    # -------------------------

    return jsonify({
        'message': 'Task created successfully',
        'task': {
            'id': task.id,
            'raw_text': task.raw_text,
            'parsed_type': task.parsed_type,
            'schedule': task.schedule,
            'config': task.config,
            'next_run': task.next_run.isoformat() if task.next_run else None,
            'confidence': confidence
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
        'message': log.message,
        'error_details': log.error_details,
        'duration': (log.end_time - log.start_time).total_seconds()
        if log.end_time and log.start_time else None
    } for log in task.logs]

    return jsonify({
        'id': task.id,
        'raw_text': task.raw_text,
        'parsed_type': task.parsed_type,
        'schedule': task.schedule,
        'status': task.status,
        'created_at': task.created_at.isoformat(),
        'next_run': task.next_run.isoformat() if task.next_run else None,
        'last_run': task.last_run.isoformat() if task.last_run else None,
        'total_executions': task.total_executions,
        'logs': logs
    })


@api_bp.route('/tasks/<int:task_id>', methods=['PATCH'])
def update_task_status(task_id):

    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400

    old_status = task.status
    task.status = data['status']
    db.session.commit()

    from app.core.celery_scheduler import get_celery_scheduler

    celery_sched = get_celery_scheduler()

    if celery_sched:
        if task.status == 'ACTIVE' and old_status != 'ACTIVE':
            celery_sched.register_task(task)

        elif task.status in ['PAUSED', 'FAILED']:
            celery_sched.remove_task(task.id)

    return jsonify({
        'message': 'Task updated successfully',
        'task': {
            'id': task.id,
            'status': task.status
        }
    })


@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    celery_sched = get_celery_scheduler()
    if celery_sched:
        celery_sched.remove_task(task.id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'})


@api_bp.route('/tasks/<int:task_id>/execute', methods=['POST'])
def execute_task_now(task_id):
    task = Task.query.get_or_404(task_id)

    from app.tasks import execute_workflow_task
    execute_workflow_task.delay(task.id)

    return jsonify({
        'message': 'Task execution triggered',
        'task_id': task.id
    })


@api_bp.route('/scheduler/jobs', methods=['GET'])
def get_scheduled_jobs():
    scheduler = get_celery_scheduler()
    if not scheduler:
        return jsonify({'error': 'Scheduler not available'}), 500

    jobs = scheduler.get_scheduled_jobs()
    return jsonify({
        'jobs': jobs,
        'total': len(jobs)
    })


@api_bp.route('/logs', methods=['GET'])
def get_recent_logs():

    logs = ExecutionLog.query.order_by(
        ExecutionLog.start_time.desc()
    ).limit(50).all()

    return jsonify({
        'logs': [{
            'id': log.id,
            'task_id': log.task_id,

            # 🔧 FIX 4 — safe task text access
            'task_text': (
                log.task.raw_text[:50] + '...'
                if log.task and len(log.task.raw_text) > 50
                else (log.task.raw_text if log.task else "Deleted Task")
            ),

            'start_time': log.start_time.isoformat(),
            'end_time': log.end_time.isoformat() if log.end_time else None,
            'status': log.status,
            'message': log.message,
            'duration': (log.end_time - log.start_time).total_seconds()
            if log.end_time and log.start_time else None
        } for log in logs]
    })


@api_bp.route('/stats', methods=['GET'])
def get_stats():

    total_tasks = Task.query.count()
    active_tasks = Task.query.filter_by(status='ACTIVE').count()
    paused_tasks = Task.query.filter_by(status='PAUSED').count()
    failed_tasks = Task.query.filter_by(status='FAILED').count()

    total_executions = db.session.query(
        db.func.sum(Task.total_executions)
    ).scalar() or 0

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    today_executions = ExecutionLog.query.filter(
        ExecutionLog.start_time >= today_start
    ).count()

    successful_today = ExecutionLog.query.filter(
        ExecutionLog.start_time >= today_start,
        ExecutionLog.status == 'SUCCESS'
    ).count()

    failed_today = ExecutionLog.query.filter(
        ExecutionLog.start_time >= today_start,
        ExecutionLog.status == 'FAILED'
    ).count()

    return jsonify({
        'tasks': {
            'total': total_tasks,
            'active': active_tasks,
            'paused': paused_tasks,
            'failed': failed_tasks
        },
        'executions': {
            'total': int(total_executions),
            'today': today_executions,
            'successful_today': successful_today,
            'failed_today': failed_today
        }
    })

@api_bp.route('/assistant', methods=['POST'])
def ai_assistant():

    data = request.get_json()
    message = data.get("message", "")

    from app.core.intent_parser import parse_task_intent_v2
    from app.core.intent_parser import extract_schedule
    from app.models import Task, User
    from app import db

    # Parse user command
    workflow_type, config, explanation, confidence = parse_task_intent_v2(message)

    # If AI detects automation command
    if confidence > 0.6 and workflow_type != "UNKNOWN":

        user = User.query.first()

        schedule = extract_schedule(message)

        task = Task(
            raw_text=message,
            parsed_type=workflow_type,
            config=config,
            schedule=schedule,
            status="ACTIVE",
            user_id=user.id
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({
            "reply": f"Automation created successfully (Task #{task.id})"
        })

    # Otherwise fallback to normal AI chat
    return jsonify({
    "reply": "I can only help create automation tasks. Please give a clear automation command."
    })