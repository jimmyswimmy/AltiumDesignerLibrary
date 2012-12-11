import os, datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import util

CONFIG_FILE = os.path.abspath('altium.cfg')

app = Flask(__name__)
app.config.from_object('altium.config')
app.config.from_pyfile(CONFIG_FILE, silent=True)
util.save_config(app.config, CONFIG_FILE)

# Initial check of the library to establish SVN data
library = util.SVNLibrary()
library.check()
db = SQLAlchemy(app)

    
import hooks
import models

models.create()

import views
