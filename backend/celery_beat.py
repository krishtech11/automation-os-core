"""
Celery beat scheduler entry point
Run with: celery -A celery_beat beat --loglevel=info
"""
from app.celery_app import celery_app
from app import create_app

# Initialize Flask app context
flask_app = create_app()
flask_app.app_context().push()

if __name__ == '__main__':
    celery_app.start()