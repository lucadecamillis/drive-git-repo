import subprocess
import json
import os

def writeJson(data, fileName):
	"""Writing JSON data"""
	with open(fileName, 'w') as f:
		json.dump(data, f)

def readJson(fileName):
	"""Reading data back"""
	with open(fileName, 'r') as f:
		return json.load(f)

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
	"""Human readable bytes"""

	if isinstance(nbytes, str):
		nbytes = int(nbytes)

	i = 0
	while nbytes >= 1024 and i < len(suffixes) - 1:
		nbytes /= 1024.
		i += 1
	f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
	return '%s %s' % (f, suffixes[i])

def concatenateFields(fields):
	s = ","
	return s.join(fields)

def executeCommand(commandString):
	exitStatus = os.system(commandString)
	return parseExitStatus(exitStatus)

def executeCommandWithOutput(commandString):
	return subprocess.check_output(commandString, shell=True)

def parseExitStatus(exitStatus):
	"""Parse exit status of command line commands"""
	# 0 means executed correctly
	return not bool(exitStatus)

def createFolderIfNotExist(folderPath):
	if not os.path.exists(folderPath):
		os.makedirs(folderPath)

def getFolderName(folderPath):
	# remove trailing slashes or back slashes to extract the folder name
	# Use both to ensure compatibility windows/linux/urls
	return os.path.basename(folderPath.rstrip('/').rstrip('\\'))

def normalizePath(folderPath):
	return os.path.expanduser(folderPath.strip())

def nonexistentOrEmptyFolder(folderPath):
	return not os.path.exists(folderPath) or not os.listdir(folderPath)