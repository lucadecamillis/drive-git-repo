from __future__ import print_function
import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

from core import args
from core import utilities

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/token.pickle
# SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive.file']
REPO_FOLDER_NAME = 'Repositories1'

F_ID = 'id'
F_NAME = 'name'
F_MIME_TYPE = 'mimeType'
F_TRASHED = 'trashed'
F_PARENT = 'parent'
F_PARENTS = 'parents'
F_FILES = 'files'
F_SIZE = 'size'
F_VERSION = 'version'
F_HEAD_REVISION_ID = 'headRevisionId'
F_REVISIONS = 'revisions'
F_MODIFIED_TIME = 'modifiedTime'

def getMetadataFields():
	return (F_ID, F_MIME_TYPE, F_NAME, F_TRASHED, F_SIZE, F_VERSION, F_HEAD_REVISION_ID, F_MODIFIED_TIME)

def getMediaFileUpload(fileToUploadPath):
	return MediaFileUpload(fileToUploadPath, mimetype='application/binary')

def containsRevision(revisions, revisionId):
	for revision in revisions:
		if revision[F_ID] == revisionId:
			return True

	# The head revision hasn't been found
	return False

class GoogleServiceApi:
	"""Google Service Api factory"""

	# CTOR
	def __init__(self):
		self._service = None
		self._repoFolder = None
		print("Google lib created")

	def getCredentials(self):
		"""Shows basic usage of the Drive v3 API.
		Prints the names and ids of the first 10 files the user has access to.
		"""
		creds = None
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		credential_dir = self.getCredentialsFolder()
		token_path = os.path.join(credential_dir, 'token.json')

		if os.path.exists(token_path):
			creds = Credentials.from_authorized_user_file(token_path, SCOPES)
		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				credentials_path = os.path.join(credential_dir, 'credentials.json')
				flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open(token_path, 'w') as token:
				token.write(creds.to_json())
		return creds

	def getCredentialsFolder(self):
		home_dir = os.path.expanduser('~')
		credential_dir = os.path.join(home_dir, '.credentials')
		if not os.path.exists(credential_dir):
			os.makedirs(credential_dir)
		return credential_dir

	def getService(self):
		print('Getting Google Api Service ...')

		if self._service is None:
			print('Service not yet initialized. Initializing ...')
			creds = self.getCredentials()
			self._service = build('drive', 'v3', credentials=creds)
			print('Service initialized')
		return self._service

	def createRepo(self, fileToUploadPath, repoFileName):
		"""Upload a new bundle file on drive. If the file already exists, throw an exception"""

		# Check that the file hans't been previously uploaded
		driveRepo = self.getRepo(repoFileName)

		if driveRepo is None:
			# Get the repo folder
			repoFolder = self.getRepoFolder()

			# Upload the repository
			return self.uploadFile(fileToUploadPath, repoFileName, repoFolder[F_ID])
		else:
			raise Exception("The repository '" + repoFileName + "' already initialized on the google drive. Cannot initialize the repository")

	def updateRepo(self, fileToUploadPath, googleRepoId):
		"""Update a new version of the repository"""

		print('Uploading file "' + fileToUploadPath + '" to google repository id ' + googleRepoId + " ...")

		# Get the repo folder
		repoFolder = self.getRepoFolder()

		# Upload the repository
		fileContent = getMediaFileUpload(fileToUploadPath)

		result = (self
			.getService()
			.files()
			.update(
				fileId=googleRepoId,
				media_body=fileContent)
			.execute())

		print('Upload complete')

		return result

	def checkFolderExists(self, folderName):
		print("Trying to get folder with name: '" + folderName + "' ...")
		return self.getSingleQueryResult(F_NAME + "='" + folderName + "'", None)

	def createFolder(self, folderName, parentID):
		body = {
			F_NAME: folderName,
			F_MIME_TYPE: 'application/vnd.google-apps.folder'
		}
		if parentID:
			body[F_PARENT] = [{F_ID: parentID}]
		root_folder = self.getService().files().create(body = body).execute()
		return root_folder

	def getRepo(self, repoFileName):
		"""Returns the repository bundle file using the given name"""

		# Retrieve the repository folder
		repoFolder = self.getRepoFolder()

		# Write the query
		query = "{name}='{repoName}' and '{folderId}' in {parents}"\
			.format(name=F_NAME, repoName=repoFileName, folderId=repoFolder[F_ID], parents=F_PARENTS)

		# Execute the query along with the metadata fields
		return self.getSingleQueryResult(query, getMetadataFields())

	def executeQuery(self, queryString, fields):
		"""Execute the given query in string format"""

		filesProxy = self.getService().files()

		fieldsList = None
		if fields is not None:
			fieldsList = "files({0})".format(utilities.concatenateFields(fields))

		query = filesProxy.list(q=queryString, spaces='drive', fields=fieldsList)

		return query.execute()

	def getSingleQueryResult(self, queryString, fields):
		queryResult = self.executeQuery(queryString, fields)
		files = queryResult[F_FILES]
		nrResults = len(files)
		print("{0} files found for query '{1}'".format(nrResults, queryString))

		if nrResults == 0:
			return None
		elif nrResults == 1:
			return files[0]
		else:
			raise LookupError('Cannot get single result: ' + nrResults + ' files found for query ' + queryString + "'")

	def uploadFile(self, fileToUploadPath, driveName, parentID):
		fileContent = getMediaFileUpload(fileToUploadPath)

		fileBody = {F_NAME: driveName}
		if parentID is not None:
			fileBody[F_PARENTS] = [ parentID ]

		result = (self
			.getService()
			.files()
			.create(
				media_body=fileContent,
				body=fileBody)
			.execute())

		return result

	def downloadFile(self, destinationFilePath, driveFileId):
		downloadRequest = (self
			.getService()
			.files()
			.get_media(fileId=driveFileId))

		with open(destinationFilePath, 'wb') as file:

			print("Start downloading file " + driveFileId + " ...")
			mediaRequest = MediaIoBaseDownload(file, downloadRequest)

			while True:
				try:
					downloadProgress, done = mediaRequest.next_chunk()
				except HttpError as error:
					print('An error occurred: %s' % error)
					os.remove(destinationFilePath)
					return
				if downloadProgress:
					print('Download Progress: %d%%' % int(downloadProgress.progress() * 100))
				if done:
					print('Download Complete at ' + destinationFilePath)
					return

	def getFileMetaData(self, fileId):
		# Get the file along with metadata fields
		fileResult = (self
			.getService()
			.files()
			.get(
				fileId=fileId,
				fields=utilities.concatenateFields(getMetadataFields()))
			.execute())

	def getRepoFolder(self):
		"""Return an instance of the repository folder object"""

		if self._repoFolder is None:
			folderName = REPO_FOLDER_NAME
			print("Look for repository folder '" + folderName + "' ...")
			self._repoFolder = self.checkFolderExists(folderName)

			if not self._repoFolder:
				print("Folder '" + folderName + "' does not exist on drive. Create it ...")
				self._repoFolder = self.createFolder(folderName, None)
				print("Folder '" + folderName + "' created with ID='" + self._repoFolder[F_ID] + "'")
			else:
				print("Folder '" + folderName + "' retrieved with ID='" + self._repoFolder[F_ID] + "'")
		
		return self._repoFolder

	def deleteAllRevisionButHead(self, fileMetadata):
		"""Delete all revisions of the file except the head revision"""

		fileId = fileMetadata[F_ID]
		fileHeadRevisionId = fileMetadata[F_HEAD_REVISION_ID]

		revisionResponse = (self
			.getService()
			.revisions()
			.list(fileId=fileId)
			.execute())

		revisions = revisionResponse[F_REVISIONS]

		print(str(len(revisions)) + ' revisions found for fileId=' + fileId)

		if not containsRevision(revisions, fileHeadRevisionId):
			raise Exception('The head revision "' + fileHeadRevisionId + '" has not been found within the file revisions')

		for revision in revisions:
			# Delete all revisions except the head revision
			revisionId = revision[F_ID]
			if revisionId != fileHeadRevisionId:
				print('Deleting revision with id="' + revision[F_ID] + '". Revision last modified on ' + revision[F_MODIFIED_TIME])

				result = (self
					.getService()
					.revisions()
					.delete(
						fileId=fileId,
						revisionId=revisionId)
					.execute())