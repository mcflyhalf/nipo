#Tests for the db model. 
# Particularly testing logical relationships within the model
import pytest
from nipo.db.schema import Student, User, PrivilegeLevel
from nipo.tests.test_attendance import testmod 	#testmod is actually a ModuleAttendance object not a Module object

@pytest.fixture(scope = 'function')
def new_test_stud():
	student_id = 99999
	name = "New Student"
	course_uid = "EPE17"

	yield Student(id=student_id, name=name, course_uid=course_uid)

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

	yield User(**staff) 


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
		module.attachStudent(new_test_stud)
		assert new_test_stud in module.students

	def test_attach_staff_to_module(self, testmod, new_test_staff):
		module = testmod.module
		assert new_test_staff not in module.staff
		module.attachStaff(new_test_staff)
		assert new_test_staff in module.staff

	def test_attach_student_as_staff_to_module(self, testmod, new_test_stud):
		module = testmod.module
		notstaff = new_test_stud
		with pytest.raises(TypeError):
			module.attachStaff(notstaff)

	def test_attach_staff_as_student_to_module(self, testmod, new_test_staff):	
		module = testmod.module
		notstudent = new_test_staff
		with pytest.raises(TypeError):
			module.attachStudent(notstudent)
