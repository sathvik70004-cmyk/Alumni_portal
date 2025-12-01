import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_hard_to_guess_secret_key_local'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Database URI Logic
    DB_URL = os.environ.get('DATABASE_URL')
    if DB_URL:
        # Ensure correct driver and scheme
        DB_URL = DB_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        
        # Force SSL
        if '?sslmode=' not in SQLALCHEMY_DATABASE_URI:
             SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI + '?sslmode=require'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'site.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- Keep-Alive Options ---
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,        # Pings DB before query to revive connection
        "pool_recycle": 300,          # Recycle connections every 5 minutes
        "pool_timeout": 30,           # Wait 30s for a connection
        "pool_size": 10,
        "max_overflow": 5,
    }
    # ----------------------------------------

    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')