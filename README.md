# Drive Git Repo

## Share your git repository on google drive

Store your git repository on google drive using the bundle functionality of git. The scripts push and pull automatically your changes from and to the remote git bundle file starting from a local git repository folder.

The scripts use the google drive api (<https://developers.google.com/api-client-library/python/>) and need a git client installed on the local machine.

---

## repoInit

Initialize the repository on google drive. Usage:

```
$ repoInit.py -g PATH_TO_GIT_REPOSITORY
```

## repoPush

Pushes local commits to the remote repository on google drive. Usage:

```
$ repoPush.py -g PATH_TO_GIT_REPOSITORY
```

Requires the repository initialized on google drive.

## repoSync

Sync (or Clone if the local repository does not exist) the remote repository with the local git repository. Usage:

```
$ repoSync.py -g PATH_TO_GIT_REPOSITORY
```

Requires the repository initialized on google drive.

## Install Instruction

### Windows

1. Install Python 3 (<https://www.python.org/downloads/windows/>). Make sure to add the python executable to the PATH environment variable (<https://docs.python.org/3/using/windows.html>)

1. Install Git (<https://git-scm.com/download/win>)

1. Run the set up script ```install/set_up_win.bat```

2. Create the file ```credentials.json``` following the instruction at <https://developers.google.com/workspace/guides/create-credentials> and copy the file to ```%userprofile%\.credentials\```

### Linux

1. Install python3 and git from your Linux distribution

1. Run the set up script ```install/set_up_linux.sh```

2. Create the file ```credentials.json``` following the instruction at <https://developers.google.com/workspace/guides/create-credentials> and copy the file to ```~/.credentials/```