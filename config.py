# config.py (Final Established Version)

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # This is a placeholder secret key; change it for production!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A_VERY_LONG_PRODUCTION_SECRET_KEY'
    DEBUG = True # Keep True for local dev, Render will override if needed
    TESTING = False

    # CRITICAL FIX: The SQLAlchemy URL must use the driver prefix for Render PostgreSQL.
    DB_URL = os.environ.get('DATABASE_URL')
    if DB_URL:
        # Ensure the scheme is 'postgresql' before adding the driver prefix
        DB_URL = DB_URL.replace('postgres://', 'postgresql://', 1)

        # Add the +psycopg2 prefix required by SQLAlchemy for the driver
        SQLALCHEMY_DATABASE_URI = DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    else:
        # Fallback for local development (SQLite)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'site.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Google OAuth Keys (Replace placeholders if running locally, use ENV VARS on Render) ---
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or 'YOUR_GOOGLE_CLIENT_ID_HERE'
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or 'YOUR_GOOGLE_CLIENT_SECRET_HERE'
    # --------------------------------------------------------------------------------------