#!/bin/env python3
"""
Pylint validator file for pylinter
"""
import os
import pylinter


# Example exlusion that will exclude relative files/directories
EXCLUDED_FILES = [
    '.git',
    '.idea',
]
# Exclude every file/directory included
EXCLUDED_GLOBAL = ['__pycache__']


if __name__ == '__main__':
    pylinter.run(EXCLUDED_FILES, EXCLUDED_GLOBAL, os.getcwd())
