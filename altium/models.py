from altium import db

# These are fields that every table must have for the model to work properly,
# but aren't fields that we generally want to display to the user.
HIDDEN_FIELDS = ('uuid', 'id')

components = {}
ok = False

def create():
    global components, ok
    components = {}
    try:
        # Models are auto-generated, because our database schema is really simple
        # There's a table for each component type
        meta = db.Model.metadata
        meta.reflect(db.engine)
    
        # Model generation happens here.
        # A new model class is created for each table in the database.
        # All the models are stored in the 'components' dictionary, which the rest of the application uses as the overall model.
        for name, table in meta.tables.items():
            cls = type(str(name), (db.Model, object), {'__table__' : table,'properties' : table.c.keys()})
            components[name] = cls
        ok = True
    except Exception, e:
        ok = False
        print e
    