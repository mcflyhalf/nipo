#Create Setup.py file to make the module installable
from nipo.bootstrap_conf import create_bootstrap_configfile
create_bootstrap_configfile()
from setuptools import setup, find_packages
from nipo import production_engine, test_engine
from nipo.tests.populate import populate_testdb
from nipo.conf import NipoConfig, get_logger


setup(
	name = "nipo",
	version = "0.6.3",
	author = "Mcflyhalf",
	author_email = "mcflyhalf@live.com",
	description = ("An implementation of classroom attendance monitoring"),
	keywords = "facial recognition classroom attendance",
	packages= find_packages(),
	package_data={
        # For nipo_config file:
        "nipo": ["*config.cfg"],
        }
)

logger = get_logger("nipo_setup")

logger.info("Nipo python package successfuly installed")

#Create production db for actual work and test db for integration tests
logger.info("Creating tables for production. Will not drop if existing")
NipoConfig(production_engine, tables_dropped=False)
logger.info("Created tables for production. Did not drop if existing")
logger.info("Creating tables for test. Will drop if existing")
NipoConfig(test_engine, tables_dropped=True)
logger.info("Created tables for test. Dropped if existing")

populate_testdb()		#Put some data into the test db to be used for integration tests


