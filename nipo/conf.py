import os
import logging
import configparser
import tempfile
from logging.handlers import RotatingFileHandler
from nipo.db.schema import Base
from nipo.db import get_tables_metadata
from nipo.bootstrap_conf import CONFIG_FILE_NAME

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

CONFIG_FILENAME = CONFIG_FILE_NAME
UPLOAD_PATH = os.path.join(tempfile.gettempdir(), "nipo")

def get_configs(profile = 'DEFAULT'):
	
	curdir = os.path.dirname(__file__)	#The Path to this __init__ file. Trick from https://stackoverflow.com/questions/247770/how-to-retrieve-a-modules-path
	curdir = os.path.abspath(curdir)
	config = configparser.ConfigParser()
	config.read(os.path.join(curdir,CONFIG_FILENAME))
	
	return config[profile]

def get_logger(loggerName):
	log = logging.getLogger(loggerName)
	# File handler which logs even debug messages
	# To atttempt compression of old log files, try https://docs.python.org/3/howto/logging-cookbook.html#using-a-rotator-and-namer-to-customize-log-rotation-processing
	config = get_configs()
	log_location = os.path.join(config['Install Location'],'log','nipo.log')
	if not os.path.exists(log_location):
		os.makedirs(log_location[:len('nipo.log')*-1])
	fh = RotatingFileHandler(log_location, mode='a', maxBytes=1*1024*1024,backupCount=10, encoding=None, delay=0)
	fh.setLevel(logging.DEBUG)
	# Console handler that logs warnings or higher
	ch = logging.StreamHandler()
	ch.setLevel(logging.WARNING)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	# add the handlers to the logger
	log.addHandler(fh)
	log.addHandler(ch)
	log.setLevel(logging.DEBUG)
	return log

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
		default['config_file'] = os.path.join(os.getcwd(),'nipo', CONFIG_FILENAME)

		#Create config file
		with open(default['config_file'], 'w') as configfile:
			config.write(configfile)



#create sqlalchemy engine (for actual use), test engine(for testing db connection) and session (only for the engine)

production_engine = create_engine('postgresql://{dbuser}:{passwd}@{host}:{port}/{dbname}'.format(\
	dbuser = os.environ['POSTGRES_USER'] ,
	passwd = os.environ['POSTGRES_PASS'],
	host = os.environ['POSTGRES_HOST'],
	port = os.environ['POSTGRES_PORT'],
	dbname = os.environ['POSTGRES_NIPO_DBNAME']))

ProductionSession = sessionmaker(bind=production_engine)
production_session = ProductionSession()

test_engine = create_engine('postgresql://{dbuser}:{passwd}@{host}:{port}/{dbname}'.format(\
	dbuser = os.environ['POSTGRES_USER'] ,
	passwd = os.environ['POSTGRES_PASS'],
	host = os.environ['POSTGRES_HOST'],
	port = os.environ['POSTGRES_PORT'],
	dbname = os.environ['POSTGRES_NIPO_TEST_DBNAME']),
	echo = False)

TestSession = sessionmaker(bind=test_engine)
test_session = TestSession()
if os.environ['FLASK_ENV'] == 'production':
	Session = ProductionSession	
	session = production_session
else:
	Session = TestSession 
	session = test_session

