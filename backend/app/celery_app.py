
# backend/app/celery_app.py
"""
Celery application configuration
"""
from celery import Celery
from celery.schedules import crontab
import os

# Redis connection
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'uaos',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['app.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Beat schedule (for periodic tasks)
celery_app.conf.beat_schedule = {
    "check-scheduled-tasks-every-30-seconds": {
        "task": "app.tasks.check_scheduled_tasks",
        "schedule": 60.0,
    }
}

broker_url = os.environ.get("REDIS_URL")
result_backend = os.environ.get("REDIS_URL")