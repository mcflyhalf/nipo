#Attendance class will do the following:
#->Check whether there is a class (from Google/any other calendar)
#->Mark a particular student present
#->Persist attendance records to db (current strategy is to serialise/pickle a 2D list and store it as a blob in the db)
#->Display attendance records for a particular module
#->Display the attendance record for a particular student

#The nipo calendar is here(https://calendar.google.com/calendar/b/1?cid=ODBmc2g3ajllMjg5amYybGJuYThmODk2dDBAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ). It is a Google calendar where when you invite it to any events it is ging to accept given that this event doesnt clash with anything else on its calendar. This will be the default calendar that'll be used for timetabling in this project.

from nipo import get_logger, test_session 
from nipo.db.schema import Student, Course, Module
from datetime import datetime
import pickle



logger = get_logger("nipo_attendance")

# This class (MarkAttendance) will have functions related to marking attendance. The core function of this class will be to take as input a student id, a module and a date. The class would then mark that student present for that class. The intended strategy to use is to have a multidimensional Python list (to mimic a matrix or excel sheet) where the columns are all the class dates and the rows are the student attendances. Each cell (intersection between row r and column c) is then a binary value representing whether the student r attended the class on the date c.
# This class should also be able to serialise and deserialise this list in order to persist it in the DB as a blob.

# As an aside, the reason why the attendance record is kept as a list and not its own table in the db is for flexibility. We are assuming that we dont know all the dates for all the classes in the future. Some classes may be cancelled and others moved. If the attendance was a table in the DB, it would be very cumbersome, dangerous and complicated to continually edit the table's schema. As a list, it is trivial to add a new "column". In effect we have traded speed for flexibility.

# In future, maybe consider moving to a non relational DB

#Ignore this class for now. I ee no use for it. Currently use ModuleAttendance and StudentAttendance. It may be useful in some way in future though
class MarkAttendance:
	def __init__(self, studentid, modulecode, moduledate):
		'''Create a single attendance record for a student in a module'''
		pass

	def markPresent(self,timearrived):
		#Make sure to log this action
		pass

	def markAbsent(self,timearrived=None):
		#Make sure to log this action
		pass

	def markLate(self,timearrived):
		#Make sure to log this action
		pass

class ModuleAttendance:
	'''A class that manipulates the structure of any module's attendance record (Think of this like creating an attendance sheet for the module and adding students who are registered to this module into that sheet)'''
	def __init__(self, modulecode, session=test_session):
		#Check if the module code exists, if it doesnt, throw an exception.
		#Then check whether the attendance record exists for this module, if not then create it. Otherwise, do nothing
		self.modulecode = str(modulecode)
		self.session=session

		self.module = session.query(Module).\
							  filter(Module.code == self.modulecode).\
							  one_or_none()

		if not self.module:
			raise ValueError("The module code >>{}<< does not exist".format(self.modulecode))

		if not self.module.attendance:
			logger.info("Creating and persisting attendance record for module >>{}<<".format(self.module.name))
			attendance_record = self.createAttendance()
			logger.debug("Created attendance record for module >>{}<<".format(self.module.name))
			self.persistAttendance(attendance_record)
			logger.debug("Persisted attendance record for module >>{}<<".format(self.module.name))
			logger.info("Created and persisted attendance record for module >>{}<<".format(self.module.name))

	#This function breaks if a module is attached to more than one course e.g if maths2 is done by both TIE and EMT. To be fixed in version 3
	def createAttendance(self, force=False):
		#Create the first column of the attendance record for this module. The first column is a list of student ID's for all the students registered for this module
		#Unless specified to force create attendance, do not do anything if module already contains an attendance record
		#Make sure to log this action

		if not force:
			if self.module.attendance:
				logger.debug("Skipping creation of attendance for module >>{}<< code >>{}<< since an attendance record already exist. Use Force = True to create attendance record anyway".format(self.module.name, self.module.code))
				return	self.module.attendance   #Do not create any record since one already exists. Instead, return the existing one

		modulecourse = self.module.course_code
		modulestudents = self.session.query(Student).filter(Student.course_uid == modulecourse)
		attendance_list = []
		attendance_list.append(list())
		attendance_list[0].append("Dates\\Student ID's")
		for student in modulestudents:
			attendance_list[0].append(student.id)
		
		return attendance_list

	def persistAttendance(self,attendancerecord):
		#Pickle the attendance record and persist it to the appropriate table in the db using the session provided
		#Make sure to log this action
		logger.debug("Pickling module >>{}<< attendance record".format(self.module.name))
		pickled_attendance = pickle.dumps(attendancerecord)
		logger.debug("Module >>{}<< attendance record sucessfully pickled".format(self.module.name))
		self.module.attendance = pickled_attendance
		logger.debug("Successfully attached attendance record to module >>{}<<".format(self.module.name))
		self.session.add(self.module)
		self.session.commit()
		logger.info("Attendance for module >>{}<< updated".format(self.module.name))

	def getAttendance(self):
		#get the attendance record for this module
		pickled_attendance = self.module.attendance
		unpickled_attendance = pickle.loads(pickled_attendance)
		assert type(unpickled_attendance) is list
		return unpickled_attendance

	def createClassSession(self,sessiondate):
		assert type(sessiondate) is datetime 
		currentAttendance = self.getAttendance()

		for record in currentAttendance:
			if record[0] == sessiondate:
				logger.debug("Session not created, date {} already exists in attendance record for {}".format(sessiondate,self.module.name))
				return	#The session already exists

		currentAttendance.append(list())
		currentAttendance[-1].append(sessiondate)

		for cnt in range(len(currentAttendance[0])):
			currentAttendance[-1].append(0)

		self.persistAttendance(currentAttendance)

	def updateAttendance(self, studentid, sessiondate, present=False):
		'''Update the attendance record for studentid on the date sessiondate to the status present'''
		assert type(sessiondate) is datetime
		currentAttendance = self.getAttendance()

		existingDate = False
		for record in currentAttendance:
			if record[0] == sessiondate:
				existingDate = True
				dateindex = currentAttendance.index(record)
				break

		if not existingDate:
			raise ValueError("Provided date has no class session")

		#Here, check that the student with this id is part of this course: can be done in 2 ways: 1. Check that their student id appears in the coure attendance list or 2. Check the module course and confirm that the student is in the same course. Option1 is currently being implemented

		if not studentid in currentAttendance[0]:
			raise ValueError("Student with id>>{}<< not registered to module >>{}<<".format(studentid, self.module.name))

		studindex = currentAttendance[0].index(studentid)
		if present:
			currentAttendance[dateindex][studindex] = 1
		else:
			currentAttendance[dateindex][studindex] = 0

		self.persistAttendance(currentAttendance)

class StudentAttendance:
	'''A class currently primarily for getting the attendance record of an individual student'''
	def __init__(self, student_id, session=test_session):
		#Check whether the student id exists in the db. 
		self.student_id = student_id


		pass

	def get_attendance(self):
		#Get all modules that the student is a part of then get their attendance in each of them. IF you can create the function mark_attendance, this will be simple
		pass

	def mark_attendance(self, modulecode, moduledate, present=False):
		#Mark the attendance of a student in this module on this date
		#What you will need ot do is:
		# 1. confirm that the student and module actually exist		
		# 2. Confirm that the student is registered for the module
		# 3. Check that the date provided already contains a class session(lesson). IF not, raise an error and DO NOT create a new one instead as this opens us up to huge errors in future
		# 4. Iff all these conditions are satisfied, get the attendance record from the db. Do this by creating an instance of ModuleAttendance
		# 5. In this instance of Module Attendance, use the updateAttendance function of the instance to update the student's attendance  
		pass



#From here onwards, these are tests to check that the stuff here works. They will be transferred to proper test classes later
if __name__ == "__main__":
	module_code = "ETI001"
	student_id = 6
	mod = ModuleAttendance(module_code)

	print("On creation, attendance record is \n {}".format(mod.getAttendance()))

	sd = datetime(2029,4,30,10,30)

	mod.createClassSession(sd)

	print("On creation of class session, attendance record is \n {}".format(mod.getAttendance()))

	for studID in range(2,11,2):
		mod.updateAttendance(studID, sd, present=True)

	print("After marking some students present, attendance record is \n {}".format(mod.getAttendance()))



