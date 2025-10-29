# app/models.py

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# --- MODEL: Role ---
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')
    def __repr__(self): return f'<Role {self.name}>'

# --- MODEL: User ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256)) # Nullable for OAuth users
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    alumni_id = db.Column(db.Integer, db.ForeignKey('alumni.id'))
    institute_id = db.Column(db.Integer, db.ForeignKey('institute.id'))
    alumni_profile = db.relationship('Alumni', backref='user', uselist=False)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password) if self.password_hash else False
    def __repr__(self): return f'<User {self.username} | Role: {self.role.name if self.role else "None"}>'

# --- MODEL: Alumni ---
class Alumni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=False)
    major = db.Column(db.String(100))
    city = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer, index=True, nullable=False)
    phone_number = db.Column(db.String(20))
    linkedin_id = db.Column(db.String(100))
    photo_file = db.Column(db.String(100), default='default_user.png')
    profile_complete = db.Column(db.Boolean, default=False)
    institute_id = db.Column(db.Integer, db.ForeignKey('institute.id'))
    def __repr__(self): return f'<Alumni {self.name} ({self.graduation_year})>'

# --- MODEL: Event ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100))
    institute_id = db.Column(db.Integer, db.ForeignKey('institute.id'))
    def __repr__(self): return f'<Event {self.title}>'

# --- MODEL: Institute ---
class Institute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    logo_path = db.Column(db.String(255), default='logo.png')
    alumni = db.relationship('Alumni', backref='institute', lazy='dynamic')
    events = db.relationship('Event', backref='institute', lazy='dynamic')
    def __repr__(self): return f'<Institute {self.name}>'