#This file will eventually be removed. It is here to test functionality that interfaces with objects that havent been created or functionality that requires a populated DB (for this we use nipo_test which is a mirror of nipo but whose contents are used for testing purposes)

#Documentation for creating an instance of the mapped classes is very well done at https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#create-an-instance-of-the-mapped-class

from nipo import test_session, get_logger
from nipo.db.schema import Module, Student, Course, Venue, User, PrivilegeLevel
from nipo.attendance import ModuleAttendance, get_student_attendance
from datetime import datetime
import random

logger = get_logger("nipo_populate")
session = test_session
session_engine = session.get_bind()
conn_details = session_engine.url
sd = [datetime(2029,4,30,10,30)]
sd.append(datetime(2029,5,7,10,30))
sd.append(datetime(2029,5,8,10,30))
sd.append(datetime(2029,5,9,10,30))
sd.append(datetime(2029,5,10,10,30))
sd.append(datetime(2029,5,11,10,30))

def populate_testdb():
	'''Populate the test db with test info'''
	logger.info("Populating DB >>{}<< with dummy data for integration testing".format(conn_details))
	venue1 = Venue(code = "H7009", name = "Hall 7 Rm 9", capacity = 20)
	venue2 = Venue(code = "EMB101", name = "Eng Main Building 101" , capacity = 30)
	venue3 = Venue(code = "4A", name = "Form 4A", capacity = 60)
	venue4 = Venue(code = "SHAC", name = "Shirrin Aumreedy-Cziffra" , capacity = 35 )
	venue5 = Venue(code = "PLMM", name = "Patrice Lumumba" , capacity = 40)

	venues = [venue1, venue2, venue3, venue4, venue5]

	course1 = Course(uid = "TIE18", name = "Telecommunications and Information Engineering 2018")
	course2 = Course(uid = "EMT18", name = "Mechatronic Engineering 2018")
	course3 = Course(uid = "EPE17", name = "Electrical Power Systems Engineering 2018")
	course4 = Course(uid = "CSS17", name = "Computer Science 2018")



	courses = [course1, course2, course3, course4]

	student1 = Student(name = "Amondi Auma", course_uid ="TIE18" )
	student2 = Student(name = "Bob Bwanda", course_uid ="TIE18" )
	student3 = Student(name = "Chumo Chacha", course_uid ="TIE18" )
	student4 = Student(name = "Donde Dibala", course_uid ="TIE18" )
	student5 = Student(name = "Emali Ekoi", course_uid ="TIE18" )
	student6 = Student(name = "Faraja Faulu", course_uid ="TIE18" )
	student7 = Student(name = "Ginesh Gulam", course_uid ="TIE18" )
	student8 = Student(name = "Haja Halisi", course_uid ="TIE18" )
	student9 = Student(name = "Injili Inakam", course_uid ="TIE18" )
	student10 = Student(name = "Joto Jepesi", course_uid ="TIE18" )

	students = [student1, student2, student3, student4, student5, student6, \
	student7, student8, student9, student10]

	module1 = Module(code = "ETI001", name = "Telecommunications", venue_code ="H7009" , course_code = "TIE18",attendance = None)
	module2 = Module(code = "ETI002", name = "Information systems", venue_code = "EMB101", course_code = "TIE18",attendance = None)
	module3 = Module(code = "ETI003", name = "Making phonecalls", venue_code ="4A" , course_code = "TIE18",attendance = None)
	module4 = Module(code = "ETI004", name = "Receiving phonecalls", venue_code = "SHAC", course_code = "TIE18",attendance = None)
	module5 = Module(code = "ETI005", name = "Writing phone reviews", venue_code = "PLMM", course_code = "TIE18",attendance = None)

	modules = [module1, module2, module3, module4, module5]

	admin_user = User(username = "mcflyhalf", email = 'dev@mail.com', name= 'Mark Flyhalf', password_hash='2bchanged', authenticated= False, active = True, privilege=PrivilegeLevel.admin.name)
	admin_user.set_password('Admin123')
	logger.debug("Created most dummy data for DB >>{}<< for integration testing. Attempting to persist the data...".format(conn_details))	#TODO:conn_details gives too much info. reduce to only give dbname

	for venue in venues:
		session.add(venue)

	for course in courses:
		session.add(course)

	for student in students:
		session.add(student)

	for module in modules:
		session.add(module)

	session.add(admin_user)

	session.commit()
	logger.info("Persisted most dummy data for DB >>{}<<  for integration testing. ".format(conn_details))

	#------------------STUDENT USER CREATION------------------#

	logger.debug("Creating student user dummy data for DB >>{}<< for integration testing.".format(conn_details))
	
	#TODO remove this query and use the fact that sqlalchemy adds the
	#primary key from the backend RDBMS to the object when session.commit() happens
	# see https://stackoverflow.com/questions/1316952/sqlalchemy-flush-and-get-inserted-id
	#Not the best source but a start 
	students = session.query(Student).limit(20).all()
	users = []

	for student in students:
		stud_fname = student.name.split()[0].lower()
		stud_lname = student.name.split()[1].lower()
		stud_username = stud_fname[0]+stud_lname
		stud_email = stud_username + '@nipo.com'
		stud_privilege = PrivilegeLevel.student.name

		stud_user = User(username= stud_username,\
						 email= stud_email,\
						 name= student.name,\
						 privilege= stud_privilege,
						 active= True,\
						 authenticated= False,\
						 student_id= student.id)

		stud_user.set_password('Stud123')
		session.add(stud_user)

	logger.debug("Created user dummy data for DB >>{}<< for integration testing. Attempting to persist the data...".format(conn_details))
	session.commit()
	logger.info("Persisted all dummy data for DB >>{}<<  for integration testing. ".format(conn_details))

	
	#------------------STAFF USER CREATION------------------#

	logger.debug("Creating staff users for DB >>{}<< for integration testing.".format(conn_details))
		
	staff_users = []

	staff_user = User(username = "stafflyhalf", email = 'staff1@mail.com', name= 'Staff Flyhalf', password_hash='2bchanged', authenticated= False, active = True, privilege=PrivilegeLevel.staff.name)
	staff_user.set_password('Staff123')
	staff_users.append(staff_user)

	staff_user = User(username = "starflyhalf", email = 'staff2@mail.com', name= 'Star Flyhalf', password_hash='2bchanged', authenticated= False, active = True, privilege=PrivilegeLevel.staff.name)
	staff_user.set_password('Staff123')
	staff_users.append(staff_user)

	for user in staff_users:
		session.add(user)

	session.commit()

	
	logger.debug("Created staff users dummy data for DB >>{}<< for integration testing. Attempting to persist the data...".format(conn_details))
	session.commit()

	#------------------Attach staff users to modules------------------#
	for i, module in enumerate(modules, start=1):
		if i == 1:
			#For the first module, include all (students and) staff
			module.addStaff(staff_users)
		elif i%2 == 0:
			#For even numbered modules append 1 staff user
			module.addStaff(staff_users[0])
		else:
			#For odd numbered modules append some staff user
			module.addStaff(staff_users[1])


	#------------------Attach students to modules------------------#
	for i, module in enumerate(modules, start=1):
		if i == 1:
			#For the first module, include all students (and staff)
			module.addStudent(students)
		elif i%2 == 0:
			#For even numbered modules exclude first 2 students
			module.addStudent(students[2:])
		else:
			#For odd numbered modules exclude last 3 students
			module.addStudent(students[:-3])


	logger.info("Persisted all dummy data for DB >>{}<<  for integration testing. ".format(conn_details))



	module_code = "ETI001"
	student_id = 6
	logger.info("Creating dummy attendance record for module >>{}<<".format(module_code))
	mod = ModuleAttendance(module_code,session)

	logger.debug("On creation, attendance record for {} is \n {}".format(module_code,mod.getAttendance()))


	for d in sd:
		mod.createClassSession(d)

	logger.debug("On creation of class session, attendance record for {} is \n {}".format(module_code ,mod.getAttendance()))

	for d in sd:
		for studID in range(len(students)):
			mod.updateAttendance(studID+1, d, present=random.choice([True,True,False,True,True,True]))	#Skew attendance towards presence

	logger.debug("After marking some students present, attendance record is \n {}".format(mod.getAttendance()))

	att = get_student_attendance(4,mod.getAttendance())

	logger.debug("The attendance for 1 Student is :\n {}".format(att))

	logger.info("Created dummy attendance record for module >>{}<<".format(module_code))