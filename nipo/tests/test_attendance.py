import pytest
from nipo.attendance import ModuleAttendance
from nipo.db.schema import Module


module_code = "ETI001"


@pytest.fixture
def testmod():
	return ModuleAttendance(module_code)

# print("On creation, attendance record is \n {}".format(mod.getAttendance()))

# sd = datetime(2019,4,30,10,30)

# mod.createClassSession(sd)

# print("On creation of class session, attendance record is \n {}".format(mod.getAttendance()))

# for studID in range(2,11,2):
# 	mod.updateAttendance(studID, sd, present=True)

# print("After marking some students present, attendance record is \n {}".format(mod.getAttendance()))





class TestModuleAttendance:

	#sd = datetime(2019,4,30,10,30)

	#A couple of tests on the initialiser
	def test_init_existing_module_code(self,testmod):
		assert type(testmod) is ModuleAttendance
		assert type(testmod.module) is Module
		assert testmod.module.code == module_code


	def test_init_non_existing_module_code(self):
		with pytest.raises(ValueError):
			ModuleAttendance("NonExistentModule123")

	def test_CreateAttendance(self):
		pass

	def test_persistAttendance(self):
		pass

	def test_getAttendance(self):
		pass

	def test_createClassSession(self):
		pass

	def test_updateAttendance(self):
		pass