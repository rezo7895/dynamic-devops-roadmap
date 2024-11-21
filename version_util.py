"""
functiont that print the app version.
"""
import sys
VERSION = "v0.0.2"
def current_app_ver(version):
    """
    Function to print system version and exit.
    """
    print(f"App Version: {version}")
    sys.exit(0)
if __name__ == "__main__":
    current_app_ver(VERSION)
