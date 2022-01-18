from sqlalchemy import Column, String, Integer, DateTime, LargeBinary, MetaData, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
import enum
#from sqlalchemy.types import JSON

# For associating instructors to modules, we need a many-to-many r/shp.
# See resources below for how to make this. None of these was sufficient
# https://hackingandslacking.com/managing-relationships-in-sqlalchemy-data-models-effe9d1c8975
# https://www.michaelcho.me/article/many-to-many-relationships-in-sqlalchemy-models-flask
# https://prog.world/sqlalchemy-many-to-many/

Base = declarative_base()

#Tutorial for what happens here is found in https://docs.sqlalchemy.org/en/latest/orm/tutorial.html
#See also https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/
#Create Various necessary Tables to be used as tables in the DB. Classes represent tables in the DB and objects will represent rows in these tables. This is how Sqlalchemy and other Python ORM's work

#For details about all the column types supported by sqlite, see https://docs.sqlalchemy.org/en/latest/core/type_basics.html

class StudentModule(Base):
	'''
	m2m r/shp between students and modules
	Represents the modules that a student is a part of.
	'''
	__tablename__ = "student_module"

	id = Column(Integer, primary_key=True)
	student_id = Column(Integer, ForeignKey("student.id"))
	module_code = Column(String, ForeignKey("module.code"))



class UserModule(Base):
	'''
	M2m relationship between staff users and modules
	All admin users should automatically be a part of all modules
	'''
	__tablename__ = "user_module"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("user.id"))
	module_code = Column(String, ForeignKey("module.code"))


#Create Module class (corresponds to DB table that has a list of modules. We expect that each module will in turn have qualities like start date, end date, class days (are its classes on a Mon, Tue, Wed etc), start time(s), end time(s)(in case of multiple occurences of a module in a week, venue(s), start date, end date(s) and the class that should attend this lesson etc)
#---------------------MODULE TABLE------------------------
#module code | module name | venue code | Course code| Attendance 
class Module(Base):
	__tablename__ = "module"

	# Constrain module code to contain only upper case letters (it may also contain digits)
	code = Column(String, primary_key=True)
	name = Column(String, nullable=False)
	venue_code = Column(String, ForeignKey("venue.code"))	#Relate this to the venue pri key see https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/
	course_code = Column(String, ForeignKey("course.uid"))
	attendance = Column(LargeBinary)
	venues = relationship("Venue", uselist=False)
	courses = relationship("Course")

	students = relationship("Student", secondary=StudentModule.__tablename__, backref="modules")
	staff = relationship("User", secondary=UserModule.__tablename__, backref="modules")

	def _attachStaffObj(self, staffUserObj):
		'''
		Fxn checks for the type of the user before adding them as staff
		'''
		if type(staffUserObj) is not User:
			raise TypeError("Staff to be added to module must be of type {}.\
				Attempted to add object of type {}".format("User", type(staffUserObj)))

		if staffUserObj.privilege != PrivilegeLevel.staff.name:
			raise TypeError("User being added as staff must be staff member.\
				Their privilege level is listed as {}".format(staffUserObj.privilege))

		self.staff.append(staffUserObj)

	def _attachStudentObj(self, studentObj):
		'''
		Fxn checks to confirm object is a student before adding them to module
		'''
		if type(studentObj) is not Student:
			raise TypeError("Student to be added to module must be of type {}.\
				Attempted to add object of type {}".format("Student", type(studentObj)))

		self.students.append(studentObj)
		# Add student to module attendance record
		# Unable to figure out where to plce this code at the moment
 


	def attachStaff(self, staffUser):
		'''
		Attach staff member(s) to a module
		:param staffUser: User object (or list of User objects) containing staff members

		:throws TypeError: If staffUser is not actually of type User or does not have staff privilege
		'''
		if type(staffUser) is list:
			#Iterate over the list instead of using list.extend in order to check each object in turn for type correctness
			assert len(staffUser) > 0
			for su in staffUser:
				self._attachStaffObj(su)
		else:
			self._attachStaffObj(staffUser)

	def attachStudent(self, student):
		'''
		Attach student(s) to a module
		:param student: Student object (or list of Student objects) containing students

		:throws TypeError: If student is not actually of type Student
		'''
		if type(student) is list:
			#Iterate over the list instead of using list.extend in order to check each object in turn for type correctness
			assert len(student) > 0
			for stud in student:
				self._attachStudentObj(stud)
		else:
			self._attachStudentObj(student)

	def __repr__(self):
		return "Module {} held at {}".format(self.name, self.venue_code)

	#In the module class, the attendance column could also have been of type sqlalchemy.types.PickledType and that would have sqlalchemy take care of all the pickling for us but I wanted to get a chance to use/understand pickling so I use a blob type and do the pickling and unpickling myself 




#Student Class. Represents an individual student. Should have properties like a UID, Class tht they belong to (Form 1, Form 2, Engineering y1, CS y3 etc), location of their picture (to be used to recognise them)
#-----------------------STUDENT TABLE--------------------
#Student ID | Student Name | Student Course UID| 
class Student(Base):
	__tablename__ = "student"

	id = Column(Integer, primary_key=True)
	name = Column(String,nullable=False)
	course_uid = Column(String, ForeignKey("course.uid"), nullable=False)	#Relate to the course UID
	course = relationship("Course", uselist=False)

	#modules = This exists because of backref relationship in Modules table 


	def __repr__(self):
		return "Student >>{}<< ".format(self.name)





#Course Class. A course is like (Form 1, Form 2, Engineering y1, CS y3 etc). Calling this a class, which is more natural, would be confused with the programming Class structure. Consider referring to it as a course. A course has a UID, modules and Name only. Also, each student belongs to at least(usually only) one course
#-----------------------COURSE TABLE-------------------------
#Course UID | Course Name | Course Modules

class Course(Base):
	__tablename__ = "course"

	uid = Column(String, primary_key=True)
	name = Column(String, nullable=False)


	def __repr__(self):
		return "The Course {}".format(self.name)
	


#Venues table. The table that holds properties of the venues where classes may be held. 
#---------------------------VENUES TABLE----------------------
#Venue Code | Venue Name | Venue capacity
class Venue(Base):
	__tablename__ = "venue"

	code = Column(String, primary_key=True)
	name = Column(String)
	capacity = Column(Integer)


	def __repr__(self):
		return "The venue {}. It can hold {} students".format(self.name, self .capacity)



#Privilege leves are an enum that will be used in the user table

class PrivilegeLevel(enum.Enum):
	student = 0
	staff = 1
	admin = 2

#User table. This is the users of the system (who don't necessarily need to be students). These would be administrators and people who actually mark attendance. Students would be users who can only check their attendance and can't modify it.
#It was a mistake to name this table user since, that is a reserved word in psql (I did not know this at the time of creation). It can still work but is not recommended. The only work-around I can think of is to change the table-name (to users) but there is currently no capacity for that so will do that later.
#------------------------USER TABLE----------------------------
class User(Base):
	#This is a tricky tablename to use. In psql, when you attempt SELECT * from user; , it gives you the current username. Remember to SELECT * FROM public.user instead or SELECT * from 'user';
	__tablename__ = "user"

	#Think of a way to link a user to a student
	id = Column(Integer, primary_key=True)
	username =  Column(String(20),nullable=False,unique=True)	#Always Lowercase
	name = Column(String,nullable=False)
	email = Column(String(50),nullable=False)
	privilege = Column(String(15), Enum(PrivilegeLevel, validate_strings=True, default=PrivilegeLevel.student))#Must be enum student,staff, admin
	authenticated = Column(Boolean, nullable=False)
	active = Column(Boolean, nullable=False)
	# Below(modules) Only relevant for staff members. Students get their list of modules from the student table
	#modules = This exists because of backref relationship in Modules table 	
	student_id = Column(Integer, ForeignKey("student.id"),nullable=True)		#This is going to be null when the user is not a student but has a Student.id foreign key constraint otherwise
	password_hash = Column(String, nullable=False)

	annonymous = False

	def __repr__(self):
		return "Nipo user=> username: >>{}<<, Name: >>{}<<, email >>{}<<, user type >>{}<< ".\
		format(self.username, self.name, self.email, self.privilege)

# See comment at https://realpython.com/using-flask-login-for-user-management-with-flask/ about login and logout
	def is_authenticated(self):
		return self.authenticated

	def is_active(self):
		return self.active

	def is_annonymous(self):
		return self.annonymous

	def check_password(self,password):
		self.authenticated = check_password_hash(self.password_hash, str(password))
		return self.is_authenticated()

	def get_id(self):
		return str(self.id)

	def set_password(self,raw_password):
		self.password_hash = generate_password_hash(str(raw_password))

#These are all the tables I can currently think of
