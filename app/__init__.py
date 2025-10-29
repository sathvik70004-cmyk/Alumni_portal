# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from config import Config
from flask_login import LoginManager 
from authlib.integrations.flask_client import OAuth # CRITICAL: For Google Login

# --- 1. Initialize extensions BEFORE the app object ---
db = SQLAlchemy() 
login = LoginManager() 
login.login_view = 'login' 

app = Flask(__name__)

# 2. Load configuration settings
app.config.from_object(Config)

# 3. Initialize extensions WITH the app
db.init_app(app) 
login.init_app(app) 

# --- CORRECTED Authlib/OAuth Initialization ---
oauth = OAuth(app)
oauth.register(
    'google',
    client_id=app.config.get('GOOGLE_CLIENT_ID'),
    client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
    # CRITICAL FIX: This URL tells Authlib where to find all required security endpoints (including jwks_uri)
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
# -----------------------------------------------

# --- User Loader (Required by Flask-Login) ---
@login.user_loader
def load_user(id):
    """Callback function used by Flask-Login to retrieve a User object."""
    from app.models import User
    return db.session.get(User, int(id))
# ---------------------------------------------

# 4. Import models and routes LAST
from app import models
from app import routes