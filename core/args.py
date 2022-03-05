import argparse
from core import utilities

class Arguments:
	"""Collection of arguments"""

	# CTOR
	def __init__(self):
		parser = argparse.ArgumentParser()
		Arguments.addArguments(parser)

		print('Parsing arguments ...')
		self.ParsedArgs = parser.parse_args()
		print('Parsed arguments: ' + str(self.ParsedArgs))

		print("Arguments lib created")
	
	def getGitRepoFolder(self):
		return utilities.normalizePath(self.ParsedArgs.gitRepoFolder)

	def getOutputFile(self):
		if self.ParsedArgs.outputFile is None:
			return None
		else:
			return utilities.normalizePath(self.ParsedArgs.outputFile)

	@staticmethod
	def addArguments(parser):
		parser.add_argument(
			'-g',
			action="store",
			dest="gitRepoFolder",
			help="Path to the git folder to be synch",
			required=True)
		parser.add_argument(
			'-o',
			action="store",
			dest="outputFile",
			help="Output bundle file",
			required=False)
		parser.add_argument(
			'--reset-credentials',
			action='store_true',
			dest="resetCredentials",
			help="Reset oauth2 cached credentials",
			required=False)