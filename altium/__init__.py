from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('altium.config')
try:
    app.config.from_envvar('ALTIUM_DESIGNER_LIBRARY_SETTINGS')
except:
    pass

db = SQLAlchemy(app)

import util
sch, ftpt = util.get_library_data()

import hooks
import models
import views
