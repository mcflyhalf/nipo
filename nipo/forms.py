from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from nipo.db import schema
from nipo.nipo_api import session

class DictForm(FlaskForm):
    '''
    Custom FlaskForm whose instances can be converted to a dict
    with an .asDict() method. Intentionally not using __iter__
    as it is already implemented for sth else
    '''
    def asDict(self):
        resDict = {}
        for field in self:
            resDict[field.name]= str(field.raw_data[0]) #regretable hack
        return resDict

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=3, message='Please supply a longer username')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=5,message='Please supply a longer password')])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    accept_terms = BooleanField('I accept the terms of this site')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = session.query(schema.User).filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError('Invalid username. Please use a different username.')

    def validate_email(self, email):
        user = session.query(schema.User).filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('Invalid email address. Please use a different email address.')


## Add Entity forms below allow adding Venues, modules, Students Users etc
## In future versions, this code should be self generated during setup
## Generator looks at schema and determines the required fields in the form
## To be Done in the far future or by a mega rockstar!

class AddCourseForm(DictForm):
    uid = StringField('Course UID')
    name = StringField('Course name', validators=[DataRequired()])

class AddVenueForm(DictForm):
    code = StringField('Venue Code')
    name = StringField('Venue name', validators=[DataRequired()]) 
    capacity = IntegerField('capacity')

class AddModuleForm(DictForm):
    code = StringField('Module Code')
    name = StringField('Module name', validators=[DataRequired()])
    course_code = StringField('Course UID')

class AddUserForm(DictForm):
    username = StringField('Course name', validators=[DataRequired()])
    name = StringField('Course name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    privilege = IntegerField('Privilege')
    student_id = StringField('Student ID')

class AddStudentForm(DictForm):
    name = StringField('Course name', validators=[DataRequired()])
    course_uid = StringField('Course ID')
    course = StringField('Course name', validators=[DataRequired()])

