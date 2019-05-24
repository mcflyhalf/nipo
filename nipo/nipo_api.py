#import Flask and create api functions here
from nipo.attendance import ModuleAttendance
from nipo import attendance, production_session, test_session, db
from flask import Flask, request, render_template

session = test_session	#Change to production_session in the production environment. This would then utilise production data(bases) 

app = Flask(__name__)

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
	unpickled_attendance = get_attendance_module(modulecode)

	return attendance.get_student_attendance(studentID, unpickled_attendance)

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
def landing():
	'''get Course list and display it using a template'''
	courses = get_course_list(session)
	return render_template('list_courses.html', courses = courses)

under_cons_msg = "OOPS! This part of the website is still under construction"

# Return a list of the modules that a student is taking
@app.route('/modules')
def mishmash1():
	return under_cons_msg

#Not working at the moment
# Return attendance record for the student logged in
@app.route('/module/attendance', methods = ['GET','POST'])
def get_student_module_attendance():
	if request.method == 'POST':
		studentID = request.form.get('studentID')
		modulecode = request.form.get('modulecode')

		student_attendance = get_attendance_student_module(studentID,modulecode)

		return student_attendance 	#TODO: Have this returned by a pretty template
	return under_cons_msg + 'for a Get request'

# Return the modules a student is enrolled in with summary attendance (Dashboard)
@app.route('/student', methods = ['GET','POST'])
def get_student_attendance():	#For all modules
	if request.method == 'POST':
		studentID = request.form.get('studentID')
		student = attendance.StudentAttendance(studentID,session)
		student_modules = student.modules

		student_attendance = dict()

		for module in student_modules:
			student_attendance[module.code] = student.get_module_attendance(module.code)

		return str(student_attendance) 	#TODO: Have this returned by a pretty  dashboard-like template
	return under_cons_msg + 'for a Get request'


# Return attendance for a student for a module 
@app.route('/student/module', methods = ['GET','POST'])
def mishmash4():	#Not Yet implemented
	if request.method == 'POST':
		studentID = request.form.get('studentID')
		modulecode = request.form.get('modulecode')

		student_attendance = get_attendance_student_module(studentID,modulecode)

		return student_attendance 	#TODO: Have this returned by a pretty template
	return under_cons_msg + 'for a Get request'

#Return the list of students in a module
@app.route('/students', methods = ['POST'])
def mishmash5():		#Not Yet implemented
	if request.method == 'POST':
		studentID = request.form.get('studentID')
		modulecode = request.form.get('modulecode')

		student_attendance = get_attendance_student_module(studentID,modulecode)

		return student_attendance 	#TODO: Have this returned by a pretty template
	return under_cons_msg + 'for a Get request'


app.debug = True
if __name__ == '__main__':
	app.run(debug = True)