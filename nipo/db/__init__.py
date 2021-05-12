from nipo.db.schema import User, Venue, Course, Student, Module
from nipo.task_mgr import get_celery_app
from celery.exceptions import Ignore
from nipo import session
from sqlalchemy.exc import IntegrityError

celery_app= get_celery_app()

def get_course_list(session, max=10):
	courses = session.query(Course).\
							limit(max).\
							all()

	return courses

def get_module_list(session, max=10):
	modules = session.query(Module).\
							limit(max).\
							all()

	return modules


def get_student_list(session, max=10):
	students = session.query(Student).\
							limit(max).\
							all()

	return students

def get_user_list(session, max=10):
	users = session.query(User).\
							limit(max).\
							all()

	return users

def get_venue_list(session, max=10):
	venues = session.query(Venue).\
							limit(max).\
							all()

	return venues

def get_tables_metadata():
	sorted_tables = schema.Base.metadata.sorted_tables

	return sorted_tables

def get_tables_data(session):
	'''
	Get BOTH data and metadata of the tables. Metadata is required to make sense of the data
	The tables student_module and user_module are excluded as they are secondary tables
	'''
	# Tables to be stored in a dict as:
	# * Table1Name
	#	- Name
	# 	- Headers
	# 	- Data
	# * Table2Name
	#	- Name
	# 	- Headers
	# 	- Data
	# Data to be limited to 10 items for now
	table = {} #Dict to store the table info (headers + data)
	
	_tables = get_tables_metadata()
	# drop student_module and user_module tables
	for _table in _tables:
		if _table.name.endswith("_module"):
			_tables.remove(_table)

	for _table in _tables:
		table_prop = {}	#Dict for table properties
		tableName = str(_table.name)
		headers = [col.name for col in _table.columns]
		raw_data = session.query(_table).limit(10).all()

		#Regretable hack to remove the password hash and attendance columns
		#TODO: Modify query to only return the columns of interest
		# from the concerned tables
		#This will eliminate the need for the if statements in the rest of the fxn
		if tableName in ['user', 'module']:
			headers = headers[:-1]	#Drop the last element

		data = []
		for row in raw_data:
			data_list = [cell for cell in row]
			if tableName in ['user', 'module']:
				data_list = data_list[:-1]	#Drop the last element (pw or attendance)
			data.append(data_list)

		table_prop['name'] = tableName  # Not necessary as is captured elsewhere
		table_prop['headers'] = headers
		table_prop['data'] = data

		table[tableName] = table_prop

	return table

tableName2ORMClass = {}
tableName2ORMClass['student'] = Student
tableName2ORMClass['module'] = Module
tableName2ORMClass['venue'] = Venue
tableName2ORMClass['course'] = Course
tableName2ORMClass['user'] = User

#In the method below, the status is actually stored by the return
#(in task.info). The state is eventually changed to success because no
#exception is raised. Need to figure out how to sort this out
@celery_app.task(bind=True, throws=(IntegrityError))
def add_entity(self,entity_dict, tablename):
	ORM_cls = tableName2ORMClass[tablename]
	ORM_obj = ORM_cls(**entity_dict)
	result = {}
	try:
		session.add(ORM_obj)
		session.commit()
	except IntegrityError as e:
		self.update_state(meta={'Added': False, 'description': 'Non-unique id property'})
		session.rollback()
		print('>>celery worker Failed to add entity.')
		# return result
		raise e

	result['status'] = 'SUCCESS'
	self.update_state(state='SUCCESS', meta={'Added': True, 'more': 'info1'})
	#TODO: Convert to log
	print('entity added by celery worker')
	return result
	
