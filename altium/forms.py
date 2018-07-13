from wtforms import TextField, validators
from flask_wtf import Form
from . import models
from . import util

def create_component_form(model):
    dct = {}
    for key in model.properties:
        if key not in models.HIDDEN_FIELDS:
            dct[key] = TextField(util.prettify(key), id='id_%s' % key)
    return type('ComponentForm', (Form,), dct)

class PrefsForm(Form):
    ALTIUM_SVN_URL = TextField('SVN URL', validators=[validators.required()])
    ALTIUM_SYM_PATH = TextField('SchLib Path', validators=[validators.required()])
    ALTIUM_FTPT_PATH = TextField('PcbLib Path', validators=[validators.required()])
    
    SQLALCHEMY_DATABASE_URI = TextField('Database URI', validators=[validators.required()])
    
def create_prefs_form():
    from altium import app
    return PrefsForm(obj=util.AttributeWrapper(app.config))
