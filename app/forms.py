# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional
from flask_wtf.file import FileField, FileAllowed
from app.models import User, Institute 

class IndividualRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]
    )
    name = StringField('Full Name', validators=[DataRequired()])
    graduation_year = IntegerField('Graduation Year', validators=[DataRequired()])
    submit = SubmitField('Register')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('That username is taken. Please choose a different one.')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('That email address is already registered.')


class InstituteRegistrationForm(FlaskForm):
    institute_name = StringField('Institute Name', validators=[DataRequired()])
    admin_username = StringField('Admin Username', validators=[DataRequired(), Length(min=4, max=25)])
    admin_email = StringField('Admin Email', validators=[DataRequired(), Email()])
    admin_password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    admin_password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('admin_password')]
    )
    submit = SubmitField('Register Institute')
    def validate_institute_name(self, institute_name):
        institute = Institute.query.filter_by(name=institute_name.data).first()
        if institute is not None:
            raise ValidationError('That institute is already registered.')


class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class ProfileCompletionForm(FlaskForm):
    major = StringField('Major/Discipline', validators=[DataRequired()])
    city = StringField('Current City', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    linkedin_id = StringField('LinkedIn ID (e.g., your-profile-name)', validators=[DataRequired()])
    photo = FileField('Profile Picture (.jpg or .png)', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!'),
        DataRequired()
    ])
    submit = SubmitField('Complete Profile')


class AdminStudentRegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    graduation_year = IntegerField('Graduation Year', validators=[DataRequired()])
    major = StringField('Major/Discipline', validators=[DataRequired()])
    city = StringField('Current City', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    linkedin_id = StringField('LinkedIn ID', validators=[Optional()])
    email = StringField('Email (Mandatory)', validators=[DataRequired(), Email()])
    username = StringField('Username (Optional)', validators=[Optional(), Length(max=25)])
    submit = SubmitField('Register Student/Alumnus')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('That email is already registered to a user.')
        
# app/forms.py (Add this class to the end)

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, Length

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    # DateTimeLocalField is a specialized field for date/time input
    date_time = DateTimeLocalField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Add Event')