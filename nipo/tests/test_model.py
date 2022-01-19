#Tests for the db model. 
# Particularly testing logical relationships within the model
import pytest
from nipo.conf import test_session as session
from nipo.db.schema import Student, User, PrivilegeLevel
from nipo.tests.test_attendance import testmod 	#testmod is actually a ModuleAttendance object not a Module object

@pytest.fixture(scope = 'function')
def new_test_stud():
	student_id = 99999
	name = "New Student"
	course_uid = "EPE17"
	stud = Student(id=student_id, name=name, course_uid=course_uid)
	session.add(stud)
	session.commit()

	yield stud
	session.delete(stud)
	session.commit()


@pytest.fixture(scope = 'function')
def new_test_staff():
	staff = {}
	staff["id"] = 123321 
	staff["username"] = "newstaff" 
	staff["name"] = "New Staff"
	staff["email"] = "new@staff.com" 
	staff["privilege"] =  PrivilegeLevel.staff.name
	staff["authenticated"] = False 
	staff["active"] = True 
	staff["password_hash"] = "cant_Login"
	staff_user = User(**staff)

	session.add(staff_user)
	session.commit()

	yield staff_user 

	session.delete(staff_user)
	session.commit()

class TestModule:
	'''
	Tests logical functionality of a module on the db
	Currently testing:
	1. Adding students
	2. Adding staff
	'''

	def test_attach_student_to_module(self, testmod, new_test_stud):
		module = testmod.module
		assert new_test_stud not in module.students
		module.attachStudent(new_test_stud, testmod)
		assert new_test_stud in module.students

	def test_attach_staff_to_module(self, testmod, new_test_staff):
		module = testmod.module
		assert new_test_staff not in module.staff
		module.attachStaff(new_test_staff)
		assert new_test_staff in module.staff
		module.staff.remove(new_test_staff) #Should move to some teardown somewhere

	def test_attach_student_as_staff_to_module(self, testmod, new_test_stud):
		module = testmod.module
		notstaff = new_test_stud
		with pytest.raises(TypeError):
			module.attachStaff(notstaff)

	def test_attach_staff_as_student_to_module(self, testmod, new_test_staff):	
		module = testmod.module
		notstudent = new_test_staff
		with pytest.raises(TypeError):
			module.attachStudent(notstudent, testmod)


	# This test is incomplete. Waiting for attachStudent implementation to include attachment to attendance record
	def test_attached_student_has_attendance_record(self, testmod, new_test_stud):
		assert new_test_stud not in testmod.students #check student isnt already in the module
		#Ensure module has an attendance record
		#Not necessary because we are using a real module used in other test fxns

		#confirm this attendance record does not include this student
		attendance_record = testmod.getAttendance()
		assert new_test_stud.id not in attendance_record['Student_ID'].tolist()

		testmod.module.attachStudent(new_test_stud, testmod)

		#Check that after attachment, the attendance record does contain the student
		attendance_record = testmod.getAttendance()
		assert new_test_stud.id in attendance_record['Student_ID'].tolist()

	def test_detached_student_has_no_attendance_record(self, testmod, new_test_stud):
		#Attach student
		testmod.module.attachStudent(new_test_stud, testmod)

		#Check that after attachment, the attendance record does contain the student
		attendance_record = testmod.getAttendance()
		assert new_test_stud.id in attendance_record['Student_ID'].tolist()

		#detach student
		testmod.module.detachStudent(new_test_stud, testmod)
		attendance_record = testmod.getAttendance()
		assert new_test_stud.id not in attendance_record['Student_ID'].tolist()




