#This file will eventually be removed. It is here to test functionality that interfaces with objects that havent been created or functionality that requires a populated DB (for this we use nipo_test which is a mirror of nipo but whose contents are used for testing purposes)

#Documentation for creating an instance of the mapped classes is very well done herehttps://docs.sqlalchemy.org/en/latest/orm/tutorial.html#create-an-instance-of-the-mapped-class



from nipo import test_session
from nipo.db.schema import Module, Student, Course, Venue

venue1 = Venue(code = "H7009", name = "Hall 7 Rm 9", capacity = 20)
venue2 = Venue(code = "EMB101", name = "Eng MAin Building 101" , capacity = 30)
venue3 = Venue(code = "4A", name = "Form 4A", capacity = 60)
venue4 = Venue(code = "SHAC", name = "Shirrin Aumreedy-Cziffra" , capacity = 35 )
venue5 = Venue(code = "PLMM", name = "Patrice Lumumba" , capacity = 40)

venues = [venue1, venue2, venue3, venue4, venue5]

course1 = Course(uid = "TIE18", name = "Telecommunications and Information Engineering 2018")

courses = [course1]

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

for venue in venues:
	test_session.add(venue)

for course in courses:
	test_session.add(course)

for student in students:
	test_session.add(student)

for module in modules:
	test_session.add(module)

test_session.commit()