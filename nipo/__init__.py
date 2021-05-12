from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import configparser


#create sqlalchemy engine (for actual use), test engine(for testing db connection) and session (only for the engine)

production_engine = create_engine('postgresql://{dbuser}:{passwd}@{host}:{port}/{dbname}'.format(\
	dbuser = os.environ['POSTGRES_USER'] ,
	passwd = os.environ['POSTGRES_PASS'],
	host = 'localhost',
	port = os.environ['POSTGRES_PORT'],
	dbname = os.environ['POSTGRES_NIPO_DBNAME']))

Session = sessionmaker(bind=production_engine)
production_session = Session()

test_engine = create_engine('postgresql://{dbuser}:{passwd}@{host}:{port}/{dbname}'.format(\
	dbuser = os.environ['POSTGRES_USER'] ,
	passwd = os.environ['POSTGRES_PASS'],
	host = 'localhost',
	port = os.environ['POSTGRES_PORT'],
	dbname = os.environ['POSTGRES_NIPO_TEST_DBNAME']),
	echo = False)

TestSession = sessionmaker(bind=test_engine)
test_session = TestSession()
if os.environ['FLASK_ENV'] == 'production':		
	session = production_session
else:
	session = test_session		 


#-------------START FRONTEND API FUNCTIONS--------------#
## These helper functions are used in the frontend mostly
## to get info required by flask templates. Should be moved
## to appropriate location after blueprints implemented.
## Appropriate location is top level blueprint folder.
## I might be wrong though. Choose better location if you
## have grown older and wiser

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
	stud_att = stud.get_module_attendance(modulecode)
	att = stud_att['attendance']
	tot_present = 0
	tot_sesh = len(att)

	if tot_sesh <= 0:
		stud_att['Present_pc'] = 100
		

	else:
		for sesh in att:
			tot_present += int(att[sesh])

		stud_att['Present_pc'] =  int(tot_present/tot_sesh *100)


	stud_att['Absent_pc'] = 100-stud_att['Present_pc']
	return stud_att


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

def recognise_student(session, studentID=None, encoding=None, face_pixels=None):
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
