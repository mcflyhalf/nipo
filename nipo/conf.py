from nipo import get_logger
from nipo.db.schema import Base
from nipo.db import get_tables_metadata
from nipo.bootstrap_conf import CONFIG_FILE_NAME

CONFIG_FILENAME = CONFIG_FILE_NAME
logger = get_logger("nipo_config")

class NipoConfig:
	'''
	Class contains functionality for creating tables for a fresh install.
	DB needs to have been created in advance outside of python
	'''

	def __init__(self,engine, tables_dropped=False):
		#Probably not a good idea to drop all tables 
		#while doing a new configuration
		#TODO: Consider applying a migration to account for schema changes
		self.tables_dropped=tables_dropped
		self.new_db_config(engine)


	def create_tables(self, engine):
		tables = get_tables_metadata()
		#Create (but not populate all tables in the db schema)
		logger.info("Attempting to create tables")
		#Do stuff here using metadata from the classes in the schema
		for table in tables:
			logger.info("Creating table *{}*".format(table.name))
			Base.metadata.create_all(engine, tables=[table])
			logger.info("Table *{}* created successfully".format(table.name))

		logger.info("Tables Created successfully!")

	#Delete all tables (DB should have been created in advance)
	def drop_tables(self, engine):
		tables = get_tables_metadata()
		tables.reverse()
		logger.warn("Deleting all tables")
		#Do dangerous stuff here and log as each table is deleted
		for table in tables:
			logger.warn("Deleting table *{}*".format(table.name))
			#TODO: Move use of Base away from here to somewhere in nipo.db
			#EXample like get_tables()
			Base.metadata.drop_all(engine, tables=[table])
			logger.info("Table *{}* deleted successfully".format(table.name))

		logger.info("Tables deleted successfully!")

	def new_db_config(self, engine):	#For a new install
		if self.tables_dropped:
			self.drop_tables(engine)
		self.create_tables(engine)

	def create_configfile(self):
		config = configparser.ConfigParser()

		config['DEFAULT'] = {}
		default = config['DEFAULT']

		default['Install Location'] = str(os.getcwd())	#Base install directory
		default['config_file'] = os.path.join(os.getcwd(), CONFIG_FILENAME)

		#Create config file
		with open(CONFIG_FILENAME, 'w') as configfile:
			config.write(configfile)