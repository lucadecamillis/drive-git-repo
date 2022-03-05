#!/usr/bin/env python3

from core import repoLib

def main():
	"""Initialize a new repository on google drive
	If the repository is already initialized, throw an exception"""
	lib = repoLib.RepoLib()
	lib.init()

if __name__ == '__main__':
	main()