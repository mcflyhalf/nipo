#import Flask and create api functions here
from nipo.attendance import ModuleAttendance
from nipo import attendance, production_session, test_session

session = test_session	#Change to production_session in the production environment. This would then utilise production data(bases) 


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

	return attendance.getStudentAttendance(studentID, unpickled_attendance)

def mark_attendance_student_module(studentID, modulecode):
	pass

def mark_attendance_students_module(studentIDs, modulecode):
	pass

def recognise_student(studentID=None, encoding=None, face_pixels=None):
	pass

def get_student_from_encoding(encoding):
	pass

def get_student_from_face_pixels(face_pixels):
	pass

def get_student_from_ID(studentID):
	pass