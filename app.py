"""
This module contains a function to print the current application version
and exit the program.
"""
import sys
VERSION="v0.0.1"
def current_app_ver(version):
    '''
    Function print system Version then Exit
    '''
    print(version)
    sys.exit()
current_app_ver(VERSION)
