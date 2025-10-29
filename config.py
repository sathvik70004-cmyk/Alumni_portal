# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Use environment variable on Render, fallback locally
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_hard_to_guess_secret_key_local'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true' # Read debug state from env
    TESTING = False
    
    # Database URL: Prioritize Render's env var, fallback to local SQLite
    DB_URL = os.environ.get('DATABASE_URL')
    if DB_URL:
        # Ensure correct scheme for SQLAlchemy with psycopg2 driver
        DB_URL = DB_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    else:
        # Local SQLite fallback
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'site.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth Keys (Read from environment variables on Render, fallbacks are for local testing ONLY)
    # MAKE SURE TO SET THESE AS ENV VARS ON RENDER
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or 'YOUR_LOCAL_GOOGLE_CLIENT_ID_HERE'
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or 'YOUR_LOCAL_GOOGLE_CLIENT_SECRET_HERE'