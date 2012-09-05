from sqlalchemy import *
from altium import db
HIDDEN_FIELDS = ('uuid', 'id')
# Models are auto-generated, because our database schema is really stupid-simple
meta = db.Model.metadata
meta.reflect(db.engine)

class Resistor(db.Model):
    __table__ = meta.tables['resistor']
    properties = meta.tables['resistor'].c.keys()

class Capacitor(db.Model):
    __table__ = meta.tables['capacitor']
    properties = meta.tables['capacitor'].c.keys()

class Inductor(db.Model):
    __table__ = meta.tables['inductor']
    properties = meta.tables['inductor'].c.keys()

class Diode(db.Model):
    __table__ = meta.tables['diode']
    properties = meta.tables['diode'].c.keys()

class Crystal(db.Model):
    __table__ = meta.tables['crystal']
    properties = meta.tables['crystal'].c.keys()

class MOSFET(db.Model):
    __table__ = meta.tables['mosfet']
    properties = meta.tables['mosfet'].c.keys()

class BJT(db.Model):
    __table__ = meta.tables['bjt']
    properties = meta.tables['bjt'].c.keys()

class Connector(db.Model):
    __table__ = meta.tables['connector']
    properties = meta.tables['connector'].c.keys()

class IC(db.Model):
    __table__ = meta.tables['ic']
    properties = meta.tables['ic'].c.keys()
components = {'resistor':Resistor, 'capacitor':Capacitor, 'inductor':Inductor, 'diode':Diode, 'crystal':Crystal, 'mosfet':MOSFET, 'bjt':BJT, 'connector':Connector, 'ic':IC}
