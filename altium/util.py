import threading
from altium import app
import os
PRETTYDICT = {  'esr' : 'ESR',
                'uuid' : 'UUID',
                'bjt' : 'BJT',
                'mosfet' : 'MOSFET',
                'ic' : 'IC'}

def prettify(s):
    words = s.lower().replace('_', ' ').split()
    return ' '.join([PRETTYDICT.get(word, word.capitalize()) for word in words])


def get_library_data():
    try:
        import pysvn
        svn_client = pysvn.Client()
        sch = svn_client.list(app.config['SVN_URL'] + app.config['SVN_SCH_PATH'])
        sch = [entry[0].data['path'] for entry in sch if entry[0].data['kind'] == pysvn.node_kind.file and entry[0].data['path'].lower().endswith('.schlib')]
        sch = [os.path.splitext(os.path.split(s)[1])[0] for s in sch]
        ftpt = svn_client.list(app.config['SVN_URL'] + app.config['SVN_FTPT_PATH'])
        ftpt = [entry[0].data['path'] for entry in ftpt if entry[0].data['kind'] == pysvn.node_kind.file and entry[0].data['path'].lower().endswith('.pcblib')]
        ftpt = [os.path.splitext(os.path.split(s)[1])[0] for s in ftpt]
        return sch, ftpt
    except:
        return ([],[])

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
            print e
