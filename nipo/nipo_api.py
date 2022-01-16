import datetime
import tempfile
import os
from nipo.attendance import ModuleAttendance, StudentAttendance
from nipo import attendance, db
from nipo.conf import session
from flask import Flask, flash, request, render_template, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from nipo.db import schema
from nipo.db.utils import get_student_list, get_module_list, get_course_list, add_entity, add_entities,\
celery_app, attach_individual
# from nipo.task_mgr import celery_app 
from nipo.forms import LoginForm, RegistrationForm, AddCourseForm, AddVenueForm, AddUserForm, AddStudentForm, AddModuleForm, BulkAddForm,\
AttachToModuleIndividualForm, AttachToModuleFileUploadForm, AttachToModuleEntireCourseForm, form_endpoints, attach_to_module_forms,\
add_entity_forms
import random
import time


app = Flask(__name__)
# celery_app = get_celery_app()
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.config['db_session'] = session #iss this ever used?
#TODO: Modify app config to expire sessions after a day 
#See https://stackoverflow.com/questions/11783025/is-there-an-easy-way-to-make-sessions-timeout-in-flask
#Max upload size = 100 kB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 
login_manager = LoginManager(app)
login_manager.init_app(app)

login_manager.login_view = 'login'
UPLOAD_PATH = os.path.join(tempfile.gettempdir(), "nipo")

@login_manager.user_loader
def load_user(user_id):
    return session.query(schema.User).filter(schema.User.id==int(user_id)).one_or_none()

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.close()

def make_form_dict():
	form = {}
	form['course'] = AddCourseForm()
	form['venue'] = AddVenueForm()
	form['user'] = AddUserForm()
	form['student'] = AddStudentForm()
	form['module'] = AddModuleForm()
	form['file_upload'] = BulkAddForm()
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
		#Use query strings to pass name of module in url and refresh whenever module is changed
		#The refreshed page will contain dates of the selected module (from query string)
		#Remember to check that staff member has access to module.
		#Optionally, use post request and have javascript refresh the page (too much work!!!)
		#TODO: For each module, only show valid dates. Nipo challenge?
		modules = current_user.modules
		dates = []
		formatted_dates = []
		
		mod_code = request.args.get('mod_code')
		session_date = request.args.get('session_date')
		#Each of the options below needs to set:
		# 1. selectedModule
		# 2. dates
		# 3. selectedDate
		if mod_code is not None and session_date is None:
			# module changed
			mod_attendance = ModuleAttendance(mod_code, session)
			selectedModule = mod_attendance.module
			if selectedModule not in current_user.modules:
				# User not enrolled in this module
				flash("Invalid module selection")
				return redirect(url_for('landing'))

			dates += mod_attendance.dates
			if len(dates) == 0:
				flash("selected module has no registered class sessions")
				return redirect(url_for('landing'))
			selectedDate = dates[0]

		elif mod_code is not None and session_date is not None:
			# Date changed
			mod_attendance = ModuleAttendance(mod_code, session)
			selectedModule = mod_attendance.module
			dates += mod_attendance.dates
			selectedDate = datetime.datetime.fromisoformat(session_date)
			if selectedModule not in current_user.modules or selectedDate not in dates:
				# User not enrolled in this module or module has no session on this date
				flash("Invalid module or date selection")
				return redirect(url_for('landing'))

		else:
			#Default scenario, fresh login
			if len(modules) == 0:
				flash("You are currently not assigned to any modules. Contact admin to correct this. Showing dummy module.")
				# TODO: Create test module for showing when 
				# staff is not assigned to any modules
				# modules = [test_module]
				modules = get_module_list(session)

			selectedModule = modules[0]
			dates += ModuleAttendance(selectedModule.code, session).dates
			selectedDate = dates[0]
		
		#move selected options to the top of list to make them 
		#the ones selected by default
		if selectedDate != dates[0]:
			dates.remove(selectedDate)
			dates.insert(0, selectedDate)
		
		if selectedModule != modules[0]:
			modules.remove(selectedModule)
			modules.insert(0, selectedModule)
		# raise
		for date in dates:
			human_friendly_format = date.strftime('%a %d %b %H:%M')
			iso_format = date.strftime('%Y-%m-%dT%H:%M')
			combined_format = {"human friendly format": human_friendly_format,
								"iso format": iso_format}

			formatted_dates.append(combined_format)

		students = selectedModule.students
		for student in students:
			student_attendance = StudentAttendance(student.id, session)
			session_attendance = student_attendance.get_session_attendance(selectedModule.code, selectedDate)

			if session_attendance['attendance']:
				student.status= "student-present"
			else:
				student.status= "student-absent"

		return render_template('staff_dashboard.html',\
								dates=formatted_dates,students=students,modules=modules)

	elif current_user.privilege == schema.PrivilegeLevel.admin.name:
		tables = db.utils.get_tables_data(session)
		return render_template('admin_dashboard/admin_dashboard.html',\
								tables=tables, form=add_entity_forms(), attach_to_module_forms=attach_to_module_forms())

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
#Will only be corrected if some academic institution is interested
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
	flash("registration page is disabled. Contact admin")
	return redirect(url_for('login'))
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
@app.route('/module/attendance/mark', methods = ['POST'])
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


# Return attendance record for the student logged in for the specified module
@app.route('/module/attendance', methods = ['GET','POST'])
def get_student_module_attendance():
	if request.method == 'POST':
		req = request.get_json()
		studentID = req['studentID']
		modulecode = req['modulecode']
		isoDate = req['SessionDate']
		sessiondate = datetime.datetime.fromisoformat(isoDate)
		student_attendance = StudentAttendance(studentID, session)
		session_attendance = student_attendance.get_session_attendance(modulecode, sessiondate)
		resp = session_attendance

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


#Potentially change to /modify/entity to allow deleting through this route as well
@app.route('/add/<entity_type>', methods=['POST'])
def request_add_entity(entity_type):
	all_add_entity_forms =add_entity_forms()
	form = all_add_entity_forms[entity_type.lower()]
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

#Bulk add entities using a file
@app.route('/fadd/<entity_type>', methods=['POST'])
def request_bulk_add_entities_via_file(entity_type):
	all_add_entity_forms =add_entity_forms()
	form = all_add_entity_forms['file_upload']
	if form.validate_on_submit():
		uploaded_data = request.files[form.csv.name].read()
		if not os.path.exists(UPLOAD_PATH):
			os.makedirs(UPLOAD_PATH)
		tmp_file = tempfile.NamedTemporaryFile(
									suffix='.csv',
									prefix='nipo_fupload_',
									dir=UPLOAD_PATH,
									delete=False)
		with open(tmp_file.name, 'w') as f:
			f.write(uploaded_data.decode('utf-8'))
		#Confirm that stuff is actually written to the temp file
		# raise
		task_info = add_entities.delay(entity_type, tmp_file.name)
		response = {}
		response['request-id']= task_info.id
		response['status']= task_info.status
		return jsonify(response)
	return jsonify({'status':'FAILURE', 
					'info':'Invalid file format'})

@app.route(form_endpoints['attach_to_module_individual'],methods=['POST'])
def request_attach_to_module_individual():
	form = AttachToModuleIndividualForm()
	if form.validate_on_submit():
		# Offload to celery functinon
		# Get form data
		designation = form.designation.data.lower()
		modulecode = form.modulecode.data.upper()
		emailOrId = form.emailOrId.data.lower()

		# Celery func
		task_info = attach_individual.delay(designation,modulecode,emailOrId)
		response = {}
		response['request-id']= task_info.id
		response['status']= task_info.status
		return jsonify(response)
	return jsonify({'status': 'FAILURE', 
					'info': form.errors})

@app.route(form_endpoints['attach_to_module_file_upload'],methods=['POST'])
def request_attach_to_module_file_upload():
	form = AttachToModuleFileUploadForm()
	if form.validate_on_submit():
		# Offload to celery functinon
		# Get form data

		# Celery func

		return jsonify(response)
	return jsonify({'status': 'FAILURE', 
					'info': 'Include Form.errors here'})

@app.route(form_endpoints['attach_to_module_entire_course'],methods=['POST'])
def request_attach_to_module_entire_course():
	form = AttachToModuleEntireCourseForm()
	if form.validate_on_submit():
		# Offload to celery functinon
		# Get form data

		# Celery func

		return jsonify(response)
	return jsonify({'status': 'FAILURE', 
					'info': 'Include Form.errors here'})



#Does this require login??
@app.route('/status/<task_id>')
def get_task_status(task_id):
	task = celery_app.AsyncResult(task_id)
	response = {}
	response['task-id'] = task_id
	response['status'] = task.status
	response['info'] = str(task.info)
	# if task.status in ["SUCCESS", "FAILURE"]:
	task.forget()
	return jsonify(response)	

# @app.route('/debug', methods = ['GET','POST'])
# def get_debugger():
# 	raise 