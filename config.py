# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_hard_to_guess_secret_key_local'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # CRITICAL FIX: The SQLAlchemy URL must use the driver prefix for Render PostgreSQL.
    DB_URL = os.environ.get('DATABASE_URL')
    if DB_URL:
        # Ensure the scheme is 'postgresql' (not 'postgres')
        DB_URL = DB_URL.replace('postgres://', 'postgresql://', 1)
        
        # Add the +psycopg2 driver prefix
        SQLALCHEMY_DATABASE_URI = DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        
        # Explicitly require SSL, which stabilizes connections
        if '?sslmode=' not in SQLALCHEMY_DATABASE_URI:
             SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI + '?sslmode=require'
    else:
        # Fallback for local development (SQLite)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'site.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Google OAuth Keys (Read from environment variables on Render) ---
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # --- Gemini API Key (Read from environment variables on Render) ---
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')