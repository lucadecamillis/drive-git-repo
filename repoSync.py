#!/usr/bin/env python3

from core import repoLib

def main():
	"""Sync local repository from google drive"""
	lib = repoLib.RepoLib()
	lib.sync()

if __name__ == '__main__':
	main()