import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-this-premium-b2b-key'
    
    # Handle Supabase/Heroku 'postgres://' vs SQLAlchemy 'postgresql://' compatibility
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Analytics settings
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')

    # Database stability for serverless
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "poolclass": NullPool,
    }
