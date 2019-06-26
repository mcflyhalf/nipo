from sqlalchemy import Column, String, Integer, DateTime, LargeBinary, MetaData, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import enum
#from sqlalchemy.types import JSON

Base = declarative_base()





#Tutorial for what happens here is found in https://docs.sqlalchemy.org/en/latest/orm/tutorial.html
#See also https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/
#Create Various necessary Tables to be used as tables in the DB. Classes represent tables in the DB and objects will represent rows in these tables. This is how Sqlalchemy and other Python ORM's work

#For details about all the column types supported by sqlite, see https://docs.sqlalchemy.org/en/latest/core/type_basics.html

#Create Module class (corresponds to DB table that has a list of modules. We expect that each module will in turn have qualities like start date, end date, class days (are its classes on a Mon, Tue, Wed etc), start time(s), end time(s)(in case of multiple occurences of a module in a week, venue(s), start date, end date(s) and the class that should attend this lesson etc)
#---------------------MODULE TABLE------------------------
#module code | module name | venue code | Course code| Attendance 
class Module(Base):
	__tablename__ = "module"

	code = Column(String, primary_key=True)
	name = Column(String, nullable=False)
	venue_code = Column(String, ForeignKey("venue.code"))	#Relate this to the venue pri key see https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/
	course_code = Column(String, ForeignKey("course.uid"))
	attendance = Column(LargeBinary)
	venues = relationship("Venue", uselist=False)
	courses = relationship("Course")

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

	face_encoding = Column(LargeBinary)


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
#------------------------USER TABLE----------------------------
class User(Base):
	__tablename__ = "user"
	#Think of a way to link a user to a student
	id = Column(Integer, primary_key=True, nullable=True)
	username =  Column(String(20),nullable=False,unique=True)	#Always Lowercase
	email = Column(String(50),nullable=False)
	privilege = Column(String(15), Enum(PrivilegeLevel, validate_strings=True, default=PrivilegeLevel.student))#Must be enum student,staff, admin
	password_hash = Column(String, nullable=False)
	student_id = Column(Integer, ForeignKey("student.id"),nullable=True)		#This is going to be null when the user is not a student but has a Student.id foreign key constraint otherwise
	is_authenticated = True
	is_active = True
	is_annonymous = False




	def check_password(self,password):
		cred_check = False
		cred_check = check_password_hash(self.password_hash, str(password))
		return cred_check

	def get_id(self):
		return str(self.id)

	def set_password(self,raw_password):
		self.password_hash = generate_password_hash(str(raw_password))

#These are all the tables I can currently think of


