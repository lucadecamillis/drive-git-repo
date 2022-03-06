import os
from core import utilities
from core import args
from core import gitLib
from core import google
from core import pathLib

class RepoLib:
	"""Manages interactions of git repository in google drive"""

	# CTOR
	def __init__(self):
		print('Google Driver Git Repository @lucadecamillis, version 0.1')
		self._argLib = args.Arguments()
		self._pathLib = pathLib.PathLib(self._argLib)
		self._gapi = None

	def repoVersion(self):
		print('Print the version of the repository on the drive')

		repoFileName = self._pathLib.getBundleFileName()

		# Try to retrieve the given repostory from the google drive store
		repoMetadata = self.getGoogleApi().getRepo(repoFileName)

		# Print the info
		if repoMetadata is None:
			print("No repository '{0}' saved in drive".format(repoFileName))
		else:	
			print("Current version on drive ({0})".format(self.printMetadata(repoMetadata)))

	def sync(self):
		print('Sync local repository from google drive')

		# Try to sync the local bundle file
		metadata = self.trySyncLocalBundle()

		gitRepoFolder = self._argLib.getGitRepoFolder()
		bundleFilePath = self._pathLib.getBundleFilePath()

		if utilities.nonexistentOrEmptyFolder(gitRepoFolder):
			print('Folder "' + gitRepoFolder + '" null or emtpy. Try to create it ...')
			# Repository not yet initialized, create the folder
			utilities.createFolderIfNotExist(gitRepoFolder)
			# Clone then the bundle
			gitLib.cloneFromBundle(gitRepoFolder, bundleFilePath)
		else:
			# Folder not emtpy. Check it is a valid Git Repository
			gitRepo = gitLib.GitLib(self._argLib.getGitRepoFolder())
			print('Folder "' + gitRepoFolder + '" is a valid Git Repository')
			# Fetch the last version
			gitRepo.fetchFromBundle(bundleFilePath)

		print('Sync local repository complete')

	def push(self):
		print('Push local repository changes to google drive')

		gitRepoFolder = self._argLib.getGitRepoFolder()
		repoFileName = self._pathLib.getBundleFileName()
		bundleFilePath = self._pathLib.getBundleFilePath()

		# Try to sync the local bundle file
		metadata = self.trySyncLocalBundle()

		# Get the HEAD version of the synched repo
		original_head = gitLib.getBunldeHead(bundleFilePath)
		print('Head of the existing bundle before bundeling: ' + original_head)

		# Open the git repository
		gitRepo = gitLib.GitLib(gitRepoFolder)

		# Now we bundle the current repo
		gitRepo.bundleRepo(bundleFilePath)

		# Recalculate the head
		pushed_head = gitLib.getBunldeHead(bundleFilePath)
		print('Head of the existing bundle after bundeling: ' + pushed_head)

		# Check the bundle has changed
		if original_head == pushed_head:
			# Local repository hasn't been updated, return
			print('Git repo has not changed, discard bundle')
			return

		print('New head version, pushing to drive')

		# Upload the new version
		metadata = self.getGoogleApi().updateRepo(bundleFilePath, metadata[google.F_ID])

		# Delete older versions
		print('Deleting older drive revisions ...')
		self.getGoogleApi().deleteAllRevisionButHead(metadata)
		print('Older drive revisions deleted')

		# Download again the bundle metadata, since the version number may be updated
		metadata = gBundleFile = self.getGoogleApi().getRepo(repoFileName)

		# Update the metadata
		self.updateBundleMetadata(metadata, pushed_head)
		print('Local metadata updated')

		print('Pushing to drive complete')

	def init(self):
		print('Initialize a new repository on google drive')
		print('If the repository is already initialized, throw an exception')

		gitRepoFolder = self._argLib.getGitRepoFolder()
		repoFileName = self._pathLib.getBundleFileName()

		# Try to retrieve the given repostory from the google drive store
		api = self.getGoogleApi()
		gBundleFile = api.getRepo(repoFileName)

		if gBundleFile is None:
			# Open the git repository
			gitRepo = gitLib.GitLib(gitRepoFolder)

			# Bundle the repository
			bundleFilePath = self._pathLib.getBundleFilePath()
			gitRepo.bundleRepo(bundleFilePath)

			# initialize the repository on google drive
			print("Initializing repository '" + repoFileName + "'...")
			metadata = api.createRepo(bundleFilePath, repoFileName)
			print("Repository '" + repoFileName + "' initialized")
		else:
			raise Exception("The repository '" + repoFileName + "' already initialized on the google drive. Cannot initialize the repository")

	def tryUploadNewVersion(self):
		"""Upload the local bundle file to google drive"""

		repoFileName = self._pathLib.getBundleFileName()

		# Try to retrieve the given repostory from the google drive store
		gBundleFile = self.getGoogleApi().getRepo(repoFileName)

		if gBundleFile is None:
			raise Exception("The repository '" + repoFileName + "' does not exist on the drive")

		# Upload the new version

	def trySyncLocalBundle(self):
		"""Sync the drive bundle file on local disk"""

		repoFileName = self._pathLib.getBundleFileName()
		repoLocalPath = self._pathLib.getBundleFilePath()
		repoMetadataPath = self._pathLib.getJsonFilePath()

		# Try to retrieve the given repostory from the google drive store
		gBundleFile = self.getGoogleApi().getRepo(repoFileName)

		if gBundleFile is None:
			raise Exception("The repository '" + repoFileName + "' does not exist on the drive")

		print("Found repository on drive (" + self.printMetadata(gBundleFile) + ")")

		# Check whether the local file exists
		if os.path.isfile(repoLocalPath) and os.path.isfile(repoMetadataPath):

			# load the metadata
			metadata = self.readMetadata()

			# Check whether the metadata refers to the bundle on the drive
			if metadata[google.F_ID] != gBundleFile[google.F_ID]:
				raise Exception("The repository with name '" + repoFileName +
					"' found on drive doesn't match the ID of the locally stored metadata")

			# Parse the versions
			localVersion = int(metadata[google.F_VERSION])
			driveVersion = int(gBundleFile[google.F_VERSION])

			# If the repository matched the locally stored id, check if a new version is available
			if driveVersion > localVersion:
				# Download the new version
				print("An old version is saved on disk (" +
					str(localVersion) + "<" + str(driveVersion) +
					"). Download the new version ...")
				self.downloadBundle(gBundleFile)
			else:
				print("The local repository is up to date. Current version (" +
					str(localVersion) + "), Drive version (" +
					str(driveVersion) + ")")
		else:
			# Download the current drive version on disk
			print("No local repository available on disk. Start download ...")
			self.downloadBundle(gBundleFile)

		return gBundleFile

	def downloadBundle(self, gBundleFile):
		"""Clear and download the bundle file into a temporary location along with its metadata"""

		repoLocalPath = self._pathLib.getBundleFilePath()

		# Delete existing bundle file
		if os.path.exists(repoLocalPath):
			os.remove(repoLocalPath)
		
		# Local bundle file not yet downloaded
		self.getGoogleApi().downloadFile(repoLocalPath, gBundleFile['id'])

		# Update the metadata
		self.updateBundleMetadata(gBundleFile, gitLib.getBunldeHead(repoLocalPath))

		print("New version downloaded (" + self.printMetadata(gBundleFile) + ")")

	def updateBundleMetadata(self, gBundleFile, head):
		repoMetadataPath = self._pathLib.getJsonFilePath()

		# Delete existing metadata file
		if os.path.exists(repoMetadataPath):
			os.remove(repoMetadataPath)

		# Create json file
		metadata = {
			google.F_ID: gBundleFile[google.F_ID],
			google.F_VERSION: gBundleFile[google.F_VERSION],
			google.F_TRASHED: gBundleFile[google.F_TRASHED],
			google.F_SIZE: gBundleFile[google.F_SIZE],
			google.F_MODIFIED_TIME: gBundleFile[google.F_MODIFIED_TIME],
			gitLib.FT_HEAD: head,
		}
		utilities.writeJson(metadata, repoMetadataPath)

	def printMetadata(self, gBundleFile):
		result = "ID: {id}, Name: {name}, Version: {version}, Size: {size} B ({hSize}), Modified: {modifiedTime}, HeadRevision: {headRevision}".format(\
			id = gBundleFile[google.F_ID],\
			name = gBundleFile[google.F_NAME],\
			version = gBundleFile[google.F_VERSION],\
			size = gBundleFile[google.F_SIZE],\
			hSize = utilities.humansize(gBundleFile[google.F_SIZE]),\
			modifiedTime = gBundleFile[google.F_MODIFIED_TIME],\
			headRevision = gBundleFile[google.F_HEAD_REVISION_ID])
		return result

	def getGoogleApi(self):
		"""Return an instance of the google api object"""
		if self._gapi is None:
			self._gapi = google.GoogleServiceApi()
		return self._gapi

	def readMetadata(self):
		return utilities.readJson(self._pathLib.getJsonFilePath())