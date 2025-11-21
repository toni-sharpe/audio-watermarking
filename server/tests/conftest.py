"""
Configuration for pytest to enable imports from parent server directory
"""
import sys
import os

# Add the parent directory (server/) to the Python path
# so tests can import modules like 'app', 'db_config', etc.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
