from flask import flash, render_template, url_for, redirect, request, make_response, session, g
from altium import app, db, library, CONFIG_PATH
import csv
import tablib
import re, uuid
import forms
import models
import util
import tempfile, zipfile, StringIO


def get_table_data(name, order_by=None):
    '''
    Return a 2-tuple of header and table row data:
    header = [(order_by, header),]
    row = [(id, uuid,  [col1,col2...coln]),]
    ''' 
    component = models.components[name]
    properties = sorted(component.properties)
    order_by = order_by or []
    for field in models.HIDDEN_FIELDS:
        properties.remove(field)
    headers = [(True if prop in order_by else False, prop) for prop in properties]
    rows = [(x.id, x.uuid, [getattr(x, field) or '' for field in properties]) for x in component.query.order_by(' '.join(order_by)).all()]
    return headers, rows

def get_table_dataset(name, order_by=None):
    headers, rows = get_table_data(name)
    order_by, headers = zip(*headers)
    data = tablib.Dataset(headers=['uuid'] + list(headers))
    for _id, uuid, fields in rows:
        data.append([uuid] + list(fields))
    return data

def get_database_zip():
    fp = StringIO.StringIO()
    with zipfile.ZipFile(fp, 'w') as z:
        for table in models.components.keys():
            z.writestr(table + '.csv', get_table_dataset(table).csv)
    return fp.getvalue()

def get_file_dataset(_file):
        reader = csv.reader(_file)
        headers = reader.next()
        data = tablib.Dataset(headers=headers)
        for row in reader:
            data.append(row)
        return data

def search_table(table, query, order_by=None):
    order_by = order_by or []
    component = models.components[table]
    properties = sorted(component.properties)
    for field in models.HIDDEN_FIELDS:
        properties.remove(field)
    pattern = re.compile(r'(\"[^\"]+\")|([^\s\"]+)')
    matches = pattern.findall(query)
    tokens = [a or b for a, b in matches]
    tokens = [token.replace('"', '').strip() for token in tokens]
    tokens = filter(None, tokens) 

    results = component.query
    for token in tokens:
        #ilike = '%%%s%%' % token
        regex = r'\m%s\M' % token        
        clauses = [getattr(component, p).op('~*')(regex) for p in properties]
        results = results.filter(db.or_(*clauses))
    results = results.distinct()
        
    headers = [(True if prop in order_by else False, prop) for prop in properties]
    rows = [(x.id, x.uuid, [getattr(x, field) or '' for field in properties]) for x in results.order_by(' '.join(order_by)).all()]
    
    return headers, rows
    
    
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    tables = models.components.keys()
    form = forms.create_prefs_form()
    if form.validate_on_submit():
        form.populate_obj(util.AttributeWrapper(app.config))
        util.save_config(app.config, CONFIG_PATH)
        warning = library.check()
        if warning:
            flash(warning, "error")
        flash("Your settings have been saved.", "success")
        models.create()
        return redirect(request.referrer)
    return render_template('settings.html', form=form, tables=tables)

@app.route('/', methods=['GET', 'POST'])
def index():
    tables = sorted(models.components.keys())
    info = {'svn_ok' : bool(library.sym) and bool(library.ftpt), 'db_ok' : models.ok}
    info.update({'syms' : len(library.sym), 'ftpts' : len(library.ftpt)})
    info.update({'db_tables' : len(tables)})
    if not library.sym and not library.ftpt:
        flash('There is a problem accessing the SVN repositories.  Check the <a href="%s">SVN Settings.</a>' % url_for('settings'), "warning")
    return render_template('index.html', tables=tables, info=info)

@app.route('/table', methods=['GET','POST'])
def table():
    name = request.args['name']
    order_by = request.args.get('order_by', '')
    headers, rows = get_table_data(name, order_by=[order_by])
    return render_template('table.html', tables = models.components.keys(), headers=headers , data=rows, name=name)

@app.route('/search', methods=['GET','POST'])
def search():
    table = request.args.get('table', '')
    query = request.args.get('query', '')
    headers, rows = search_table(table, query)
    if rows:
        #flash('Search returned %d results.' % len(rows), 'success')
        return render_template('search_results.html', tables = models.components.keys(), headers=headers , data=rows, name=table)
    else:
        flash('No search results were returned.', 'warning')
        return redirect(url_for('table', name=table))

@app.route('/export', methods=['GET','POST'])
def export():
    table = request.args.get('name', '')
    _format = request.args.get('format', 'json')
    
    if not table:
        table='adl_export'
        exported_data = get_database_zip()
        content_type = 'application/zip'
        _format = 'zip'
    else:
        data = get_table_dataset(table)
        
        if _format == 'json':
            exported_data = data.json
            content_type = 'application/json'        
        elif _format == 'xls':
            exported_data = data.xls
            content_type = 'application/vnd.ms-excel'
        elif _format == 'csv':
            exported_data = data.csv
            content_type = 'text/csv'
        else:
            raise Exception("Invalid format '%s'" % _format)
    
    # Export in appropriate format    
    response = make_response(exported_data)
    response.headers['Content-Type'] = content_type
    response.headers['Content-Disposition'] = 'attachment; filename=%s.%s' % (table, _format)
    
    return response

@app.route('/import', methods=['GET', 'POST'])
def _import():
    try:
        name = request.args.get('name', None)
        if not name:
            name = request.form['name']
    except Exception, e:
        print e

    # Entry point:  When in doubt: Stage 1.
    try: stage = int(request.form['stage'])
    except Exception, e:
        stage = 1
    if request.method == 'GET':
        stage = 1

    # Stage 2: We have a file from the user
    if stage == 2:
        _file = request.files['file']
        # Parse the file as a CSV
        try:
            data = get_file_dataset(_file)
        except Exception, e:
            msg = str(e)
            flash('There was an error parsing your file%s' % (': %s' % msg if msg else '.'), 'error')
        
        # Make sure the parts have uuids
        try:
            import_uuids = data['uuid']
        except KeyError, e:
            try:
                import uuid
                # Create uuid for all data in the absence of one
                data.append_col([str(uuid.uuid4()) for row in data], header='uuid')
                import_uuids = data['uuid']
                flash('The imported data contains no uuid column.  New uuids will be created.', 'info')
            except Exception, e:
                flash(str(e), 'error')
                return render_template('import_1.html', table=name, tables=models.components.keys())

        # Compare columns in the imported dataset with columns in the table and make sure they look sane
        c = models.components[name]
        import_columns_not_in_db = set(data.headers) - set(c.properties)
        db_columns_not_in_import = set(c.properties) - set(data.headers)

        # Warn the user about any discrepancies in the data
        if len(db_columns_not_in_import) == len(c.properties):
            flash('The imported file columns do not match the columns of this table. At least one column in the imported file must be present in the target table to perform an import.', 'error')
            return render_template('import_1.html', table=name, tables=models.components.keys())
        if len(db_columns_not_in_import) > 1:
            flash('Imported file does not have all the columns that this table does.  (It is missing %d columns) Some columns will be filled with default values.' % len(db_columns_not_in_import))
        if len(import_columns_not_in_db) > 0:
            flash('Imported file has columns that do not appear in this table. (It has %d extra columns)  Data from these columns were not imported.' % len(import_columns_not_in_db), 'warning')
        
        # Pull all the parts that need updating from the database
        parts_to_update = db.session.query(c).filter(c.uuid.in_(import_uuids)).all() # component objects that already exist in the db
        db_uuids = set([part.uuid for part in parts_to_update])
        
        # add a 'status' column that indicates whether we're creating new data or changing existing data
        uuid_idx = data.headers.index('uuid') 
        data.append_col(lambda row : row[uuid_idx] in db_uuids, header="status")
       
        for col in import_columns_not_in_db:
            del data[col]

        # save data in a way that will pickle with the session (skirting a bug in tablib)
        session['import_headers'] = data.headers
        data.headers = []
        session['import_dict'] = data.dict
        data.headers = session['import_headers']
        
        # Save all the uuids as their own list, for convenience
        session['import_uuids'] = import_uuids
        
        return render_template('import_2.html', table=name, tables=models.components.keys(), data=data)
    elif stage == 3:
        Component = models.components[name]

        import_uuids = session['import_uuids']
        import_data = tablib.Dataset(*session['import_dict'], headers=session['import_headers'])
        
        parts_to_update = db.session.query(Component).filter(Component.uuid.in_(import_uuids)).all()
        db_uuids = set([part.uuid for part in parts_to_update])
        new_uuids = set(import_uuids) - set(db_uuids)
                
        # Create new parts
        for uuid in new_uuids:
            idx = import_data['uuid'].index(uuid)
            row = import_data[idx]  # The row of data we wish to install
            c = Component()
            for key,value in zip(import_data.headers, row):
                if key != 'status' and key in Component.properties:
                    setattr(c, key, value)
            db.session.add(c) # Add to session to insert

        for part in parts_to_update:
            uuid = part.uuid        
            idx = import_data['uuid'].index(uuid)
            row = import_data[idx]  # The row of data we wish to update
            for key,value in zip(import_data.headers, row):
                if key != 'status' and key in Component.properties:
                    setattr(part, key, value)
            
        db.session.commit()

        message = 'Component database was updated.  '
        if new_uuids:
            message += '%d components were added.  ' % len(new_uuids)
        if db_uuids:
            message += '%d components were updated.  ' % len(db_uuids)
        
        flash(message , 'success')
        
        return redirect(url_for('table', name=name))
        
    else:
        # finally:
        return render_template('import_1.html', table=name, tables=models.components.keys())

@app.route('/edit', methods=['GET','POST'])
def edit():
    name = request.args['name']
    _id = int(request.args['id'])
    Component = models.components[name]
    Form = forms.create_component_form(Component)
    form = Form()
    component = Component.query.get(_id)
    if form.validate_on_submit():
        form.populate_obj(component)
        db.session.add(component)
        db.session.commit()
        flash("The component was edited successfully.", "success")
        return redirect(url_for('table', name=name))
    form = Form(obj=component)
    return render_template('edit.html',  tables = models.components.keys(), form=form, sch=library.sym, ftpt=library.ftpt)

@app.route('/new', methods=['GET','POST'])
def new():
    name = request.args['name']
    Component = models.components[name]
    Form = forms.create_component_form(Component)

    # Pop the form with template data if this is a duplicate
    template = request.args.get('template', None)        
    if template:
        template_component = Component.query.get(int(template))
        form = Form(obj=template_component)
    else:
        form = Form()

    if form.validate_on_submit():
        component = Component()
        form.populate_obj(component)
        component.uuid = str(uuid.uuid4())
        db.session.add(component)
        db.session.commit()
        flash('The new component was created successfully.', 'success')
        return redirect(url_for('table', name=name))
    return render_template('edit.html',  tables = models.components.keys(), form=form, sch=library.sym, ftpt=library.ftpt)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    name = request.args['name']
    _id = int(request.args['id'])
    Component = models.components[name]
    component = Component.query.get(_id)
    db.session.delete(component)
    db.session.commit()
    flash('The component was deleted successfully', 'success')
    return redirect(url_for('table', name=name))

@app.route('/symbols', methods=['GET'])
def symbols():
    return render_template('list.html', tables = models.components.keys(), data=library.sym_index, type='symbol')

@app.route('/footprints', methods=['GET'])
def footprints():
    return render_template('list.html', tables = models.components.keys(), data=library.ftpt_index, type='footprint')

@app.route('/get_file', methods=['GET'])
def get_file():
    name = request.args['name']
    _type = request.args['type']
    if _type == 'symbol':
        filename, file_data = library.get_symbol_file(name)
    elif _type == 'footprint':
        filename, file_data = library.get_footprint_file(name)
    else:
        return redirect(request.referrer)
    response = make_response(file_data)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
    
        
    
