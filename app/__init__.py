# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from datetime import timedelta # Needed for session lifetime

# 1. Initialize extensions BEFORE the app object
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'login' # Route name for login page redirection

# Explicitly set session cookie security settings for production
login.session_protection = "strong"

oauth = OAuth() # Initialize OAuth registry later

app = Flask(__name__)

# 2. Load configuration settings
app.config.from_object(Config)

# Configure session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_PERMANENT'] = True

# 3. Initialize extensions WITH the app
db.init_app(app)
login.init_app(app)
oauth.init_app(app) # Initialize OAuth with the app instance

# Register Google OAuth client using the loaded config
oauth.register(
    'google',
    client_id=app.config.get('GOOGLE_CLIENT_ID'),
    client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# --- User Loader ---
@login.user_loader
def load_user(id):
    from app.models import User
    return db.session.get(User, int(id))
# --------------------

# 4. Import models and routes LAST
from app import models
from app import routes