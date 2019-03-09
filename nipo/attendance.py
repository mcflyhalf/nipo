#Attendance class will do the following:
#->Check whether there is a class (from Google/any other calendar)
#->Mark a particular student present
#->Persist attendance records to db (current strategy is to serialise/pickle a 2D list and store it as a blob in the db)
#->Display attendance records for a particular module
#->Display the attendance record for a particular student

#The nipo calendar is here(https://calendar.google.com/calendar/b/1?cid=ODBmc2g3ajllMjg5amYybGJuYThmODk2dDBAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ). It is a Google calendar where when you invite it to any events it is ging to accept given that this event doesnt clash with anything else on its calendar. This will be the default calendar that'll be used for timetabling in this project.


# This class (MarkAttendance) will have functions related to marking attendance. The core function of this class will be to take as input a student id, a module and a date. The class would then mark that student present for that class. The intended strategy to use is to have a multidimensional Python list (to mimic a matrix or excel sheet) where the columns are all the class dates and the rows are the student attendances. Each cell (intersection between row r and column c) is then a binary value representing whether the student r attended the class on the date c.
# This class should also be able to serialise and deserialise this list in order to persist it in the DB as a blob.

# As an aside, the reason why the attendance record is kept as a list and not its own table in the db is for flexibility. We are assuming that we dont know all the dates for all the classes in the future. Some classes may be cancelled and others moved. If the attendance was a table in the DB, it would be very cumbersome, dangerous and complicated to continually edit the table's schema. As a list, it is trivial to add a new "column". In effect we have traded speed for flexibility.

# In future, maybe consider moving to a non relational DB
class MarkAttendance:
	def __init__(self, studentid, modulecode, moduledate):
		'''Create a single attendance record'''
		pass

	def markpresent(self,timearrived):
		#Make sure to log this action
		pass

	def markabsent(self,timearrived=None):
		#Make sure to log this action
		pass

	def marklate(self,timearrived):
		#Make sure to log this action
		pass

class ModuleAttendance:
	'''A class that manipulates the structure of any module's attendance record (Think of this like creating an attendance sheet for the module and adding students who are registered to this module into that sheet)'''
	def __init__(self, modulecode):
		#Check if the module code exists, si it doesnt, throw an exception.
		#Then check whether the attendance record exists for this module, if not then create it. Otherwise, do nothing
		self.modulecode = modulecode
		pass

	def createattendance(self):
		#Create the first column of the attendance record for this module. The first column is a list of student ID's for all the students registered for this module
		#Make sure to log this action
		pass

	def persistattendance(self,attendancerecord,engine):
		#Pickle the attendance record and persist it to the appropriate table in the engine
		#Make sure to log this action
		pass

	def getattendance(self,engine):
		#get the attendance record for this module
		pass

class StudentAttendance:
	'''A class currently primarily for getting the attendance record of an individual student'''
	def __init__(self, student_id):
		#Check whether the student id exists in the db. 
		self.student_id = student_id

		pass

	def get_attendance:
		pass