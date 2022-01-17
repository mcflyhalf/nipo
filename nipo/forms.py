import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
from sqlalchemy.exc import NoResultFound
from nipo.db import schema
from nipo.db.utils import get_course_list
from nipo.db.schema import PrivilegeLevel
from nipo.conf import session

form_endpoints = {
	'attach_to_module_individual':'/attach',
	'attach_to_module_file_upload': '/fattach',
	'attach_to_module_entire_course':'/cattach'
}


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
		user = session.query(schema.User).filter(schema.User.username==username.data.lower()).first()
		if user is not None:
			raise ValidationError('Invalid username. Please use a different username.')

	def validate_email(self, email):
		user = session.query(schema.User).filter(schema.User.email==email.data.lower()).first()
		if user is not None:
			raise ValidationError('Invalid email address. Please use a different email address.')


## Add Entity forms below allow adding Venues, modules, Students Users etc
## In future versions, this code should be self generated during setup
## Generator looks at schema and determines the required fields in the form
## To be Done in the far future or by a mega rockstar!

class AddCourseForm(DictForm):
	uid = StringField('Course UID', validators=[DataRequired(), Length(min=5, message='Module code should be exactly 5 characters e.g. EPE17'), Length(max=5, message='Module code should be exactly 5 characters e.g. EPE17')])
	name = StringField('Course name')

class AddVenueForm(DictForm):
	code = StringField('Venue Code')
	name = StringField('Venue name', validators=[DataRequired()]) 
	capacity = IntegerField('capacity')

courses = get_course_list(session)

class AddModuleForm(DictForm):
	code = StringField('Module Code', validators=[DataRequired(), Length(min=5, message='Module code should be exactly 5 characters e.g. EPE17'), Length(max=5, message='Module code should be exactly 5 characters e.g. EPE17')])
	name = StringField('Module name', validators=[DataRequired()])
	course_code = SelectField('Module\'s Course UID', choices=[(course.uid, course.name) for course in courses])

class AddUserForm(DictForm):
	username = StringField('User\'s username', validators=[DataRequired()])
	name = StringField('User\'s name', validators=[DataRequired()])
	email = StringField('User\'s Email', validators=[DataRequired(), Email()])
	privilege = SelectField('User type', choices=[(priv.name, priv.name) for priv in list(PrivilegeLevel)])
	student_id = StringField('User\'s Student ID (if applicable)')

class AddStudentForm(DictForm):
	name = StringField('Student name', validators=[DataRequired()])
	course_uid = SelectField('Student\'s Course', choices=[(course.uid, course.name) for course in courses])

class BulkAddForm(FlaskForm):
	'''
	Base form class for adding entities via a form
	'''
	# csv = FileField(u'csv File', validators=[Regexp(u'^[a-zA-Z0-9_]+\.csv$', message="filenames can only contain alphanumeric and underscore characters"),
	csv = FileField(u'csv File')
	def validate_csv(self, csv):
		if csv.data:
			pass

def add_entity_forms():
	form = {}
	form['course'] = AddCourseForm()
	form['venue'] = AddVenueForm()
	form['user'] = AddUserForm()
	form['student'] = AddStudentForm()
	form['module'] = AddModuleForm()
	form['file_upload'] = BulkAddForm()
	return form


#--------- Attach to module forms--------#

class AttachToModuleForm(FlaskForm):
	@property
	def id_text(self):
		return self.form_name.replace('_','-')


class AttachToModuleIndividualForm(AttachToModuleForm):
	form_name = "attach_to_module_individual_form"
	action = form_endpoints['attach_to_module_individual']

	modulecode = StringField('Module code')
	designation =  SelectField(u'Staff or Student?', choices=[('Student', 'Student'), ('Staff', 'Staff')])
	emailOrId = StringField('Staff email address OR student ID')

	def validate_modulecode(self, code):
		try:
			# Modulecode Must be upppercase
			mod = session.query(schema.Module).filter(schema.Module.code==code.data.upper()).one()
		except NoResultFound:
			raise ValidationError('Invalid module code {}. Module code must be upper case'
					.format(code.data.upper()))
		except:
			raise ValidationError("OtherError")

	def validate_emailOrId(self, emailOrId):
		id_desig_mismatch_notice= \
		'Student ID must be integer, staff email must be valid email address\
		Invalid email or ID for: \t{}'.\
		format(emailOrId.data)

		if self.designation.data.lower() == 'student':
			try:
				int(emailOrId.data)
			except ValueError:
				raise ValidationError(id_desig_mismatch_notice)

		if self.designation.data.lower() == 'staff':
			email_validator = Email(message = id_desig_mismatch_notice)
			email_validator(self, self.designation)
	

class AttachToModuleFileUploadForm(AttachToModuleForm, BulkAddForm):
	form_name = "attach_to_module_file_upload_form"

	action = form_endpoints['attach_to_module_file_upload']


class AttachToModuleEntireCourseForm(AttachToModuleForm):
	form_name = "attach_to_module_entire_course_form"

	modulecode = StringField('Module code')
	course_uid = SelectField('Course uid', choices=[(course.uid, course.name) for course in courses])
	action = form_endpoints['attach_to_module_entire_course']

	def validate_modulecode(self, code):
		mod = session.query(schema.Module).filter(schema.Module.code==code.data.upper()).one_or_none()
		if mod is None:
			raise ValidationError('Invalid module code. Module code must be upper case')


def attach_to_module_forms():
	return [AttachToModuleIndividualForm(),\
		    AttachToModuleFileUploadForm(),\
		    AttachToModuleEntireCourseForm()]
