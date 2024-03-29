import pandas
import os
import csv
from celery.exceptions import Ignore
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound
from nipo.db.schema import User, Venue, Course, Student, Module
from nipo.db import schema, get_tables_metadata
from nipo.task_mgr import get_celery_app
from nipo.conf import Session

celery_app= get_celery_app()
UPLOAD_FILE_LIFETIME = 5*60*60 #5 Hours

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
		raw_data = session.query(_table).limit(30).all()

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

def _ORM_obj_from_dict(entity_dict, tablename):
	'''
	Take in a dict, add an equivalent record to db table
	'''
	tableName2ORMClass = {}
	tableName2ORMClass['student'] = Student
	tableName2ORMClass['module'] = Module
	tableName2ORMClass['venue'] = Venue
	tableName2ORMClass['course'] = Course
	tableName2ORMClass['user'] = User

	ORM_cls = tableName2ORMClass[tablename]
	ORM_obj = ORM_cls(**entity_dict)

	return ORM_obj

#In the method below, the status is actually stored by the return
#(in task.info).
@celery_app.task(bind=True, throws=(IntegrityError))
def add_entity(self,entity_dict, tablename):
	ORM_obj = _ORM_obj_from_dict(entity_dict, tablename)
	result = {}
	with Session() as session:
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
	#TODO: Convert to log. Still currently 
	print('entity added by celery worker')
	return result
	
@celery_app.task(bind=True, throws=(IntegrityError))
def add_entities(self, entity_type, filepath):
	'''
	adds several entities (of the same type) To db from a csv file
	:param entity_type: The type of entities. Can be one of the db tables (Module, Student, User etc)
	:param filepath: The full path to the location of the file. Must be a csv file with a header row where headers are names of attributes
	'''
	tablename = entity_type.lower()
	entities_df = pandas.read_csv(filepath)
	#Mark file for deletion in 24 hours
	remove_file.apply_async((filepath,), countdown=UPLOAD_FILE_LIFETIME)
	col_rename_mapper = {}

	for column in entities_df.columns:
		if ' ' not in column:
			continue
		space_loc = column.index(' ')
		col_rename_mapper[column] = column[space_loc+1:].lower()

	entities_df = entities_df.rename(mapper=col_rename_mapper,
									 axis='columns')
	# Returns a list of dicts
	entities_list = entities_df.to_dict(orient='records')
	total_entities = len(entities_list)

	# Previous implementation that could tell exactly which record was duplicated
	# with Session() as session:
	# 	for i, entity_dict in enumerate(entities_list):
	# 		ORM_obj = _ORM_obj_from_dict(entity_dict, tablename)
	# 		try:
	# 			session.add(ORM_obj)
	# 			session.commit()
	# 			self.update_state(state= 'IN PROGRESS',
	# 							  meta ={'current': i, 'total': total_entities})
	# 		except IntegrityError as e:
	# 			# Log these actions??
	# 			self.update_state(state= 'IN PROGRESS',
	# 							  meta ={'current': i, 'total': total_entities, 'fail '+str(i): 'ERROR'})
	# 			print('>>celery worker Failed to add entity {} of {}.'
	# 				.format(i, total_entities))
	# 			# return result
	# 			raise e

	# This version uses context managers and foregoes committing records 1 by 1.
	# This loses benefit of knowing exactly which record failed. This info 
	# is still available in the exception message but has been deemed unnecessary
	# as the entire transaction is supposed to be rolled back anyway 
	with Session() as session:
		try:
			with session.begin(): 
				for i, entity_dict in enumerate(entities_list):
					ORM_obj = _ORM_obj_from_dict(entity_dict, tablename)
					session.add(ORM_obj)
					self.update_state(state= 'IN PROGRESS',
									  meta ={'current': i, 'total': total_entities})
		except IntegrityError as e:
			# Log these actions??
			self.update_state(state= 'IN PROGRESS',
							  meta ={'current': i, 'total': total_entities, 'fail '+str(i): 'ERROR'})
			print('>>celery worker Failed to add at least one of the entities.')
			# return result
			raise e
			
	#TODO: Convert to log
	print('entities added by celery worker')

	
@celery_app.task(bind=True, throws=(ValueError, MultipleResultsFound, NoResultFound))
def attach_individual(self, designation, modulecode, emailOrId):
	'''
	attaches a single student or member of staff to a module
	:param designation : staff or student
	:param modulecode : module code for the module where stff/student is to be attached 
	:param emailOrId : email address (for staff) Or Id (for student). Must match the designation 
	'''
	with Session() as session:
		with session.begin():
			module = session.query(Module).filter(Module.code==modulecode).one()

			try:
				# Attach the individual to the module then commit
				if designation.lower() == 'staff':
					staff_user = session.query(User).filter(User.email==emailOrId).one()
					module.attachStaff(staff_user)
					desig_id = 'email'
				elif designation.lower() == 'student':
					stud_user = session.query(Student).filter(Student.id==emailOrId).one()
					module.attachStudent(stud_user)
					desig_id = 'id'
				else:
					raise ValueError("Invalid designation. Designation must be 'student' or 'staff'")
			except MultipleResultsFound as e:
				raise e("Non-unique staff email {} in use. Contact admin immediately!".format(emailOrId))

			except NoResultFound as e:
				raise e("Invalid {} {}:\t{}".format(designation, design_id, emailOrId))


	
@celery_app.task(bind=True, throws=(ValueError, MultipleResultsFound, NoResultFound))
def attach_to_module_from_file_upload(self, filepath):
	'''
	attach several students and/or members of staff to a module as designated by a file

	file should be csv with each row in the format:
	deignation, modulecode, emailOrId
	where 	designation = 'student' or 'staff'
			modulecode = modulecode in question e.g. 'ETI002'
			emailOrId = an integer student ID for a student e.g. 23 or an email address for staff member e.g. 'ciku@mail.com' 
	:param filepath : path to the csv file containing the info 
	'''
	remove_file.apply_async((filepath,), countdown=UPLOAD_FILE_LIFETIME)
	with open(filepath) as csvfile:
		records = csv.DictReader(csvfile,fieldnames=['designation','modulecode','emailorid'])
		# Convert to iterator in order to skip first record (header row)
		records = iter(records)
		next(records)
		with Session() as session:
			try:
				with session.begin():
					for record in records:
						designation = record['designation']
						modulecode = record['modulecode']
						emailOrId = record['emailorid']

						#If exception comes from this next line, nonexistent module code may be the issue
						module = session.query(Module).filter(Module.code==modulecode).one()

						if designation.lower() == 'staff':
							staff_user = session.query(User).filter(User.email==emailOrId).one()
							module.attachStaff(staff_user)
						elif designation.lower() == 'student':
							stud_user = session.query(Student).filter(Student.id==emailOrId).one()
							module.attachStudent(stud_user)
						else:
							raise ValueError("Invalid designation. Designation must be 'student' or 'staff'")
			except:
				# Reserved for future use
				raise
	print('All students/staff attached')
			

@celery_app.task(bind=True, throws=(ValueError, NoResultFound))
def attach_to_module_entire_course(self, modulecode, courseuid):
	'''
	attaches all students registered to a course to a module
	:param modulecode : module code for the module where course students are to be attached 
	:param courseuid : uid of course whose students are to be attached 
	'''
	with Session() as session:
		with session.begin():
			module = session.query(Module).filter(Module.code==modulecode).one()
			students = session.query(Student).filter(Student.course_uid==courseuid).all()
			module.attachStudent(students)

	print("Students from course >>{}<< attached to module>>{}<<".format(courseuid, modulecode))




@celery_app.task(ignore_result=True)
def remove_file(filepath):
	'''
	Deletes a file. Function defined so it can be called later via celery

	:param filepath: The full path to the location of the file.
	'''
	if os.path.exists(filepath):
		os.remove(filepath)
		print ('File >>{}<< removed by celery worker'.format(filepath))
		return
	print ('Attempted to remove File >>{}<<. File not found by celery worker'.format(filepath))
