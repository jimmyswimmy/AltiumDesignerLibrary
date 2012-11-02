from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('altium.config')

db = SQLAlchemy(app)

import util
library = util.SVNLibrary()

import hooks
import models
import views
