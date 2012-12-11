'''
This is the base configuration file.
All configuration options live here
'''

SECRET_KEY = 'CHANGE_ME'
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:password@localhost/altium'
STATIC_ROOT = None

ALTIUM_SVN_URL = 'http://localhost/svn/repos'

ALTIUM_SYM_PATH = '/path/to/SYM'
ALTIUM_FTPT_PATH = '/path/to/FTPT'

SESSION_PATH = '.sessions'