import datetime
import os
from nipo.attendance import ModuleAttendance
from nipo import attendance, production_session, test_session, db
from flask import Flask, flash, request, render_template, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from nipo.db import schema
session = test_session		#Change to production_session in the production environment. This would then utilise production data(bases) 

#The nipo.forms import requires the session var so it is done after session's creation.
from nipo.forms import LoginForm, RegistrationForm


#TODO: Add login required to relevant routes


app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return session.query(schema.User).filter(id==int(user_id)).one_or_none()

login_manager.login_view = 'login'

def get_attendance_module(modulecode):
	try:
		mod_attendance = ModuleAttendance(modulecode)

	except ValueError:
		#Handle this error better
		return "Invalid module code >>{}<<".format(modulecode)

	return mod_attendance.getAttendance()




def get_attendance_student(studentID):
	stud_attendance = attendance.StudentAttendance(studentID, session=session)
	modules = stud_attendance.get_student_modules()
	modulecodes = [mod.code for mod in modules]

	student_attendance = {}

	for modulecode in modulecodes:
		student_attendance[str(modulecode)]=stud_attendance.\
											get_module_attendance(modulecode)

	return student_attendance



def get_attendance_student_module(studentID,modulecode):

	stud = attendance.StudentAttendance(studentID, session)
	return stud.get_module_attendance(modulecode)


def update_attendance_student_module(studentID, modulecode, sessiondate, present=False):
	#Check for exceptions thrown in case of non-existent student and invalid session date. then catch them as appropriate
	mod_attendance = ModuleAttendance(modulecode, session)
	mod_attendance.updateAttendance(studentID,sessiondate,present=present)

def mark_attendance_students_module(stud_attendances, modulecode, sessiondate):
	'''Accept a dictionary of key:value pairs where the keys are student ID's and the values are True or False for present and absent for each respective student'''
	assert type(stud_attendances) is dict
	mod_attendance = ModuleAttendance(modulecode, session)

	for ID in stud_attendances:
		mod_attendance.updateAttendance(ID, sessiondate,present=stud_attendances[ID])

def recognise_student(studentID=None, encoding=None, face_pixels=None, session=session):
	if studentID is not None:
		student = attendance.StudentAttendance(studentID, session)
	elif encoding is not None:
		student = get_student_from_encoding(encoding)
	elif face_pixels is not None:
		student = get_student_from_face_pixels(face_pixels)
	else:
		raise ValueError("No student ID, face encoding or face pixels provided")
	return student


def get_student_from_encoding(encoding):
	return attendance.get_student_from_encoding(encoding, session)

def get_student_from_face_pixels(face_pixels):
	return attendance.get_student_from_pixels(face_pixels, session)

#Probably want to move this method elsewhere
def get_course_list(session):
	courses = session.query(db.schema.Course).\
							limit(10).\
							all()

	return courses


#Landing page, display the courses (e.g TIEY4, Form 1, Grade 3B etc)
@app.route('/')
@app.route('/index/')
#@login_required
def landing():
	'''get Course list and display it using a template'''
	courses = get_course_list(session)
	return render_template('list_courses.html', courses = courses)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('landing'))

@app.route('/login', methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('landing'))
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		user = session.query(schema.User).\
					  filter(schema.User.username == username.lower()).\
									  one_or_none()

		if user is None or not user.check_password(password):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		
		flash('Login successful')
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('landing')
		#print ("Next Page is >>>>>>{}".format(user.is_authenticated))
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

#This route will need to be hidden in future/require login because student wouldnt register themselves. Only an admin should register students. We probably also want to be able to register students in bulk using a csv or excel file
@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('landing'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = schema.User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		session.add(user)
		session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

under_cons_msg = "OOPS! This part of the website is still under construction"

# Return a list of the modules that a student is taking
@app.route('/modules', methods = ['GET','POST'])
def get_student_modules():
	return get_student_attendance()

# Return attendance record for the student logged in for the specified module
@app.route('/module/attendance', methods = ['GET','POST'])
def get_student_module_attendance():
	if request.method == 'POST':
		studentID = request.form.get('studentID')
		modulecode = request.form.get('modulecode')

		student_attendance = get_attendance_student_module(studentID,modulecode)
		resp = dict()
		resp['Student ID'] = studentID
		resp['Module Code'] = "Module Name not yet Implemented"	#To Do
		resp['Student Name'] = "student Name not yet implemented"	#To Do
		resp['Module Name'] = modulecode 
		resp['Student attendance'] = student_attendance

		return jsonify(resp) 	#TODO: Have this returned by a pretty template
	return under_cons_msg + 'for a Get request'

# Return the modules a student is enrolled in with summary attendance (Dashboard)
@app.route('/student', methods = ['GET','POST'])
def get_student_attendance():	#For all modules
	if request.method == 'POST':
		studentID = request.form.get('studentID')
		student = attendance.StudentAttendance(studentID,session)
		student_modules = student.modules

		student_attendance = dict()

		#TODO: Include student name and ID in this response

		for module in student_modules:
			student_attendance[module.code] = student.get_module_attendance(module.code)

		return jsonify(student_attendance) 	#TODO: Have this returned by a pretty  dashboard-like template
	return under_cons_msg + 'for a Get request'


# Return attendance for a student for a module 
@app.route('/student/module', methods = ['GET','POST'])
def get_module_attendance_student():	#Not Yet implemented
	return get_student_module_attendance()#TODO: Have this returned by a pretty template

#Return the list of students in a module
@app.route('/students', methods = ['POST'])
def get_module_students():		#Not Yet implemented
	if request.method == 'POST':
		modulecode = request.form.get('modulecode')
		module = attendance.ModuleAttendance(modulecode, session)

		mod_students = module.students

		resp = dict()

		for student in mod_students:
			resp[student.id] = dict()
			resp[student.id]['Name'] = student.name
			#resp[student.id]['Attendance'] = 

		#student_attendance = get_attendance_student_module(studentID,modulecode)

		return jsonify(resp) 	#TODO: Have this returned by a pretty template
	return under_cons_msg + 'for a Get request'

# Return attendance record for the student logged in for the specified module
@app.route('/module/attendance/mark', methods = ['GET','POST'])
def set_student_module_attendance():
	if request.method == 'POST':
		studentID = request.form.get('studentID')
		modulecode = request.form.get('modulecode')
		status = request.form.get('status')
		sess_date = request.form.get('SessionDate')	#Expects YYYY-MM-DDTHH:MM Format (Iso 8601)
		try:
			studentID = int(studentID)
		except ValueError:
			return "The student ID {} must be a number (integer)".format(studentID)
		try:
			sess_date = datetime.datetime.strptime(sess_date, '%Y-%m-%dT%H:%M')
		except ValueError:
			return "The date {} is not in the required YYYY-MM-DDTHH:mm format".format(sess_date) 

		if status.lower() == "present":
			status = True
		else:
			status = False

		mod_attendance = attendance.ModuleAttendance(modulecode, session)

		mod_attendance.updateAttendance(studentID,sess_date, present=status)
		try:
			mod_attendance.updateAttendance(studentID,sess_date, present=status)			
		except ValueError:
			return "The date >>{}<< does not have a class session for the module with code >>{}<<".format(sess_date.isoformat(), modulecode)

		#redirect to show student's attendance for the module. Preserve the POST parameters
		return redirect(url_for('get_student_module_attendance'), code=307)
	return under_cons_msg + 'for a Get request'


app.debug = True
if __name__ == '__main__':
	app.run(debug = True)