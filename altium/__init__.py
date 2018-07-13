import os, datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .sqlite_session_interface import SqliteSessionInterface
from . import util

CONFIG_FILE = 'altium.cfg'

app = Flask(__name__)
CONFIG_PATH = os.path.join(app.root_path, CONFIG_FILE)
app.config.from_object('altium.config')
app.config.from_pyfile(CONFIG_PATH, silent=True)
util.save_config(app.config, CONFIG_PATH)

# Server-side sessions

path = app.config['SESSION_PATH']                   
path = os.path.join(app.root_path, '.sessions')
if not os.path.exists(path):
    os.mkdir(path)
    os.chmod(path, int('700', 8))
app.session_interface = SqliteSessionInterface(path)


# Initial check of the library to establish SVN data
library = util.SVNLibrary()
#library.check()
db = SQLAlchemy(app)

    
from . import hooks
from . import models

models.create()

from . import views
