#Create Setup.py file to make the module installable
from setuptools import setup, find_packages
from nipo import get_logger


setup(
    name = "nipo",
    version = "0.1",
    author = "Mcflyhalf",
    author_email = "mcflyhalf@live.com",
    description = ("An application of facial recognition in classroom attendance monitoring"),
    keywords = "facial recognition classroom attendance",
    packages= find_packages(),
)

logger = get_logger()

logger.info("Nipo python package successfuly installed")


class NipoConfig:
	#Create tables (DB needs to have been created in advance)
	def create_tables(self):
		#Create (but not populate all tables in the db schema)
		logger.info("Attempting to create tables")
		#Do stuff here using metadata from the classes in the schema


		logger.info("Tables Created successfully!")

	def create_paths(self, rootpath = ):	#Set default root path to the current directory
		pass