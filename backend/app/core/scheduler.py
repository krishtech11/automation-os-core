from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from pytz import timezone as pytz_timezone
from app import db
from app.models import Task, ExecutionLog
import logging

logger = logging.getLogger(__name__)

# India timezone
IST = pytz_timezone('Asia/Kolkata')

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone='Asia/Kolkata',
            job_defaults={
                'coalesce': True,        # Combine missed executions into one
                'max_instances': 1,      # Only one instance of each job at a time
                'misfire_grace_time': 30 # Skip if missed by more than 30 seconds
            }
        )
        self._running_tasks = set()  # Track currently executing task IDs
        self.scheduler.start()
        logger.info("APScheduler started successfully with Asia/Kolkata timezone")
    
    def parse_schedule(self, schedule_text):
        """
        Parse natural language schedule into APScheduler trigger
        Returns: (trigger, next_run_description)
        """
        logger.info(f"DEBUG: Received schedule_text = '{schedule_text}'")
        schedule_lower = schedule_text.lower().strip()

        # Handle advanced schedule formats from parser v2
        # Format: daily_18_0 (daily at 18:00), every_monday_9_30 (Monday at 9:30)
        parts = schedule_lower.split('_')
        
        # Daily with specific time: daily_HH_MM
        if len(parts) == 3 and parts[0] == 'daily':
            try:
                hour = int(parts[1])
                minute = int(parts[2])
                return CronTrigger(hour=hour, minute=minute, timezone=IST), f"Daily at {hour}:{minute:02d}"
            except:
                pass
        
        # Weekly with specific time: every_monday_HH_MM (or tuesday, etc)
        if len(parts) == 4 and parts[0] == 'every':
            day_map = {
                'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed',
                'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun'
            }
            day = parts[1]
            if day in day_map:
                try:
                    hour = int(parts[2])
                    minute = int(parts[3])
                    return CronTrigger(day_of_week=day_map[day], hour=hour, minute=minute, timezone=IST), \
                        f"Every {day.title()} at {hour}:{minute:02d}"
                except:
                    pass
        
        # Weekly with simple format: every_monday (no time specified)
        if len(parts) == 2 and parts[0] == 'every':
            day_map = {
                'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed',
                'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun'
            }
            day = parts[1]
            if day in day_map:
                return CronTrigger(day_of_week=day_map[day], hour=9, minute=0, timezone=IST), \
                    f"Every {day.title()} at 9:00 AM"
        
        # Every N hours: every_3_hours
        if len(parts) >= 3 and parts[0] == 'every' and parts[2] == 'hours':
            try:
                hours = int(parts[1])
                return IntervalTrigger(hours=hours, timezone=IST), f"Every {hours} hours"
            except:
                pass
        
        # Every N minutes: every_5_minutes
        if len(parts) >= 3 and parts[0] == 'every' and parts[2] == 'minutes':
            try:
                minutes = int(parts[1])
                return IntervalTrigger(minutes=minutes, timezone=IST), f"Every {minutes} minutes"
            except:
                pass

        # Original simple patterns (fallback)
        if 'daily' in schedule_lower or 'har din' in schedule_lower or 'roz' in schedule_lower:
            hour = 9
            if 'shaam' in schedule_lower or 'evening' in schedule_lower:
                hour = 18
            elif 'subah' in schedule_lower or 'morning' in schedule_lower:
                hour = 7
            elif 'raat' in schedule_lower or 'night' in schedule_lower:
                hour = 22
            trigger = CronTrigger(hour=hour, minute=0, timezone=IST)
            return trigger, f"Daily at {hour}:00"

        elif 'monday' in schedule_lower or 'somwar' in schedule_lower:
            return CronTrigger(day_of_week='mon', hour=9, minute=0, timezone=IST), "Every Monday at 9 AM"

        elif 'tuesday' in schedule_lower or 'mangalwar' in schedule_lower:
            return CronTrigger(day_of_week='tue', hour=9, minute=0, timezone=IST), "Every Tuesday at 9 AM"

        elif 'wednesday' in schedule_lower or 'budhwar' in schedule_lower:
            return CronTrigger(day_of_week='wed', hour=9, minute=0, timezone=IST), "Every Wednesday at 9 AM"

        elif 'thursday' in schedule_lower or 'guruwar' in schedule_lower:
            return CronTrigger(day_of_week='thu', hour=9, minute=0, timezone=IST), "Every Thursday at 9 AM"

        elif 'friday' in schedule_lower or 'shukrawar' in schedule_lower:
            return CronTrigger(day_of_week='fri', hour=9, minute=0, timezone=IST), "Every Friday at 9 AM"

        elif 'saturday' in schedule_lower or 'shaniwar' in schedule_lower:
            return CronTrigger(day_of_week='sat', hour=9, minute=0, timezone=IST), "Every Saturday at 9 AM"

        elif 'sunday' in schedule_lower or 'raviwar' in schedule_lower:
            return CronTrigger(day_of_week='sun', hour=9, minute=0, timezone=IST), "Every Sunday at 9 AM"

        elif 'hour' in schedule_lower or 'ghante' in schedule_lower:
            return IntervalTrigger(hours=1, timezone=IST), "Every hour"

        elif 'minute' in schedule_lower or 'min' in schedule_lower:
            return IntervalTrigger(minutes=1, timezone=IST), "Every minute (testing)"

        else:
            return None, "Manual execution only"
    
    def schedule_task(self, task):
        """
        Schedule a task with APScheduler
        """
        try:
            trigger, description = self.parse_schedule(task.schedule)
            
            if trigger is None:
                logger.info(f"Task {task.id} is manual only, not scheduling")
                return False
            
            job_id = f"task_{task.id}"
            
            # Always remove existing job first to prevent duplicates
            existing_job = self.scheduler.get_job(job_id)
            if existing_job:
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed existing job for task {task.id} before rescheduling")
            
            # Add job with strict single-instance enforcement
            self.scheduler.add_job(
                func=self.execute_task,
                trigger=trigger,
                args=[task.id],
                id=job_id,
                name=f"Task {task.id}: {task.raw_text[:50]}",
                replace_existing=True,
                max_instances=1,   # Enforce here too, per job
                coalesce=True,     # Enforce here too, per job
                misfire_grace_time=30  # If job misfires by >30s, skip it
            )
            
            logger.info(f"Scheduled task {task.id}: {description}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling task {task.id}: {str(e)}")
            return False
    
    def execute_task(self, task_id):
        """
        Execute a scheduled task and log the execution.
        Uses a running-set lock to guarantee only one execution at a time.
        """
        # --- Software lock: bail out if already running ---
        if task_id in self._running_tasks:
            logger.warning(f"Task {task_id} is already running — skipping duplicate trigger")
            return
        self._running_tasks.add(task_id)

        from app import create_app
        app = create_app()
        log = None

        try:
            with app.app_context():
                try:
                    task = Task.query.get(task_id)
                    if not task:
                        logger.error(f"Task {task_id} not found")
                        return
                    
                    # Create execution log
                    log = ExecutionLog(
                        task_id=task.id,
                        start_time=datetime.now(IST),
                        status='RUNNING',
                        message='Task execution started'
                    )
                    db.session.add(log)
                    db.session.commit()
                    
                    logger.info(f"Executing task {task.id}: {task.raw_text}")
                    
                    # REAL WORKFLOW EXECUTION (WEEK 3)
                    from app.workflows import execute_workflow
                    
                    workflow_type = task.parsed_type or 'MANUAL'
                    workflow_config = task.config or {}
                    
                    if workflow_type == 'MANUAL':
                        # For manual tasks, just log
                        success = True
                        success_message = f"✓ Manual task executed: {task.raw_text}"
                        details = {}
                    else:
                        # Execute actual workflow
                        success, success_message, details = execute_workflow(
                            workflow_type, 
                            workflow_config
                        )
                    
                    # Update log as successful
                    log.end_time = datetime.now(IST)
                    log.status = 'SUCCESS'
                    log.message = success_message
                    
                    # Update task counters
                    task.last_run = datetime.now(IST)
                    task.total_executions = (task.total_executions or 0) + 1
                    
                    db.session.commit()
                    
                    logger.info(f"Task {task.id} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Error executing task {task_id}: {str(e)}")
                    
                    # Update log as failed
                    if log:
                        log.end_time = datetime.now(IST)
                        log.status = 'FAILED'
                        log.message = 'Execution failed'
                        log.error_details = str(e)
                        
                        # Still update task counters even on failure
                        task.last_run = datetime.now(IST)
                        task.total_executions = (task.total_executions or 0) + 1
                        
                        db.session.commit()

        finally:
            # Always release the lock
            self._running_tasks.discard(task_id)
    
    def remove_task(self, task_id):
        """
        Remove a task from scheduler
        """
        job_id = f"task_{task_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed task {task_id} from scheduler")
            return True
        return False
    
    def get_scheduled_jobs(self):
        """
        Get all scheduled jobs info
        """
        jobs = self.scheduler.get_jobs()
        return [{
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None
        } for job in jobs]
    
    def shutdown(self):
        """
        Shutdown the scheduler
        """
        self.scheduler.shutdown()
        logger.info("Scheduler shut down")


# Global scheduler instance
task_scheduler = None

def init_scheduler(app):
    """
    Initialize the scheduler and load all active tasks
    """
    global task_scheduler
    task_scheduler = TaskScheduler()
    
    with app.app_context():
        active_tasks = Task.query.filter_by(status='ACTIVE').all()
        for task in active_tasks:
            task_scheduler.schedule_task(task)
        
        logger.info(f"Loaded {len(active_tasks)} active tasks into scheduler")
    
    return task_scheduler

def get_scheduler():
    """
    Get the global scheduler instance
    """
    return task_scheduler
