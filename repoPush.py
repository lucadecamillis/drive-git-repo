#!/usr/bin/env python3

from core import repoLib

def main():
	"""Push local repository changes to google drive"""
	lib = repoLib.RepoLib()
	lib.push()

if __name__ == '__main__':
	main()