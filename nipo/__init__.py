from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import os
import configparser

config_filename = 'nipo_config.cfg'

def get_configs(defaults = True):
	config = configparser.ConfigParser()
	config.read(os.path.join(os.path.cwd(),'..',config_filename))
	if defaults:
		return config['DEFAULT']
	else:
		return config


def get_logger(loggerName):
	log = logging.getLogger(loggerName)
	# File handler which logs even debug messages
	fh = logging.FileHandler('nipo.log')
	fh.setLevel(logging.DEBUG)
	# Console handler that logs warnings or higher
	ch = logging.StreamHandler()
	ch.setLevel(logging.WARNING)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	# add the handlers to the logger
	print ("Adding a set of handlers now")
	log.addHandler(fh)
	log.addHandler(ch)
	log.setLevel(logging.DEBUG)
	return log

#create sqlalchemy engine (for actual use), test engine(for testing db connection) and session (only for the engine)

engine = create_engine('postgresql://{dbuser}:{passwd}@{host}:{port}/{dbname}'.format(\
	dbuser = os.environ['POSTGRES_USER'] ,
	passwd = os.environ['POSTGRES_PASS'],
	host = 'localhost',
	port = os.environ['POSTGRES_PORT'],
	dbname = os.environ['POSTGRES_NIPO_DBNAME']))

Session = sessionmaker(bind=engine)
session = Session()

test_engine = create_engine('postgresql://{dbuser}:{passwd}@{host}:{port}/{dbname}'.format(\
	dbuser = os.environ['POSTGRES_USER'] ,
	passwd = os.environ['POSTGRES_PASS'],
	host = 'localhost',
	port = os.environ['POSTGRES_PORT'],
	dbname = os.environ['POSTGRES_NIPO_TEST_DBNAME']))

TestSession = sessionmaker(bind=test_engine)
test_session = TestSession()

