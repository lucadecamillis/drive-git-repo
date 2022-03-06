from core import utilities
from git import Repo

FT_HEAD = 'HEAD'

class GitLib:
	
	# CTOR
	def __init__(self, repoPath):
		self._repoPath = repoPath
		self.repo = Repo(self._repoPath)

		print("GitLib created")

	def bundleRepo(self, bundleFilePath):
		print("Bundeling repo '{0}' to output file '{1}' ...".format(self.repo.git_dir, bundleFilePath))

		command = 'git --git-dir "' + self.repo.git_dir + '" bundle create "' + bundleFilePath + '" --all'
		print("Executing command " + command)
		result = utilities.executeCommand(command)
		if result:
			print("Bundeling complete")
		else:
			print("An error occurred during bundeling")

		return result

	def fetchFromBundle(self, bundleFilePath):
		print("Fetching repo '" + str(self.repo.git_dir) + "' from bundle file '" + str(bundleFilePath) + "' ...")

		command = 'git --git-dir "' + self.repo.git_dir + '" fetch "' + bundleFilePath + '"'
		print("Executing command " + command)
		result = utilities.executeCommand(command)
		if result:
			print("Fetch complete")
		else:
			print("An error occurred during fetch")

def cloneFromBundle(gitRepoPath, bundleFilePath):
	print("Cloning from bundle '" + bundleFilePath + "' into repository '" + gitRepoPath + "' ...")

	command = 'git clone "' + bundleFilePath + '" "' + gitRepoPath + '"'
	print("Executing command " + command)
	result = utilities.executeCommand(command)
	if result:
		print("Cloning complete")
	else:
		print("An error occurred during cloning")

	return result

def getBunldeVersion(bundleFilePath):
	print("Getting bunlde version from bunlde '" + bundleFilePath + "'")

	command = 'git bundle list-heads "' + bundleFilePath + '"'
	print("Executing command " + command)
	result = bytes.decode(utilities.executeCommandWithOutput(command))

	version = {}
	for line in result.splitlines():
		splitLine = line.split()
		version[str(splitLine[1]).strip()] = str(splitLine[0]).strip()

	print(str(len(version)) + ' versions retrieved')
	return version

def getBunldeHead(bundleFilePath):
	version = getBunldeVersion(bundleFilePath)
	return version[FT_HEAD]