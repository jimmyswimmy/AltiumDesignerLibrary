import threading
from altium import app
import os
import time

# Replacements for things like acronyms that don't prettify() well
PRETTYDICT = {  'esr' : 'ESR',
                'uuid' : 'UUID',
                'bjt' : 'BJT',
                'mosfet' : 'MOSFET',
                'ic' : 'IC'}

def prettify(s):
    words = s.lower().replace('_', ' ').split()
    return ' '.join([PRETTYDICT.get(word, word.capitalize()) for word in words])

class AttributeWrapper(object):    
    def __init__(self, z):
        object.__setattr__(self, 'data', z)

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError:
            return getattr(self.data, name)

    def __setattr__(self, name, value):
        try:
            self.data[name] = value
        except:
            return setattr(self.data, name, value)
        
class ThreadWorker(threading.Thread):
    def __init__(self, callable, *args, **kwargs):
        super(ThreadWorker, self).__init__()
        self.callable = callable
        self.args = args
        self.kwargs = kwargs
        self.setDaemon(True)

    def run(self):
        try:
            self.callable(*self.args, **self.kwargs)
        except Exception, e:
            print "Exception in ThreadWorker: %s" % e

class SVNLibrary(ThreadWorker):
    def __init__(self, update_rate=5.0):
        super(SVNLibrary, self).__init__(self.continuous_update, update_rate)
        self.sym = []
        self.ftpt = []
        self.start()
    
    def continuous_update(self, update_rate):
        while True:
            self.update()
            time.sleep(update_rate)
            
    def update(self):
        url = app.config['ALTIUM_SVN_URL']
        sym_path = app.config['ALTIUM_SYM_PATH']
        ftpt_path = app.config['ALTIUM_FTPT_PATH']
        try:
            import pysvn
            svn_client = pysvn.Client()
            sch = svn_client.list(url + sym_path)
            sch = [entry[0].data['path'] for entry in sch if entry[0].data['kind'] == pysvn.node_kind.file and entry[0].data['path'].lower().endswith('.schlib')]
            sch = [os.path.splitext(os.path.split(s)[1])[0] for s in sch]
            ftpt = svn_client.list(url + ftpt_path)
            ftpt = [entry[0].data['path'] for entry in ftpt if entry[0].data['kind'] == pysvn.node_kind.file and entry[0].data['path'].lower().endswith('.pcblib')]
            ftpt = [os.path.splitext(os.path.split(s)[1])[0] for s in ftpt]
            self.sym, self.ftpt = sch, ftpt
        except Exception, e:
            self.sym, self.ftpt =  ([],[])