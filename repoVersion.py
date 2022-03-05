#!/usr/bin/env python3

from core import repoLib

def main():
	"""Print the current version of the repository on the drive"""
	lib = repoLib.RepoLib()
	lib.repoVersion()

if __name__ == '__main__':
	main()