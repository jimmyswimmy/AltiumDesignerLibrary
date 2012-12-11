import os, datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from session import SqliteSessionInterface
import util

CONFIG_FILE = 'altium.cfg'

app = Flask(__name__)
CONFIG_PATH = os.path.join(app.root_path, CONFIG_FILE)
app.config.from_object('altium.config')
app.config.from_pyfile(CONFIG_PATH, silent=True)
util.save_config(app.config, CONFIG_PATH)

# Server-side sessions

path = app.config['SESSION_PATH']                   
if not os.path.exists(path):
    os.mkdir(path)
    os.chmod(path, int('700', 8))
app.session_interface = SqliteSessionInterface(path)


# Initial check of the library to establish SVN data
library = util.SVNLibrary()
library.check()
db = SQLAlchemy(app)

    
import hooks
import models

models.create()

import views
