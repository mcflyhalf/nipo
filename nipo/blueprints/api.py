import tempfile
from flask import Blueprint, jsonify, request, redirect, url_for
from nipo import attendance
from nipo.forms import add_entity_forms, AttachToModuleIndividualForm, AttachToModuleFileUploadForm,\
AttachToModuleEntireCourseForm, form_endpoints
from nipo.db.utils import add_entity, add_entities, celery_app, attach_individual,\
attach_to_module_from_file_upload, attach_to_module_entire_course
from nipo.conf import UPLOAD_PATH

def capture_upload_file(request, infile_name, upload_file):
	uploaded_data = request.files[infile_name].read()
	
	with open(upload_file.name, 'w') as f:
		f.write(uploaded_data.decode('utf-8'))

bp = Blueprint('api', __name__, url_prefix='')
#Evenutually migrate to this version of api
# bp = Blueprint('api', __name__, url_prefix='/api/v1')

# TODO: Require login (or api token) in sensitive api endpoints

@bp.route('/userdetails')
@login_required
def get_user_details():
	'''Get Student's Name and ID'''
	user_detail = {}
	if current_user.privilege == 'student':
		user_detail['name'] = current_user.name
		user_detail['student_id'] = current_user.student_id
		user_detail['status'] = 0	#TODO: Determine status codes for Nipo

	else:
		#Return a 404 Or sth similar in this case
		user_detail['status'] = 1	#TODO: Determine status codes for Nipo
	
	return jsonify(user_detail)





# Return the modules a student is enrolled in with summary attendance (Dashboard)
@bp.route('/student', methods = ['POST'])
def get_student_attendance():	#For all modules
	studentID = request.form.get('studentID')
	student = attendance.StudentAttendance(studentID,session)
	student_modules = student.modules

	student_attendance = dict()

	#TODO: Include student name and ID in this response

	for module in student_modules:
		student_attendance[module.code] = student.get_module_attendance(module.code)

	return jsonify(student_attendance) 	#TODO: Have this returned by a pretty  dashboard-like template

# Return a list of the modules that a student is taking
@bp.route('/modules', methods = ['POST'])
def get_student_modules():
	return get_student_attendance()

# Return attendance record for the student logged in for the specified module
@bp.route('/module/attendance/mark', methods = ['POST'])
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

		try:
			mod_attendance.updateAttendance(studentID,sess_date, present=status)			
		except ValueError:
			return "The date >>{}<< does not have a class session for the module with code >>{}<<".format(sess_date.isoformat(), modulecode)

		#redirect to show student's attendance for the module. Preserve the POST parameters
		return redirect(url_for('get_student_module_attendance'), code=307)


# Return attendance record for the student logged in for the specified module
@bp.route('/module/attendance', methods = ['POST'])
def get_student_module_attendance():
	req = request.get_json()
	studentID = req['studentID']
	modulecode = req['modulecode']
	isoDate = req['SessionDate']
	sessiondate = datetime.datetime.fromisoformat(isoDate)
	student_attendance = StudentAttendance(studentID, session)
	session_attendance = student_attendance.get_session_attendance(modulecode, sessiondate)
	resp = session_attendance
	return jsonify(resp) 	#TODO: Have this returned by a pretty render_template TODO: MAke the datetime in this response ISO8601 format


# Return attendance for a student for a module 
@bp.route('/student/module', methods = ['POST'])
def get_module_attendance_student():	#Not Yet implemented
	return get_student_module_attendance()

#Return the list of students in a module
@bp.route('/students', methods = ['POST'])
def get_module_students():		#Not Yet implemented. Looks incomplete
	modulecode = request.form.get('modulecode')
	module = attendance.ModuleAttendance(modulecode, session)

	mod_students = module.students

	resp = dict()

	for student in mod_students:
		resp[student.id] = dict()
		resp[student.id]['Name'] = student.name
		
	return jsonify(resp) 	#TODO: Have this returned by a pretty template


#Potentially change to /modify/entity to allow deleting through this route as well
@bp.route('/add/<entity_type>', methods=['POST'])
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
@bp.route('/fadd/<entity_type>', methods=['POST'])
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

@bp.route(form_endpoints['attach_to_module_individual'],methods=['POST'])
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

@bp.route(form_endpoints['attach_to_module_file_upload'],methods=['POST'])
def request_attach_to_module_file_upload():
	form = AttachToModuleFileUploadForm()
	if form.validate_on_submit():
		# Offload to celery functinon
		# Get form data
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
		task_info = attach_to_module_from_file_upload.delay(tmp_file.name)
		response = {}
		response['request-id']= task_info.id
		response['status']= task_info.status
		return jsonify(response)
	return jsonify({'status': 'FAILURE', 
					'info': form.errors})

@bp.route(form_endpoints['attach_to_module_entire_course'],methods=['POST'])
def request_attach_to_module_entire_course():
	form = AttachToModuleEntireCourseForm()
	if form.validate_on_submit():
		# Offload to celery functinon
		# Get form data
		modulecode = form.modulecode.data.upper()
		course_uid = form.course_uid.data.upper()

		task_info = attach_to_module_entire_course.delay(modulecode, course_uid)

		response = {}
		response['request-id']= task_info.id
		response['status']= task_info.status
		return jsonify(response)
	return jsonify({'status': 'FAILURE', 
					'info': form.errors})

#Does this require login??
@bp.route('/status/<task_id>')
def get_task_status(task_id):
	task = celery_app.AsyncResult(task_id)
	response = {}
	response['task-id'] = task_id
	response['status'] = task.status
	response['info'] = str(task.info)
	# if task.status in ["SUCCESS", "FAILURE"]:
	task.forget()
	return jsonify(response)	
