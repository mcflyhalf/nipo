def get_course_list(session):
	courses = session.query(schema.Course).\
							limit(10).\
							all()

	return courses

def get_module_list(session):
	modules = session.query(schema.Module).\
							limit(10).\
							all()

	return modules


def get_student_list(session):
	students = session.query(schema.Student).\
							limit(10).\
							all()

	return students

def get_user_list(session):
	users = session.query(schema.User).\
							limit(10).\
							all()

	return users

def get_venue_list(session):
	venues = session.query(schema.Venue).\
							limit(10).\
							all()

	return venues

def get_tables_metadata():
	sorted_tables = schema.Base.metadata.sorted_tables

	return sorted_tables

def get_tables_data(session):
	'''Get BOTH data and metadata of the tables. Metadata is required to make sense of the data'''
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




