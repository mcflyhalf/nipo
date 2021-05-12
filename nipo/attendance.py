#Attendance class will do the following:
#->Check whether there is a class (from Google/any other calendar)
#->Mark a particular student present
#->Persist attendance records to db (current strategy is to use python-pandas)
#->Display attendance records for a particular module
#->Display the attendance record for a particular student

#The nipo calendar is here(https://calendar.google.com/calendar/b/1?cid=ODBmc2g3ajllMjg5amYybGJuYThmODk2dDBAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ). It is a Google calendar where when you invite it to any events it is ging to accept given that this event doesnt clash with anything else on its calendar. This will be the default calendar that'll be used for timetabling in this project.

from nipo import get_logger 
from nipo.db.schema import Student, Course, Module
from datetime import datetime
from numpy import uintc
import pandas as pd
import pickle



logger = get_logger("nipo_attendance")

# This class (MarkAttendance) will have functions related to marking attendance. The core function of this class will be to take as input a student id, a module and a date. The class would then mark that student present for that class. The intended strategy to use is to have a multidimensional Python list (to mimic a matrix or excel sheet) where the columns are all the class dates and the rows are the student attendances. Each cell (intersection between row r and column c) is then a binary value representing whether the student r attended the class on the date c.
# This class should also be able to serialise and deserialise this list in order to persist it in the DB as a blob.

# As an aside, the reason why the attendance record is kept as a list and not its own table in the db is for flexibility. We are assuming that we dont know all the dates for all the classes in the future. Some classes may be cancelled and others moved. If the attendance was a table in the DB, it would be very cumbersome, dangerous and complicated to continually edit the table's schema. As a list, it is trivial to add a new "column". In effect we have traded speed for flexibility.

# In future, maybe consider moving to a non relational DB

#Ignore this class for now. I see no use for it. Currently use ModuleAttendance and StudentAttendance. It may be useful in some way in future though
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
	def __init__(self, modulecode, session):
		#Check if the module code exists, if it doesnt, throw an exception.
		#Then check whether the attendance record exists for this module, if not then create it. Otherwise, do nothing
		self.modulecode = str(modulecode)
		self.session=session

		self.module = self.session.query(Module).\
							  filter(Module.code == self.modulecode).\
							  one_or_none()

		if not self.module:
			raise ValueError("The module code >>{}<< does not exist".format(self.modulecode))

		if (not self.module.attendance) or (pickle.loads(self.module.attendance) is None):
			logger.info("Creating and persisting attendance record for module >>{}<<".format(self.module.name))
			attendance_record = self.createAttendance(force=True)
			logger.debug("Created attendance record for module >>{}<< with force option".format(self.module.name))
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
				logger.debug("Skipping creation of attendance for module >>{}<< code >>{}<< since an attendance record already exists. Use Force = True to create attendance record anyway".format(self.module.name, self.module.code))
				return	self.module.attendance   #Do not create any record since one already exists. Instead, return the existing one

		# modulecourse = self.module.course_code
		modulestudents = self.module.students
		student_ids = []

		for student in modulestudents:
			student_ids.append(student.id)

		stud_data = {"Student_ID":pd.Series(student_ids)}
		attendance_sheet = pd.DataFrame(stud_data, dtype=uintc)	#Datatype is C unsigned int (via numpy)
		
		return attendance_sheet

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
		return unpickled_attendance

	def createClassSession(self,sessiondate):
		assert type(sessiondate) is datetime 
		currentAttendance = self.getAttendance()

		if sessiondate in currentAttendance.columns:
			logger.debug("Session not created, date {} already exists in attendance record for {}".format(sessiondate,self.module.name))
			return	#The session already exists

		currentAttendance[sessiondate] = 0

		assert len(currentAttendance[sessiondate]) == len(currentAttendance['Student_ID'])		#TODO: Move this to the test suite
		self.persistAttendance(currentAttendance)

	def updateAttendance(self, studentid, sessiondate, present=False):
		'''Update the attendance record for studentid on the date sessiondate to the status present'''
		assert type(sessiondate) is datetime
		assert type(int(studentid)) is int

		currentAttendance = self.getAttendance()

		existingDate = sessiondate in currentAttendance.columns

		if not existingDate:
			raise ValueError("Provided date has no class session")

		#Here, check that the student with this id is part of this course: can be done in 2 ways: 1. Check that their student id appears in the course attendance list or 2. Check the module course and confirm that the student is in the same course. Option1 is currently being implemented

		if not int(studentid) in currentAttendance["Student_ID"].values:
			raise ValueError("Student with id>>{}<< not registered to module >>{}-{}<<".format(studentid,self.module.code, self.module.name))

		#TODO: Log this action
		if present:
			#Column sessiondate in currentAttendance where the student_ID value is studentid. See https://pandas.pydata.org/docs/user_guide/indexing.html#the-where-method-and-masking
			currentAttendance[sessiondate][currentAttendance.Student_ID == studentid] = 1
		else:
			currentAttendance[sessiondate][currentAttendance.Student_ID == studentid] = 0

		self.persistAttendance(currentAttendance)

	@property
	def students(self):
		'''
		Return a list of students in this module. Limited to max 400 students
		'''
		module_students = self.module.students

		return module_students

	@property
	def dates(self):
		'''Return a list of all dates where module has a session. Returns a list of datetime objects.'''
		current_attendance = self.getAttendance()
		module_dates = current_attendance.columns.to_list()

		module_dates = [date for date in module_dates if type(date) is datetime]
		return module_dates


class StudentAttendance:
	'''
	A class currently primarily for getting the attendance record of an individual student
	'''
	def __init__(self, student_id, session):
		#Check whether the student id exists in the db. 
		try:
			self.student_id = int(student_id)
		except ValueError:
			raise TypeError('Invalid student ID >>{}<<. The student ID must be an integer'.format(student_id) )

		self.session=session

		self.student = session.query(Student).\
							  filter(Student.id == self.student_id).\
							  one_or_none()

		if self.student is None:
			raise ValueError('Invalid student ID >>{}<<. The student ID does not exist'.format(student_id))

		
	def get_module_attendance(self, modulecode):
		'''
		Get attendance of this student for the module with modulecode. 
		:throws ValueError: If modulecode points to a module that doesnt exist.
		'''
		mod_attendance=ModuleAttendance(modulecode,session=self.session)
		mod_attendance_record = mod_attendance.getAttendance()

		stud_att = get_student_attendance(self.student_id, mod_attendance_record)
		logger.debug("Type stud_att is {} and content is:\n {}\n\
			and module concerned is {}"
			.format(type(stud_att), stud_att, modulecode))
		stud_attendance = {}
		stud_attendance['student_name'] = self.student.name
		stud_attendance['student_id'] = self.student.id
		stud_attendance['module_name'] = mod_attendance.module.name
		stud_attendance['module_code'] = mod_attendance.module.code

		#assert len(stud_att) == 1	>> Do this in tests
		att = {str(key):int(stud_att[key].values) for key in stud_att.keys()}
		att.pop('Student_ID')	#This may print out random stud_ID's to stdout

		stud_attendance['attendance'] =  att

		return stud_attendance

		#TODO
	def get_session_attendance(self, modulecode, sessiondate):
		'''
		get a present/absent record for a student for a particular session

		:param modulecode: String with the module code
		:param sessiondate: Datetime object with session date
		'''
		if type(sessiondate) is not datetime:
			raise TypeError("session date must be datetime.\
				Is currently {}".format(type(sessiondate)))

		mod_att = self.get_module_attendance(modulecode)
		try:
			mod_att['attendance'] = mod_att['attendance'][str(sessiondate)]
		except KeyError:
			raise ValueError("No session exists for the date {}".format(str(sessiondate)))
		mod_att['session date'] = str(sessiondate)
		return mod_att
	
	@property
	def modules(self):
		'''
		get all the modules that the student is registered in. Return a list of the module objects.
		'''
		return self.student.modules

	def mark_attendance(self, modulecode, sessiondate, present=False):
		'''Update the attendance record for this student, for module with modulecode on the date sessiondate to the status present'''
		#Mark the attendance of a student in this module on this date.
		#If present is not False, it will be assumed to be True
		#What you will need to do is:
		# 1. confirm that the student and module actually exist		
		# 2. Confirm that the student is registered for the module
		# 3. Check that the date provided already contains a class session(lesson). IF not, raise an error and DO NOT create a new one instead as this opens us up to huge errors in future
		# 4. Iff all these conditions are satisfied, get the attendance record from the db. Do this by creating an instance of ModuleAttendance
		# 5. In this instance of Module Attendance, use the updateAttendance function of the instance to update the student's attendance  
		mod_attendance=ModuleAttendance(modulecode,session=self.session)
		mod_attendance.updateAttendance(self.student_id, sessiondate, present)



def get_student_from_encoding(encoding, session):
	student = session.query(Student).\
							  filter(Student.face_encoding == encoding).\
							  one_or_none()

	return student

def get_student_from_pixels(face_pixels, session):
	face = Face(face_pixels)
	encoding = face.get_encoding()

	return get_student_from_encoding(encoding,session=session)


#We probably want to deprecate this function. We shouldnt be exposing anyone outside this module to pickling
#Modulewide function to get the attendance of a single student given their student id and a module's unpickled attendance
def get_student_attendance(studentid,unpickled_attendance,sessiondate=None):
	#get the attendance record for this module
	assert type(unpickled_attendance) is pd.DataFrame

	if sessiondate is None:
		return unpickled_attendance[unpickled_attendance.Student_ID == studentid]	#Entire record for all sessions

	else:
		return unpickled_attendance[unpickled_attendance.Student_ID == studentid][sessiondate].values		#Were they present or absent on that single session?

#To be moved to testing
if __name__ == "__main__":
	from nipo import session
	mod_code =  "ETI001"
	studid = 4
	session_date = datetime(2029,5,7,10,30)

	sa = StudentAttendance(studid, session)
	ma = sa.get_module_attendance(mod_code)
	sesh_att = sa.get_session_attendance(mod_code, session_date)
	mod_att = ModuleAttendance(mod_code, session)
	dts = mod_att.dates
