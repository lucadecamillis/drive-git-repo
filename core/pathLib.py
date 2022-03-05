import tempfile
import os
from core import utilities

class PathLib:

	# CTOR
	def __init__(self, argLib):
		self._argLib = argLib
		self._configFolderPath = None
		self._tempBundleFilePath = None
		print("PathLib lib created")

	def getBundleFilePath(self):
		outputFile = self._argLib.getOutputFile()

		if not outputFile:
			return self.getTempBundleFilePath()
		else:
			return outputFile

	def getBundleFileName(self):
		return utilities.getFolderName(self.getBundleFilePath())

	def getJsonFilePath(self):
		return self.getBundleFilePath() + '.json'

	def getConfigFolderPath(self):
		if self._configFolderPath is None:
			# Get the current user folder
			userFolder = os.path.expanduser('~')

			# Create a temp folder for the application
			self._configFolderPath = os.path.join(userFolder, '.repoSync')
			utilities.createFolderIfNotExist(self._configFolderPath)

		return self._configFolderPath

	def getTempBundleFilePath(self):
		if self._tempBundleFilePath is None:
			# Create a folder for the repository into the config folder
			gitRepoFolder = self._argLib.getGitRepoFolder()
			gitRepoName = utilities.getFolderName(gitRepoFolder)
			bundleTempFolder = os.path.join(self.getConfigFolderPath(), gitRepoName)
			utilities.createFolderIfNotExist(bundleTempFolder)
			# Store the bundle file path
			self._tempBundleFilePath = os.path.join(bundleTempFolder, gitRepoName)

		return self._tempBundleFilePath