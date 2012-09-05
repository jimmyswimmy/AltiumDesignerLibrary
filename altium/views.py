from flask import flash, render_template, url_for, redirect, request
from altium import app, db, svn_client
import config
import forms
import datetime
import models
import util
import uuid
import pysvn
import os

def get_library_data():
    sch = svn_client.list(config.SVN_URL + config.SVN_SCH_PATH)
    sch = [entry[0].data['path'] for entry in sch if entry[0].data['kind'] == pysvn.node_kind.file and entry[0].data['path'].lower().endswith('.schlib')]
    sch = [os.path.splitext(os.path.split(s)[1])[0] for s in sch]
    ftpt = svn_client.list(config.SVN_URL + config.SVN_FTPT_PATH)
    ftpt = [entry[0].data['path'] for entry in ftpt if entry[0].data['kind'] == pysvn.node_kind.file and entry[0].data['path'].lower().endswith('.pcblib')]
    ftpt = [os.path.splitext(os.path.split(s)[1])[0] for s in ftpt]
    return sch, ftpt

def get_table_data(name, order_by=None):
    component = models.components[name]
    properties = sorted(component.properties)
    for field in models.HIDDEN_FIELDS:
        properties.remove(field)
    headers = [util.prettify(property) for property in properties]
    rows = [(x.id, x.uuid, [getattr(x, field) for field in properties]) for x in component.query.all()]
    return headers, rows

@app.route('/', methods=['GET', 'POST'])
def index():
    tables = db.Model.metadata.tables.keys()
    return render_template('index.html', tables=tables)

@app.route('/table', methods=['GET','POST'])
def table():
    name = request.args['name']
    headers, rows = get_table_data(name)
    return render_template('table.html', headers=headers , data=rows, name=name)

@app.route('/edit', methods=['GET','POST'])
def edit():
    name = request.args['name']
    id = int(request.args['id'])
    print get_library_data()
    Component = models.components[name]
    Form = forms.create_form(Component)
    form = Form()
    component = Component.query.get(id)
    if form.validate_on_submit():
        form.populate_obj(component)
        db.session.add(component)
        db.session.commit()
        flash("The component was edited successfully.", "success")
        return redirect(url_for('table', name=name))
    form = Form(obj=component)
    return render_template('edit.html', form=form)

@app.route('/new', methods=['GET','POST'])
def new():
    name = request.args['name']
    Component = models.components[name]
    Form = forms.create_form(Component)
    form = Form()
    if form.validate_on_submit():
        component = Component()
        form.populate_obj(component)
        component.uuid = str(uuid.uuid4())
        db.session.add(component)
        db.session.commit()
        flash("The new component was created successfully.", "success")
        return redirect(url_for('table', name=name))
    return render_template('edit.html', form=form)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    name = request.args['name']
    id = int(request.args['id'])
    Component = models.components[name]
    component = Component.query.get(id)
    db.session.delete(component)
    db.session.commit()
    return redirect(url_for('table', name=name))
