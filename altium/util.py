import threading
import os
import time
import datetime

# Replacements for things like acronyms that don't prettify() well
PRETTYDICT = {  'esr' : 'ESR',
                'uuid' : 'UUID',
                'bjt' : 'BJT',
                'mosfet' : 'MOSFET',
                'ic' : 'IC'}
def prettify(s):
    words = s.lower().replace('_', ' ').split()
    return ' '.join([PRETTYDICT.get(word, word.capitalize()) for word in words])

def save_config(config, filename):
    with open(filename, 'w') as fp:
        for key, value in config.items():
            # Config values must be basic types, timedeltas not allowed
            if isinstance(value, datetime.timedelta):
                value = int(value.total_seconds())
            fp.write('%s = %s\n' % (key, repr(value)))

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
    def __init__(self, func, *args, **kwargs):
        super(ThreadWorker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.setDaemon(True)

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
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
    
    def check(self):
        try:
            self.update(silent=False)
            return None
        except Exception, e:
            return str(e)
        
    def update(self, silent=True):
        from altium import app
        url = app.config['ALTIUM_SVN_URL']
        sym_path = app.config['ALTIUM_SYM_PATH']
        ftpt_path = app.config['ALTIUM_FTPT_PATH']
        try:
            import pysvn
            svn_client = pysvn.Client()
            retval = []
            for path, ext in [(sym_path, '.schlib'), (ftpt_path, '.pcblib')]:
                l = svn_client.list(url + path)
                l = [entry[0].data['path'] for entry in l if entry[0].data['kind'] == pysvn.node_kind.file and entry[0].data['path'].lower().endswith(ext)]
                l = [os.path.splitext(os.path.split(s)[1])[0] for s in l]
                retval.append(l)
            self.sym, self.ftpt = retval
        except Exception, e:
            self.sym, self.ftpt =  ([],[])
            if not silent:
                raise e