#Minimal configuration for bootstrapping a first install
import os
import configparser

CONFIG_FILE_NAME = 'nipo_config.cfg'

def create_bootstrap_configfile():
	config = configparser.ConfigParser()

	config['DEFAULT'] = {}
	default = config['DEFAULT']

	default['Install Location'] = str(os.getcwd())	#Base install directory
	default['config_file'] = os.path.join(os.getcwd(), CONFIG_FILENAME)

	#Create config file
	with open(CONFIG_FILE_NAME, 'w') as configfile:
		config.write(configfile)

create_bootstrap_configfile()