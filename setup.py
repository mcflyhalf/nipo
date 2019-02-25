#Create Setup.py file to make the module installable


#Create Various necessary Classes to be used as tables in the DB. Classes represent tables in the DB and objects will represent rows in these tables. This is how Sqlalchemy and other Python ORM's work
#(Not sure whether these classes should be created here in setup.py or in the base nipo/__init__.py so will list them in both places)

#Create lesson class (corresponds to DB table that has a list of lessons. We expect that each lesson will in turn have qualities like start time, end time, venue, date and the class that should attend this lesson etc)

#Student Class. Represents an individual student. Should have properties like a UID, Class tht they belong to (Form 1, Form 2, Engineering y1, CS y3 etc), location of their picture (to be used to recognise them)

#Course Class. A course is like (Form 1, Form 2, Engineering y1, CS y3 etc). Calling this a class which is more natural would be confused with the programming Class structure. Consider referring to it as a course. A class has a UID and Name only. Also, each student belongs to at least(usually only) one class

#These are all the tables I can currently think of