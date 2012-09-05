from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pysvn

app = Flask(__name__)
app.config.from_object('altium.config')

db = SQLAlchemy(app)

svn_client = pysvn.Client()

import hooks
import models
import views
