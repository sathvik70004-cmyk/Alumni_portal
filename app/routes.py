# app/routes.py

from flask import render_template, request, abort, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from . import app, db, oauth 
from .utils import save_profile_picture 
from .ml_utils import get_recommendations
from app.models import Alumni, Institute, Event, User, Role
from app.forms import (
    IndividualRegistrationForm, InstituteRegistrationForm, LoginForm, 
    ProfileCompletionForm, AdminStudentRegistrationForm, EventForm
)
from datetime import datetime, timedelta 
from sqlalchemy.exc import IntegrityError
import google.generativeai as genai
import os
import traceback 

# --- CRITICAL: Automatic Database Initialization and Data Insertion ---
with app.app_context():
    try:
        if not db.engine.dialect.has_table(db.engine.connect(), "role"):
            print("--- Database setup running (tables not found) ---")
            
            db.create_all()
            
            role_admin = Role(name='Institute_Admin')
            role_alumnus = Role(name='Alumnus')
            role_student = Role(name='Student')
            db.session.add_all([role_admin, role_alumnus, role_student])
            db.session.commit()

            admin_role_id = role_admin.id
            alumnus_role_id = role_alumnus.id

            main_institute = Institute(name='Main University', logo_path='logo.png')
            db.session.add(main_institute)
            db.session.flush() 
            main_institute_id = main_institute.id

            admin_user = User(
                username='admin_main', 
                email='admin@main.edu', 
                role_id=admin_role_id,
                institute_id=main_institute_id
            )
            admin_user.set_password('supersecret')
            db.session.add(admin_user)

            sample_alumni = [
                Alumni(name='Alice Johnson', graduation_year=2025, major='Computer Science', city='New York', phone_number='555-1234', linkedin_id='alice_j', institute_id=main_institute_id, profile_complete=True),
                Alumni(name='Bob Smith', graduation_year=2024, major='Electrical Engineering', city='San Francisco', phone_number='555-5678', linkedin_id='bob_s', institute_id=main_institute_id, profile_complete=True),
            ]
            db.session.add_all(sample_alumni)
            
            sample_events = [
                Event(title='Annual Gala Dinner', date_time=datetime.now() + timedelta(days=60), location='Grand Hall', institute_id=main_institute_id),
                Event(title='Mentorship Workshop', date_time=datetime.now() + timedelta(days=90), location='Online Webinar', institute_id=main_institute_id),
            ]
            db.session.add_all(sample_events)
            
            db.session.commit()
            print("--- LIVE DATABASE SCHEMA AND DATA SUCCESSFULLY CREATED ON STARTUP ---")
    except Exception as e:
        print(f"--- Database setup skipped (may already exist) or failed: {e} ---")
        db.session.rollback()


# --- PUBLIC ROUTES ---
@app.route('/')
def home():
    institute = db.session.get(Institute, 1) 
    logo_path = institute.logo_path if institute else 'logo.png' 
    upcoming_events = []
    if institute:
        upcoming_events = Event.query.filter(Event.date_time >= datetime.now()).order_by(Event.date_time).limit(2).all()
    return render_template('index.html', institute_logo=logo_path, events=upcoming_events)

@app.route('/events')
def events_list():
    all_upcoming_events = Event.query.filter(Event.date_time >= datetime.now()).order_by(Event.date_time).all()
    return render_template('events.html', events=all_upcoming_events)

@app.route('/alumni', methods=['GET'])
def alumni_directory():
    selected_year = request.args.get('year') 
    query = Alumni.query
    if selected_year and selected_year.isdigit():
        filter_year = int(selected_year)
        query = query.filter_by(graduation_year=filter_year)
    filtered_alumni = query.order_by(Alumni.graduation_year.desc()).all()
    all_years_query = db.session.query(Alumni.graduation_year).distinct().order_by(Alumni.graduation_year.desc())
    graduation_years = [y[0] for y in all_years_query.all()]
    return render_template('alumni.html', alumni=filtered_alumni, years=graduation_years, selected_year=selected_year)

@app.route('/alumni/<int:alumni_id>')
@login_required 
def alumni_profile(alumni_id):
    alumnus = db.session.get(Alumni, alumni_id)
    if alumnus is None: abort(404)
    user_email = alumnus.user.email if alumnus.user else f"{alumnus.linkedin_id or 'alumnus'}@example.com"
    return render_template('profile.html', alumnus=alumnus, email_id=user_email)

# --- AUTHENTICATION ROUTES ---
@app.route('/register_hub')
def register_hub():
    return render_template('register_hub.html', title='Choose Registration Type')

@app.route('/register/individual', methods=['GET', 'POST'])
def register_individual():
    if current_user.is_authenticated: return redirect(url_for('home'))
    form = IndividualRegistrationForm()
    if form.validate_on_submit():
        try:
            alumnus_role = Role.query.filter_by(name='Alumnus').first()
            if not alumnus_role: raise Exception("Default 'Alumnus' role not found.")
            user = User(username=form.username.data, email=form.email.data, role_id=alumnus_role.id)
            user.set_password(form.password.data)
            new_alumni_profile = Alumni(name=form.name.data, graduation_year=form.graduation_year.data, institute_id=1)
            user.alumni_profile = new_alumni_profile
            db.session.add_all([user, new_alumni_profile])
            db.session.commit()
            flash('Registration successful! Please log in to complete your profile.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Database error: Username or Email already exists.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
    return render_template('register_individual.html', title='Alumni/Student Registration', form=form)

@app.route('/register/institute', methods=['GET', 'POST'])
def register_institute():
    if current_user.is_authenticated: return redirect(url_for('home'))
    form = InstituteRegistrationForm()
    if form.validate_on_submit():
        try:
            admin_role = Role.query.filter_by(name='Institute_Admin').first()
            if not admin_role: raise Exception("Default 'Institute_Admin' role not found.")
            new_institute = Institute(name=form.institute_name.data, logo_path='default_institute_logo.png')
            db.session.add(new_institute)
            db.session.flush()
            admin_user = User(username=form.admin_username.data, email=form.admin_email.data, role_id=admin_role.id, institute_id=new_institute.id)
            admin_user.set_password(form.admin_password.data)
            db.session.add(admin_user)
            db.session.commit()
            flash(f'Institute "{new_institute.name}" registered successfully! Admin account created.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Database error: Institute, admin username, or email already exists.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
    return render_template('register_institute.html', title='Institute Registration', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.alumni_profile and not current_user.alumni_profile.profile_complete:
            flash('Please complete your profile details to continue.', 'warning')
            return redirect(url_for('complete_profile')) 
        return redirect(url_for('home')) 
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.username_or_email.data) | (User.email == form.username_or_email.data)).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username/email or password', 'danger')
            return redirect(url_for('login'))
        login_user(user) 
        if user.alumni_profile and not user.alumni_profile.profile_complete:
            flash('Welcome! Please complete your profile to activate full portal access.', 'warning')
            return redirect(url_for('complete_profile'))
        flash('Login successful!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('home'))
    return render_template('login.html', title='Log In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))

# --- GOOGLE OAUTH ROUTES ---
@app.route('/login/google')
def google_login():
    from . import oauth
    redirect_uri = url_for('google_auth', _external=True)
    if not hasattr(oauth, 'google'):
        flash('Google OAuth not configured correctly.', 'danger')
        return redirect(url_for('login'))
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorized')
def google_auth():
    from . import oauth
    try:
        token = oauth.google.authorize_access_token()
        userinfo = oauth.google.parse_id_token(token, nonce=None) 
    except Exception as e:
        flash(f'Google sign-in failed during token exchange. Error: {e}', 'danger')
        traceback.print_exc()
        return redirect(url_for('login'))
    email = userinfo.get('email')
    if not email:
        flash('Could not retrieve email from Google.', 'danger')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=email).first()
    if user is None: # New user via Google
        try:
            alumnus_role = Role.query.filter_by(name='Alumnus').first() 
            main_institute = Institute.query.get(1)
            if not alumnus_role or not main_institute: raise Exception("Core Role/Institute data missing")
            username = userinfo.get('name', email.split('@')[0]).replace(" ", "")
            temp_username = username
            counter = 1
            while User.query.filter_by(username=temp_username).first():
                temp_username = f"{username}{counter}"
                counter += 1
            username = temp_username
            new_alumni_profile = Alumni(name=userinfo.get('name', 'Google User'), graduation_year=datetime.now().year, institute_id=main_institute.id, profile_complete=False)
            user = User(username=username, email=email, role_id=alumnus_role.id, institute_id=main_institute.id, alumni_profile=new_alumni_profile)
            user.set_password('GOOGLE_OAUTH_USER_NO_PASSWORD')
            db.session.add_all([user, new_alumni_profile])
            db.session.commit()
            flash('New account created via Google. Please complete your profile.', 'success')
        except IntegrityError: 
            db.session.rollback()
            user = User.query.filter_by(email=email).first()
            if not user:
                flash('Error creating account. Username might be taken.', 'danger')
                return redirect(url_for('register_hub'))
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred during creation: {e}', 'danger')
            traceback.print_exc()
            return redirect(url_for('login'))
    login_user(user)
    if user.alumni_profile is None: 
        flash('Account error: Profile not found. Please complete registration.', 'danger')
        return redirect(url_for('complete_profile')) 
    if not user.alumni_profile.profile_complete:
        flash('Successfully signed in with Google. Please complete your profile details.', 'warning')
        return redirect(url_for('complete_profile'))
    flash('Login successful via Google!', 'success')
    return redirect(url_for('home'))

# --- PROFILE COMPLETION & DASHBOARD ---
@app.route('/complete_profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    if current_user.role.name not in ['Alumnus', 'Student']: return redirect(url_for('dashboard'))
    if not current_user.alumni_profile: 
        try:
            main_institute = Institute.query.get(1)
            if not main_institute: raise Exception("Main institute not found.")
            new_alumni_profile = Alumni(name=current_user.username, graduation_year=datetime.now().year, institute_id=main_institute.id)
            current_user.alumni_profile = new_alumni_profile
            db.session.add(new_alumni_profile)
            db.session.commit()
        except Exception as e:
            flash(f"Error creating profile link: {e}", "danger")
            return redirect(url_for('logout'))
    if current_user.alumni_profile.profile_complete: return redirect(url_for('dashboard'))
    form = ProfileCompletionForm()
    if form.validate_on_submit():
        try:
            alumni = current_user.alumni_profile
            alumni.major = form.major.data
            alumni.city = form.city.data
            alumni.phone_number = form.phone_number.data
            alumni.linkedin_id = form.linkedin_id.data
            if form.photo.data:
                picture_file = save_profile_picture(form.photo.data, alumni.id)
                alumni.photo_file = picture_file
            else:
                alumni.photo_file = 'default_user.png'
            alumni.profile_complete = True 
            db.session.commit()
            flash('Profile successfully completed!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving profile: {e}", "danger")
            traceback.print_exc()
    return render_template('complete_profile.html', title='Complete Profile', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name in ['Alumnus', 'Student']:
        if not current_user.alumni_profile or not current_user.alumni_profile.profile_complete:
            return redirect(url_for('complete_profile'))
        return render_template('dashboard_alumni.html', title='Alumni Dashboard')
    elif current_user.role.name == 'Institute_Admin':
        return render_template('dashboard_institute.html', title='Institute Dashboard')
    else: 
        return redirect(url_for('home')) 

# --- ML RECOMMENDATIONS ---
@app.route('/recommendations')
@login_required
def recommendations():
    if current_user.role.name not in ['Alumnus', 'Student']: return redirect(url_for('dashboard'))
    if not current_user.alumni_profile or not current_user.alumni_profile.profile_complete: return redirect(url_for('complete_profile'))
    if Alumni.query.count() < 2:
         flash('Not enough alumni data available to generate recommendations.', 'warning')
         return render_template('recommendations.html', recommended_alumni=[], title='Recommended Connections')
    current_alumnus_id = current_user.alumni_id
    try:
        recommended_ids = get_recommendations(current_alumnus_id, db.session)
        recommended_alumni = Alumni.query.filter(Alumni.id.in_(recommended_ids)).all()
    except Exception as e:
         flash(f"Error generating recommendations: {e}", "danger")
         traceback.print_exc()
         recommended_alumni = []
    return render_template('recommendations.html', recommended_alumni=recommended_alumni, title='Recommended Connections')

# --- ADMIN ROUTES ---
@app.route('/admin/register_student', methods=['GET', 'POST'])
@login_required
def admin_register_student():
    if current_user.role.name != 'Institute_Admin': abort(403)
    form = AdminStudentRegistrationForm()
    if form.validate_on_submit():
        try:
            alumnus_role = Role.query.filter_by(name='Alumnus').first()
            new_alumni_profile = Alumni(
                name=form.name.data, graduation_year=form.graduation_year.data,
                major=form.major.data, city=form.city.data,
                phone_number=form.phone_number.data or None,
                linkedin_id=form.linkedin_id.data or None,
                profile_complete=True, institute_id=current_user.institute_id
            )
            default_password = 'Password123'
            username_data = form.username.data or form.email.data.split('@')[0]
            temp_username = username_data
            counter = 1
            while User.query.filter_by(username=temp_username).first():
                temp_username = f"{username_data}{counter}"
                counter += 1
            username_data = temp_username
            new_user = User(
                username=username_data, email=form.email.data,
                role_id=alumnus_role.id, institute_id=current_user.institute_id,
                alumni_profile=new_alumni_profile
            )
            new_user.set_password(default_password)
            db.session.add_all([new_user, new_alumni_profile])
            db.session.commit()
            flash(f'Successfully registered {form.name.data}. Default password: {default_password}', 'success')
            return redirect(url_for('dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: Username or Email already exists.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
            traceback.print_exc()
    return render_template('admin_register_student.html', title='Register New Student', form=form)

@app.route('/admin/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    # --- THIS IS THE LINE WITH THE TYPO ---
    if current_user.role.name != 'Institute_Admin': abort(403) # <-- Corrected from 4H03
    form = EventForm()
    if form.validate_on_submit():
        try:
            new_event = Event(
                title=form.title.data, description=form.description.data,
                date_time=form.date_time.data, location=form.location.data,
                institute_id=current_user.institute_id
            )
            db.session.add(new_event)
            db.session.commit()
            flash(f'Event "{new_event.title}" added successfully.', 'success')
            return redirect(url_for('events_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating event: {e}", "danger")
            traceback.print_exc()
    return render_template('admin_create_event.html', title='Create New Event', form=form)

# --- CHATBOT API ---
@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    api_key = app.config.get('GEMINI_API_KEY')
    if not api_key or api_key == 'YOUR_LOCAL_GEMINI_API_KEY_HERE':
        app.logger.error("Gemini API Key is not configured.")
        return jsonify({'reply': 'Sorry, the chatbot service is not configured.'}), 500
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.0-pro')
    except Exception as e:
        app.logger.error(f"Failed to configure Gemini model: {e}")
        return jsonify({'reply': 'Sorry, chatbot configuration error.'}), 500
    data = request.get_json()
    user_message = data.get('message')
    if not user_message: return jsonify({'reply': 'No message received.'}), 400
    try:
        full_prompt = f"You are a helpful assistant for an 'Alumni Portal' website. Answer questions about networking, careers, and the portal. Be friendly and professional. User: \"{user_message}\" Assistant:"
        response = model.generate_content(full_prompt)
        bot_reply = response.text
    except Exception as e:
        app.logger.error(f"Gemini API call failed: {e}")
        try:
            if response and hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                bot_reply = "I'm sorry, I can't respond to that due to my safety settings."
            else:
                bot_reply = "Sorry, I encountered an error. Please try again."
        except Exception:
             bot_reply = "Sorry, I encountered an unknown error. Please try again."
    return jsonify({'reply': bot_reply})

# --- ERROR HANDLERS ---
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() 
    return render_template('500.html'), 500