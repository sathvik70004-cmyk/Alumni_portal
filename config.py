# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # This is a placeholder secret key; change it for production!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A_VERY_LONG_PRODUCTION_SECRET_KEY'
    DEBUG = True  # Keep debug True for development
    TESTING = False
    
    # SQLite Configuration: Connects to a file named site.db in the root directory
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or 'YOUR_GOOGLE_CLIENT_ID_HERE'
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or 'YOUR_GOOGLE_CLIENT_SECRET_HERE'
