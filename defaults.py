# Default Values for Globals
# The defaults are based on the Exodus League's
# defaults.

MIN_SALARY = 0.9
MAX_SALARY = 35.3
SOFT_CAP = 109.0
APRON_CAP = 130.0
HARD_CAP = 142.0

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