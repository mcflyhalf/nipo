import pytest
from nipo import test_session
from nipo.attendance import ModuleAttendance, StudentAttendance, get_student_attendance
from nipo.db.schema import Module
from nipo.tests.populate import sd as test_date
import pandas as pd
import random


module_code = ["ETI001","ETI002","ETI003","ETI004","ETI005"]

@pytest.fixture(scope = 'function')
def test_stud_id():
	return random.randint(1,10)

@pytest.fixture(scope = 'function')
def testmod():
	return ModuleAttendance(random.choice(module_code), test_session)

@pytest.fixture
def test_stud_att():
	return StudentAttendance(test_stud_id)

class TestModuleAttendance:

	#Tests on the initialiser
	def test_init_existing_module_code(self,testmod):
		print (type(testmod))
		assert type(testmod) is ModuleAttendance
		assert type(testmod.module) is Module
		assert testmod.module.code in module_code


	def test_init_non_existing_module_code(self):
		with pytest.raises(ValueError):
			ModuleAttendance("NonExistentModule123",test_session)

	def test_CreateAttendance(self,test_stud_id,testmod):
		test_attendance = testmod.createAttendance(force=True) 
		assert type(test_attendance) is pd.DataFrame
		assert 'Student_ID' in test_attendance.columns
		assert test_stud_id in test_attendance.Student_ID.values

	def test_persistAttendance(self):
		pass

	def test_getAttendance(self,test_stud_id, testmod):
		unpickled_attendance = testmod.getAttendance()
		assert type(unpickled_attendance) is pd.DataFrame
		assert 'Student_ID' in unpickled_attendance.columns
		assert test_stud_id in unpickled_attendance.Student_ID.values


	def test_createClassSession(self):
		pass

	def test_updateAttendance(self,test_stud_id,testmod):
		present = True
		testmod.createClassSession(test_date)
		testmod.updateAttendance(test_stud_id, test_date, present)
		assert get_student_attendance(test_stud_id,testmod.getAttendance(), sessiondate=test_date) == True

		present = False
		testmod.updateAttendance(test_stud_id, test_date, present)
		assert get_student_attendance(test_stud_id,testmod.getAttendance(),sessiondate= test_date) == False

class TestStudentAttendance:

	def test_get_module_attendance(self):
		pass


	def test_get_session_attendance(self):
		pass


	def test_mark_attendance(self):
		pass






		
