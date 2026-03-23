"""
Celery-based task scheduler (replaces APScheduler for production)
"""
from celery import current_app
from celery.schedules import crontab
from datetime import datetime
from pytz import timezone as pytz_timezone
import logging

logger = logging.getLogger(__name__)
IST = pytz_timezone('Asia/Kolkata')


class CeleryScheduler:
    """
    Manages scheduled tasks using Celery Beat
    """

    def __init__(self):
        self.app = current_app

        # 🔧 FIX 1 — ensure beat_schedule exists
        if not hasattr(self.app.conf, "beat_schedule") or self.app.conf.beat_schedule is None:
            self.app.conf.beat_schedule = {}

        # 🔧 FIX 2 — enforce timezone for scheduling
        self.app.conf.timezone = 'Asia/Kolkata'
        self.app.conf.enable_utc = False

        logger.info("Celery scheduler initialized")

    def parse_schedule_to_crontab(self, schedule_text):
        """
        Convert schedule text to Celery crontab
        Returns: (crontab_obj, description)
        """

        schedule_lower = schedule_text.lower().strip()
        parts = schedule_lower.split('_')

        # Daily with specific time: daily_18_0
        if len(parts) == 3 and parts[0] == 'daily':
            try:
                hour = int(parts[1])
                minute = int(parts[2])
                return crontab(hour=hour, minute=minute), f"Daily at {hour}:{minute:02d}"
            except:
                pass

        # Weekly with specific time: every_friday_18_0
        if len(parts) == 4 and parts[0] == 'every':
            day_map = {
                'monday': 1, 'tuesday': 2, 'wednesday': 3,
                'thursday': 4, 'friday': 5, 'saturday': 6, 'sunday': 0
            }

            day = parts[1]

            if day in day_map:
                try:
                    hour = int(parts[2])
                    minute = int(parts[3])

                    return crontab(
                        day_of_week=day_map[day],
                        hour=hour,
                        minute=minute
                    ), f"Every {day.title()} at {hour}:{minute:02d}"

                except:
                    pass

        # Simple weekly: every_friday
        if len(parts) == 2 and parts[0] == 'every':
            day_map = {
                'monday': 1, 'tuesday': 2, 'wednesday': 3,
                'thursday': 4, 'friday': 5, 'saturday': 6, 'sunday': 0
            }

            day = parts[1]

            if day in day_map:
                return crontab(day_of_week=day_map[day], hour=9, minute=0), \
                       f"Every {day.title()} at 9:00 AM"

        # Hourly
        if 'hour' in schedule_lower:
            return crontab(minute=0), "Every hour"

        # Every minute (testing)
        if 'minute' in schedule_lower:
            return crontab(), "Every minute"

        # Fallback patterns
        if 'daily' in schedule_lower:

            hour = 9

            if 'evening' in schedule_lower:
                hour = 18
            elif 'morning' in schedule_lower:
                hour = 7
            elif 'night' in schedule_lower:
                hour = 22

            return crontab(hour=hour, minute=0), f"Daily at {hour}:00"

        if 'friday' in schedule_lower:
            return crontab(day_of_week=5, hour=9, minute=0), "Every Friday at 9 AM"

        if 'monday' in schedule_lower:
            return crontab(day_of_week=1, hour=9, minute=0), "Every Monday at 9 AM"

        return None, "Manual execution only"

    def register_task(self, task):
        """
        Register a task with Celery Beat
        """

        try:

            schedule_obj, description = self.parse_schedule_to_crontab(task.schedule)

            if schedule_obj is None:
                logger.info(f"Task {task.id} is manual only")
                return False

            schedule_name = f"task_{task.id}"

            self.app.conf.beat_schedule[schedule_name] = {
                'task': 'app.tasks.execute_workflow_task',
                'schedule': schedule_obj,
                'args': (task.id,),
            }

            logger.info(f"Registered Celery Beat task {task.id}: {description}")

            # ---- Calculate next run time ----
            from datetime import timedelta
            from app import db

            now = datetime.now(IST)

            next_run = None

            schedule = task.schedule.lower()

            # DAILY
            if schedule.startswith("daily"):

                parts = schedule.split("_")

                hour = 9
                minute = 0

                if len(parts) == 3:
                    hour = int(parts[1])
                    minute = int(parts[2])

                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                if next_run <= now:
                    next_run += timedelta(days=1)

            # WEEKLY
            elif schedule.startswith("every_"):

                parts = schedule.split("_")

                day_map = {
                    "monday":0,
                    "tuesday":1,
                    "wednesday":2,
                    "thursday":3,
                    "friday":4,
                    "saturday":5,
                    "sunday":6
                }

                day = parts[1]

                if day in day_map:

                    target_day = day_map[day]

                    days_ahead = target_day - now.weekday()

                    if days_ahead <= 0:
                        days_ahead += 7

                    next_run = now + timedelta(days=days_ahead)

                    hour = 9
                    minute = 0

                    if len(parts) == 4:
                        hour = int(parts[2])
                        minute = int(parts[3])

                    next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Save if calculated
            if next_run:
                task.next_run = next_run
                db.session.commit()

                logger.info(f"Next run estimated for task {task.id}: {task.next_run}")

            return True

        except Exception as e:

            logger.error(f"Error registering task {task.id}: {str(e)}")

            return False
        
    # 🔧 FIX 3 — rename function to match routes.py usage
    def remove_task(self, task_id):
        """
        Remove task from Celery Beat schedule
        """

        schedule_name = f"task_{task_id}"

        if schedule_name in self.app.conf.beat_schedule:

            del self.app.conf.beat_schedule[schedule_name]

            logger.info(f"Unregistered task {task_id}")

            return True

        return False


# Singleton
celery_scheduler = None


def init_celery_scheduler():
    """
    Initialize Celery scheduler
    """

    global celery_scheduler

    celery_scheduler = CeleryScheduler()

    return celery_scheduler


def get_celery_scheduler():
    """
    Get Celery scheduler instance
    """

    return celery_scheduler