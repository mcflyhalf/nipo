#Create Setup.py file to make the module installable
from setuptools import setup, find_packages
from nipo import get_logger, engine, test_engine
from nipo.db.schema import Base


setup(
    name = "nipo",
    version = "0.1",
    author = "Mcflyhalf",
    author_email = "mcflyhalf@live.com",
    description = ("An application of facial recognition in classroom attendance monitoring"),
    keywords = "facial recognition classroom attendance",
    packages= find_packages(),
)

logger = get_logger("nipo_log")

logger.info("Nipo python package successfuly installed")


class NipoConfig:
	#Create tables (DB needs to have been created in advance)

	def __init__(self,engine):
		self.newconfig(engine)


	def create_tables(self, engine):
		tables = Base.metadata.sorted_tables
		#Create (but not populate all tables in the db schema)
		logger.info("Attempting to create tables")
		#Do stuff here using metadata from the classes in the schema
		for table in tables:
			table = [table]
			logger.info("Creating table *{}*".format(table[0].name))
			Base.metadata.create_all(engine, tables=table)
			logger.info("Table *{}* created successfully".format(table[0].name))

		logger.info("Tables Created successfully!")

	#Delete all tables (DB should have been created in advance)
	def drop_tables(self, engine):
		tables = Base.metadata.sorted_tables
		tables.reverse()
		logger.warn("Deleting all tables")
		#Do dangerous stuff here and log as each table is deleted
		for table in tables:
			table = [table]
			logger.warn("Deleting table *{}*".format(table[0].name))
			Base.metadata.drop_all(engine, tables=table)
			logger.info("Table *{}* deleted successfully".format(table[0].name))

		logger.info("Tables deleted successfully!")

	def newconfig(self, engine):	#For a new install
		self.drop_tables(engine)
		self.create_tables(engine)

	def create_paths(self, rootpath ):	#Set default root path to the current directory
		pass

config = NipoConfig(engine)
test_config = NipoConfig(test_engine)
