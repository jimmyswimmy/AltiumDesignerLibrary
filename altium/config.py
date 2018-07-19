'''
This is the base configuration file.
All configuration options live here
'''

SECRET_KEY = 'ALTIUM DESIGNER LIBRARY SECRET KEY 379164825'
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:password@localhost/altium'
STATIC_ROOT = None

ALTIUM_SVN_URL = 'svn://localhost/database'

ALTIUM_SYM_PATH = '/SYM'
ALTIUM_FTPT_PATH = '/FTPT'

SESSION_PATH = '.sessions'

TRACK_SQLALCHEMY_MODS = False
