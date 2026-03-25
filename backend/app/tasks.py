"""
Celery tasks for async workflow execution
"""
from app.celery_app import celery_app
from datetime import datetime
from pytz import timezone as pytz_timezone
from celery.exceptions import SoftTimeLimitExceeded
import logging

logger = logging.getLogger(__name__)
IST = pytz_timezone('Asia/Kolkata')

def calculate_next_run(schedule, now):
    from datetime import timedelta

    if not schedule:
        return None

    schedule = schedule.lower()

    if schedule == "every_minute":
        return now + timedelta(minutes=1)

    elif schedule == "every_hour":
        return now + timedelta(hours=1)

    elif schedule == "daily":
        return now + timedelta(days=1)

    elif schedule.startswith("every_"):
        return now + timedelta(days=7)

    return None

@celery_app.task(
    bind=True,
    name='app.tasks.execute_workflow_task',
    autoretry_for=(),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True,
    soft_time_limit=120,   # ⚠ warn task after 2 minutes
    time_limit=150         # 🔥 kill task after 2.5 minutes
)

def execute_workflow_task(self, task_id):
    """
    Celery task to execute a workflow
    """

    from app import create_app, db
    from app.models import Task, ExecutionLog
    from app.workflows import execute_workflow
    from datetime import datetime, timedelta

    app = create_app()

    with app.app_context():

        log = None
        task = None

        try:
            task = db.session.get(Task, task_id)

            if not task:
                logger.error(f"Task {task_id} not found")
                return {'success': False, 'error': 'Task not found'}

            now = datetime.now(IST)

            # 🔥 FIX timezone safety
            if now.tzinfo is None:
                now = IST.localize(now)

            # 🔥 HARD DUPLICATE PROTECTION (FINAL)
            if task.last_run:
                last_run = task.last_run

                # 🔥 FIX timezone mismatch
                if last_run.tzinfo is None:
                    last_run = IST.localize(last_run)

                delta = now - last_run
                if delta.total_seconds() < 50:
                    logger.warning(f"Skipping duplicate execution for task {task.id}")
                    
                    # 🔥 IMPORTANT: release lock if stuck
                    task.status = "ACTIVE"
                    db.session.commit()

                    return {"skipped": True}

            # 🔥 Create execution log ONLY for real runs
            log = ExecutionLog(
                task_id=task.id,
                start_time=now,
                status='RUNNING',
                message='Task execution started (Celery worker)'
            )

            db.session.add(log)
            db.session.commit()

            logger.info(f"[Celery Worker] Executing task {task.id}: {task.raw_text}")

            # Execute workflow
            workflow_type = task.parsed_type
            workflow_config = task.config or {}

            if not workflow_type or workflow_type == 'MANUAL':
                logger.warning(f"No valid workflow type for task {task.id}")
                
                success = False
                success_message = "No valid workflow → skipped execution"
                details = {}

            else:
                success, success_message, details = execute_workflow(
                    workflow_type,
                    workflow_config
                )

            # Update execution log
            log.end_time = datetime.now(IST)
            log.status = 'SUCCESS' if success else 'FAILED'
            log.message = success_message

            # 🔥 Update task state
            task.last_run = now
            if task.last_run and task.last_run.tzinfo is None:
                task.last_run = IST.localize(task.last_run)

            task.total_executions = (task.total_executions or 0) + 1

            # 🔥 RELEASE LOCK (CRITICAL FIX)
            task.status = "ACTIVE"

            db.session.commit()

            logger.info(f"[Celery Worker] Task {task.id} completed: {success_message}")

            return {
                'success': success,
                'message': success_message,
                'details': details,
                'task_id': task_id
            }

        except SoftTimeLimitExceeded:

            logger.error(f"[Celery Worker] Task {task_id} exceeded time limit")

            try:
                if log:
                    log.end_time = datetime.now(IST)
                    log.status = 'FAILED'
                    log.message = "Task exceeded execution time limit"
                    log.error_details = "Soft time limit exceeded"

                if task:
                    task.last_run = datetime.now(IST)
                    task.total_executions = (task.total_executions or 0) + 1
                    task.status = "ACTIVE"   # 🔥 release lock

                db.session.commit()

            except Exception as inner_error:
                logger.error(f"Error updating timeout log: {inner_error}")

            raise

        except Exception as e:

            logger.error(
                f"[Celery Worker] Error executing task {task_id}: {str(e)}"
            )

            try:
                if log:
                    log.end_time = datetime.now(IST)
                    log.status = 'FAILED'
                    log.message = f'Execution failed: {str(e)}'
                    log.error_details = str(e)

                if task:
                    task.last_run = datetime.now(IST)
                    task.total_executions = (task.total_executions or 0) + 1
                    task.status = "ACTIVE"   # 🔥 release lock

                db.session.commit()

            except Exception as inner_error:
                logger.error(f"Error updating failure log: {inner_error}")

            raise

        finally:
            from app import db
            db.session.remove()

    from datetime import datetime
    from pytz import timezone

    IST = timezone("Asia/Kolkata")
    now = datetime.now(IST)

    task.last_run = now
    task.total_executions = (task.total_executions or 0) + 1

    # SINGLE SOURCE OF TRUTH
    task.next_run = calculate_next_run(task.schedule, now)
        


@celery_app.task(name='app.tasks.cleanup_old_logs')
def cleanup_old_logs():
    """
    Periodic task to cleanup old execution logs (older than 30 days)
    """

    from app import create_app, db
    from app.models import ExecutionLog
    from datetime import timedelta

    app = create_app()

    with app.app_context():

        try:

            cutoff_date = datetime.now(IST) - timedelta(days=30)

            deleted = ExecutionLog.query.filter(
                ExecutionLog.start_time < cutoff_date
            ).delete()

            db.session.commit()

            logger.info(f"Cleaned up {deleted} old execution logs")

            return {'deleted': deleted}

        except Exception as e:

            logger.error(f"Error cleaning up logs: {str(e)}")

            return {'error': str(e)}
        

@celery_app.task(name="app.tasks.check_scheduled_tasks")
def check_scheduled_tasks():

    from app import create_app, db
    from app.models import Task
    from datetime import datetime, timedelta
    from pytz import timezone

    app = create_app()

    IST = timezone("Asia/Kolkata")

    with app.app_context():   # 🔥 THIS IS THE FIX

        now = datetime.now(IST)

        if now.tzinfo is None:
            now = IST.localize(now)
            
        tasks = Task.query.filter(
            Task.status == "ACTIVE",
            Task.next_run != None,
            Task.next_run <= now
        ).with_for_update().limit(5).all()

        for task in tasks:

            
            # 🔥 LOCK IMMEDIATELY
            task.status = "RUNNING"
            db.session.commit()

           # DO NOT calculate next_run here
            execute_workflow_task.delay(task.id)

        # 🔥 cleanup DB session
        db.session.remove()


