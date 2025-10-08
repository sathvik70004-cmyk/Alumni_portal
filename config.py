# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A_VERY_LONG_PRODUCTION_SECRET_KEY'
    DEBUG = True
    TESTING = False
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- GOOGLE OAUTH KEYS REMOVED ---