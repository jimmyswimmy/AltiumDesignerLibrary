from flask.ext.wtf import Form, TextField, validators
import models
import util

def create_form(model):
    dct = {}
    for key in model.properties:
        if key not in models.HIDDEN_FIELDS:
            dct[key] = TextField(util.prettify(key))
    return type('ComponentForm', (Form,), dct)
