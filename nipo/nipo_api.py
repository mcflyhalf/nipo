import datetime
import os
from nipo.attendance import ModuleAttendance
from nipo import attendance, session, db
from flask import Flask, flash, request, render_template, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from nipo.db import schema, get_student_list, get_module_list, get_course_list, add_entity
from nipo.task_mgr import get_celery_app 
#The nipo.forms import requires the session var so it is done after session's creation.
from nipo.forms import LoginForm, RegistrationForm, AddCourseForm, AddVenueForm, AddUserForm, AddStudentForm, AddModuleForm
import random
import time


#TODOs:
# 1. Make provision to scale (celery workers, multithreading?).
# 2. Create view to check individual attendance
#


app = Flask(__name__)
celery_app = get_celery_app()
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.config['db_session'] = session #iss this ever used?
#TODO: Modify app config to expire sessions after a day 
#See https://stackoverflow.com/questions/11783025/is-there-an-easy-way-to-make-sessions-timeout-in-flask
login_manager = LoginManager(app)
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return session.query(schema.User).filter(schema.User.id==int(user_id)).one_or_none()

def make_form_dict():
	form = {}
	form['course'] = AddCourseForm()
	form['venue'] = AddVenueForm()
	form['user'] = AddUserForm()
	form['student'] = AddStudentForm()
	form['module'] = AddModuleForm()
	return form

@app.route('/')
@app.route('/index/')
@login_required
def landing():
	'''Display landing page for student, staff(instructor) or admin'''

	if current_user.privilege == schema.PrivilegeLevel.student.name:
		modules = get_module_list(session)	#TODO: This function currently gets all modules in the system. Need to modify so that it only gets the modules a student is enrolled to. Nipo challenge??
		return render_template('student_dashboard.html',modules = modules)

		courses = get_course_list(session)
		return render_template('list_courses.html', courses = courses)

	elif current_user.privilege == schema.PrivilegeLevel.staff.name:
		#TODO: Only show modules staff member is registered to. For each module, only show valid dates. Nipo challenge?
		modules = get_module_list(session)
		dates = []
		formatted_dates = []
		for module in modules:
			dates += ModuleAttendance(module.code, session).dates

		for date in dates:
			human_friendly_format = date.strftime('%a %d %b %H:%M')
			iso_format = date.strftime('%Y-%m-%dT%H:%M')
			combined_format = {"human friendly format": human_friendly_format,
								"iso format": iso_format}

			formatted_dates.append(combined_format)

		students = get_student_list(session)
		for student in students:
			student.status=random.choice(["student-absent","student-present"])
		return render_template('staff_dashboard.html',dates=formatted_dates,students=students,modules=modules)

	elif current_user.privilege == schema.PrivilegeLevel.admin.name:
		tables = db.get_tables_data(session)
		form = make_form_dict()
		return render_template('admin_dashboard.html', tables=tables, form=form)

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
		
		login_user(user, remember=form.remember_me.data)
		#Not sure if it is necessary to commit/persist after every login
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('landing')
		#print ("Next Page is >>>>>>{}".format(user.is_authenticated))
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

#The following registration flow has several steps
#But makes the most sense for an academic institution
#Will only be implemented if some academic institution is interested
#Only an admin should register students. 
#Current implementation idea, admin registers email via admin landing
#(creates a passwordless account that cannot login)
#Then student is notified that they can register on this page (including a token)
#They present the token and the email already provided by admin
#They now set their password
@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('landing'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = schema.User(username=form.username.data.lower(), email=form.email.data,authenticated=False,active=True)
		user.set_password(form.password.data)
		session.add(user)
		session.commit()		
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

under_cons_msg = "OOPS! This part of the website is still under construction"

@app.route('/userdetails')
@login_required
def get_user_details():
	'''Get Student's Name and ID'''
	user_detail = {}
	if current_user.privilege == 'student':
		user_detail['name'] = current_user.name
		user_detail['student_id'] = current_user.student_id
		user_detail['status'] = 0	#TODO: Determine status codes for Nipo

	else:
		user_detail['status'] = 1	#TODO: Determine status codes for Nipo
	
	return jsonify(user_detail)



#Will need to rethink these routes. 
	# Currently thinking of them as separate pages.
	# They should however exist as part of a single page that calls javascript to get data.
	# The page then evolves as appropriate
	# The routes would thus mostly return json data. Rarely ever an HTML template

# Return a list of the modules that a student is taking
@app.route('/modules', methods = ['GET','POST'])
def get_student_modules():
	return get_student_attendance()

# Return attendance record for the student logged in for the specified module
@app.route('/module/attendance', methods = ['GET','POST'])
def get_student_module_attendance():
	if request.method == 'POST':
		req = request.get_json()
		studentID = req['studentID']
		modulecode = req['modulecode']
		student_attendance = get_attendance_student_module(studentID,modulecode)
		resp = student_attendance

		return jsonify(resp) 	#TODO: Have this returned by a pretty render_template TODO: MAke the datetime in this response ISO8601 format
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
		req = request.get_json()
		studentID = req['studentID']
		modulecode = req['modulecode']
		status = req['status']
		sess_date = req['SessionDate']	#Expects YYYY-MM-DDTHH:MM Format (Iso 8601)
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

		# mod_attendance.updateAttendance(studentID,sess_date, present=status)
		try:
			mod_attendance.updateAttendance(studentID,sess_date, present=status)			
		except ValueError:
			return "The date >>{}<< does not have a class session for the module with code >>{}<<".format(sess_date.isoformat(), modulecode)

		#redirect to show student's attendance for the module. Preserve the POST parameters
		return redirect(url_for('get_student_module_attendance'), code=307)
	return under_cons_msg + 'for a Get request'

#Potentially change to /modify/entity to allow deleting through this route as well
@app.route('/add/<entity_type>', methods=['POST'])
def request_add_entity(entity_type):
	print("Entity type: {}\nPayload: {}".format(entity_type,123))
	# return 'Received Form'

	all_forms = make_form_dict()
	form = all_forms[entity_type.lower()]
	if form.validate_on_submit():
		form_data = form.asDict()
		form_data.pop('csrf_token')
		#Use celery for long running task (db access)
		task_info = add_entity.delay(form_data,entity_type)
		response = {}
		response['request-id']= task_info.id
		response['status']= task_info.status
		return jsonify(response)
	return jsonify({'status':'FAILURE', 
					'info':'Invalid form data'})

#Does this require login??
@app.route('/status/<task_id>')
def get_task_status(task_id):
	task = celery_app.AsyncResult(task_id)
	response = {}
	response['task-id'] = task_id
	response['status'] = task.status
	response['info'] = str(task.info)
	return jsonify(response)	

# @app.route('/debug', methods = ['GET','POST'])
# def get_debugger():
# 	raise


# app.debug = True
# if __name__ == '__main__':
# 	app.run(debug = True)
#Because of this final comment, the only way to run the flask app is to `flask run` on cmd
