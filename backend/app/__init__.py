from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
import logging

db = SQLAlchemy()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    with app.app_context():
        db.create_all()
        
        # Initialize scheduler
        from app.core.scheduler import init_scheduler
        init_scheduler(app)

        # Initialize FREE LLM planner
        from app.core.llm_planner_free import init_free_llm_planner
        init_free_llm_planner()

    import traceback

    @app.errorhandler(Exception)
    def handle_exception(e):
        traceback.print_exc()

        return {
            "status": "error",
            "message": "Something went wrong"
        }, 500
    
    return app

