# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from config import Config
from flask_login import LoginManager 
from authlib.integrations.flask_client import OAuth # NEW Import

# 1. Initialize extensions BEFORE the app object
db = SQLAlchemy() 
login = LoginManager() 
login.login_view = 'login' 

app = Flask(__name__)

# 2. Load configuration settings
app.config.from_object(Config)

# 3. Initialize extensions WITH the app
db.init_app(app) 
login.init_app(app) 

# --- Initialize Authlib/OAuth ---
oauth = OAuth(app)
oauth.register(
    'google',
    client_id=app.config.get('GOOGLE_CLIENT_ID'),
    client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v2/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)
# -------------------------------

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