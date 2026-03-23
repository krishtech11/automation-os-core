# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY not set")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://uaos:uaos123@localhost/uaos_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 3,
    "max_overflow": 2,
    "pool_timeout": 30,
    "pool_recycle": 1800,
    }