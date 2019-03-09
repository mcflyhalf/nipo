from sqlalchemy import Column, String, Integer, DateTime, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
#from sqlalchemy.types import JSON

Base = declarative_base()


#Tutorial for what happens here is found in https://docs.sqlalchemy.org/en/latest/orm/tutorial.html
#See also https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/
#Create Various necessary Tables to be used as tables in the DB. Classes represent tables in the DB and objects will represent rows in these tables. This is how Sqlalchemy and other Python ORM's work
#(Not sure whether these classes should be created here in setup.py or in the base nipo/__init__.py so will list them in both places)

#Create Module class (corresponds to DB table that has a list of modules. We expect that each module will in turn have qualities like start date, end date, class days (are its classes on a Mon, Tue, Wed etc), start time(s), end time(s)(in case of multiple occurences of a module in a week, venue(s), start date, end date(s) and the class that should attend this lesson etc)
#---------------------MODULE TABLE------------------------
#module code | module name | start date | end date |class days | Start time | End time | venue code | 
#TODO: Remove start/end date/time from this class. These options will then be fetched from Google Calendar so that they can be changed and moved around flexibly
class Module(Base):
	__tablename__ = "module"

	code = Column(String, primary_key=True)
	name = Column(String, nullable=False)
	start_date = Column(DateTime(), nullable = False)
	end_date =  Column(DateTime(), nullable = False)
	start_time =  Column(DateTime(), nullable = False)
	end_time = Column(DateTime(), nullable = False)
	class_days = Column(String(7))
	venue_code = Column(String, ForeignKey("venue.code"))	#Relate this to the venue pri key see https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/
	course_code = Column(String, ForeignKey("course.uid"))
	venues = relationship("Venue", uselist=False)
	courses = relationship("Course") 



#Student Class. Represents an individual student. Should have properties like a UID, Class tht they belong to (Form 1, Form 2, Engineering y1, CS y3 etc), location of their picture (to be used to recognise them)
#-----------------------STUDENT TABLE--------------------
#Student ID | Student Name | Student Course UID| 
class Student(Base):
	__tablename__ = "student"

	id = Column(Integer, primary_key=True)
	name = Column(String,nullable=False)
	course_uid = Column(String, ForeignKey("course.uid"), nullable=False)		#Relate to the course UID
	course = relationship("Course", uselist=False)





#Course Class. A course is like (Form 1, Form 2, Engineering y1, CS y3 etc). Calling this a class which is more natural would be confused with the programming Class structure. Consider referring to it as a course. A class has a UID, modules and Name only. Also, each student belongs to at least(usually only) one class
#-----------------------COURSE TABLE-------------------------
#Course UID | Course Name | Course Modules

class Course(Base):
	__tablename__ = "course"

	uid = Column(String, primary_key=True)
	name = Column(String, nullable=False)
	


#Venues table. The table that holds properties of the venues where classes may be held. 
#---------------------------VENUES TABLE----------------------
#Venue Code | Venue Name | Venue capacity
class Venue(Base):
	__tablename__ = "venue"

	code = Column(String, primary_key=True)
	name = Column(String)
	capacity = Column(Integer)


#These are all the tables I can currently think of