# Default Values for Globals
# The defaults are based on the Exodus League's
# defaults.

import configparser
import os

path = os.path.dirname(os.path.realpath(__file__))
path += '\SETTINGS.INI'
config = configparser.ConfigParser()
config.read(path)

MIN_SALARY = config.getfloat("DEFAULT", "MinSalary")
MAX_SALARY = config.getfloat("DEFAULT", "MaxSalary")
SOFT_CAP = config.getfloat("DEFAULT", "SoftCap")
APRON_CAP = config.getfloat("DEFAULT", "ApronCap")
HARD_CAP = config.getfloat("DEFAULT", "HardCap")
NONTAX_MLE = config.getfloat("EXCEPTION", "NonTaxMLE")
TAX_MLE = config.getfloat("EXCEPTION", "TaxMLE")

IGNORE_CAP_RULES = config.getboolean("EXCEPTION", "IgnoreAll")
USE_MLE = config.getboolean("EXCEPTION", "MLE")
USE_BIRDS = config.getboolean("EXCEPTION", "BirdRights")
USE_VET_MIN = config.getboolean("EXCEPTION", "VetMin")
BIRDS_THRESHOLD = config.getint('EXCEPTION', 'BirdRightsThreshold')

RANDOMNESS = not config.getboolean("RANDOMNESS", "RemoveRandomness")

# Logger Default Value
LOGGER = None

def log_output(string):
	if LOGGER is not None:
		"""
		Print the log as well
		as write it into file.
		"""
		print(string)
		LOGGER.write(str(string) + "\n")

	else:
		raise Exception("LOGGER value is not set.")