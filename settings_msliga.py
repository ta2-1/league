import os

PROJECT_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

SITE_ID = 2
execfile(os.path.join(PROJECT_DIR, 'settings.py'))
