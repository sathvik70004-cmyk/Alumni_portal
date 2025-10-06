# app/routes.py (FINAL CODE WITH AUTOMATIC DB SETUP)

from flask import render_template, request, abort, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from . import app, db 
from app.models import Alumni, Institute, Event, User, Role
from app.forms import IndividualRegistrationForm, InstituteRegistrationForm, LoginForm, ProfileCompletionForm, AdminStudentRegistrationForm
from datetime import datetime, timedelta 
from sqlalchemy.exc import IntegrityError 

# --- CRITICAL: Automatic Database Initialization and Data Insertion ---
# This block runs BEFORE the first request to ensure tables exist.
with app.app_context():
    # Only create tables if they don't exist (important for production)
    if not db.engine.dialect.has_table(db.engine.connect(), "role"):
        print("Database setup running...")
        
        db.create_all()
        
        # Insert initial data into the empty database
        role_admin = Role(name='Institute_Admin')
        role_alumnus = Role(name='Alumnus')
        role_student = Role(name='Student')
        db.session.add_all([role_admin, role_alumnus, role_student])
        db.session.commit()

        # Fetch the Role IDs (essential for linking users)
        admin_role_id = Role.query.filter_by(name='Institute_Admin').first().id
        alumnus_role_id = Role.query.filter_by(name='Alumnus').first().id

        # Insert Initial Institute and Admin User
        main_institute = Institute(name='Main University', logo_path='logo.png')
        db.session.add(main_institute)

        admin_user = User(
            username='admin_main', 
            email='admin@main.edu', 
            role_id=admin_role_id,
            institute_id=main_institute.id
        )
        admin_user.set_password('supersecret')
        db.session.add(admin_user)

        # Insert Sample Alumni and Events
        sample_alumni = [
            Alumni(name='Alice Johnson', graduation_year=2025, major='Computer Science', city='New York', phone_number='555-1234', linkedin_id='alice_j', institute_id=main_institute.id, profile_complete=True),
            Alumni(name='Bob Smith', graduation_year=2024, major='Electrical Engineering', city='San Francisco', phone_number='555-5678', linkedin_id='bob_s', institute_id=main_institute.id, profile_complete=True),
        ]
        db.session.add_all(sample_alumni)
        
        sample_events = [
            Event(title='Annual Gala Dinner', date_time=datetime.now() + timedelta(days=60), location='Grand Hall', institute_id=main_institute.id),
            Event(title='Mentorship Workshop', date_time=datetime.now() + timedelta(days=90), location='Online Webinar', institute_id=main_institute.id),
        ]
        db.session.add_all(sample_events)
        
        db.session.commit()
        print("---LIVE DATABASE SCHEMA AND DATA SUCCESSFULLY CREATED ON STARTUP---")


# --- PUBLIC ROUTES ---

@app.route('/')
def home():
    institute = db.session.get(Institute, 1)
    logo_path = institute.logo_path if institute else 'logo.png' 
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
    
    graduation_years = db.session.query(Alumni.graduation_year).distinct().order_by(Alumni.graduation_year.desc()).all()
    graduation_years = [y[0] for y in graduation_years] 
        
    return render_template(
        'alumni.html', 
        alumni=filtered_alumni, 
        years=graduation_years,
        selected_year=selected_year
    )

@app.route('/alumni/<int:alumni_id>')
@login_required 
def alumni_profile(alumni_id):
    alumnus = db.session.get(Alumni, alumni_id)
    if alumnus is None:
        abort(404)
    email_id = f"{alumnus.linkedin_id}@example.edu"
    return render_template('profile.html', alumnus=alumnus, email_id=email_id)


# --- AUTHENTICATION/REGISTRATION ROUTES ---

@app.route('/register_hub')
def register_hub():
    return render_template('register_hub.html', title='Choose Registration Type')


@app.route('/register/individual', methods=['GET', 'POST'])
def register_individual():
    form = IndividualRegistrationForm()
    
    if form.validate_on_submit():
        try:
            alumnus_role = Role.query.filter_by(name='Alumnus').first()
            user = User(
                username=form.username.data, 
                email=form.email.data,
                role_id=alumnus_role.id 
            )
            user.set_password(form.password.data)

            new_alumni_profile = Alumni(
                name=form.name.data,
                graduation_year=form.graduation_year.data,
                institute_id=1 
            )
            
            user.alumni_profile = new_alumni_profile 
            
            db.session.add_all([user, new_alumni_profile])
            db.session.commit()
            
            flash('Registration successful! Please log in to complete your profile.', 'success')
            return redirect(url_for('login')) 
        
        except IntegrityError:
            db.session.rollback()
            flash('Database error during registration.', 'danger')
            
    return render_template('register_individual.html', title='Alumni/Student Registration', form=form)


@app.route('/register/institute', methods=['GET', 'POST'])
def register_institute():
    form = InstituteRegistrationForm()
    if form.validate_on_submit():
        try:
            admin_role = Role.query.filter_by(name='Institute_Admin').first()
            new_institute = Institute(
                name=form.institute_name.data,
                logo_path='default_institute_logo.png' 
            )
            db.session.add(new_institute)
            db.session.flush() 

            admin_user = User(
                username=form.admin_username.data, 
                email=form.admin_email.data,
                role_id=admin_role.id,
                institute_id=new_institute.id 
            )
            admin_user.set_password(form.admin_password.data)
            
            db.session.add(admin_user)
            db.session.commit()
            
            flash(f'Institute "{new_institute.name}" registered successfully! Admin account created.', 'success')
            return redirect(url_for('login')) 
        
        except IntegrityError:
            db.session.rollback()
            flash('Database error: Check if the institute name or admin credentials already exist.', 'danger')
            
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
        user = User.query.filter(
            (User.username == form.username_or_email.data) | 
            (User.email == form.username_or_email.data)
        ).first()

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


# --- PROFILE COMPLETION ROUTE ---

@app.route('/complete_profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    if current_user.role.name not in ['Alumnus', 'Student']:
        flash('Your profile access is managed by the institute admin.', 'info')
        return redirect(url_for('dashboard')) 

    if current_user.alumni_profile.profile_complete:
        flash('Your profile is already complete.', 'info')
        return redirect(url_for('dashboard'))
        
    form = ProfileCompletionForm()

    if form.validate_on_submit():
        alumni = current_user.alumni_profile
        alumni.major = form.major.data
        alumni.city = form.city.data
        alumni.phone_number = form.phone_number.data
        alumni.linkedin_id = form.linkedin_id.data
        alumni.profile_complete = True 
        alumni.photo_file = 'user_' + str(alumni.id) + '.png' 

        db.session.commit()
        flash('Profile successfully completed! You now have full access.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('complete_profile.html', title='Complete Profile', form=form)


# --- DASHBOARD & ADMIN ROUTES ---

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name in ['Alumnus', 'Student'] and not current_user.alumni_profile.profile_complete:
        return redirect(url_for('complete_profile'))

    if current_user.role.name == 'Institute_Admin':
        return render_template('dashboard_institute.html', title='Institute Dashboard')
    
    return render_template('dashboard_alumni.html', title='Alumni Dashboard') 


@app.route('/admin/register_student', methods=['GET', 'POST'])
@login_required
def admin_register_student():
    if current_user.role.name != 'Institute_Admin':
        flash('Access denied: You must be an Institute Administrator.', 'danger')
        return redirect(url_for('dashboard'))

    form = AdminStudentRegistrationForm()
    
    if form.validate_on_submit():
        try:
            alumnus_role = Role.query.filter_by(name='Alumnus').first()
            
            new_alumni_profile = Alumni(
                name=form.name.data,
                graduation_year=form.graduation_year.data,
                major=form.major.data,
                city=form.city.data,
                phone_number=form.phone_number.data if form.phone_number.data else None,
                linkedin_id=form.linkedin_id.data if form.linkedin_id.data else None,
                profile_complete=True, 
                institute_id=current_user.institute_id
            )
            
            default_password = 'Password123' 
            username_data = form.username.data if form.username.data else form.email.data.split('@')[0]
            
            new_user = User(
                username=username_data, 
                email=form.email.data,
                role_id=alumnus_role.id,
                institute_id=current_user.institute_id
            )
            new_user.set_password(default_password)

            new_user.alumni_profile = new_alumni_profile 
            
            db.session.add_all([new_user, new_alumni_profile])
            db.session.commit()
            
            flash(f'Successfully registered {form.name.data}. Default password is: {default_password}', 'success')
            return redirect(url_for('dashboard'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Error: Username or Email already exists.', 'danger')

    return render_template('admin_register_student.html', title='Register New Student', form=form)