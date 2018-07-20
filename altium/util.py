import threading
import os
import time
import datetime
import svn.remote
import tempfile

def total_seconds(td):
    return td.days * 60 * 60 * 24 + td.seconds

# Replacements for things like acronyms that don't prettify() well
PRETTYDICT = {  'esr' : 'ESR',
                'uuid' : 'UUID',
                'bjt' : 'BJT',
                'mosfet' : 'MOSFET',
                'ic' : 'IC',
                'scr' : 'SCR',
				'icanalog' : 'IC Analog',
				'icdigital' : 'IC Digital',
				'icmemory' : 'IC Memory',
				'icpower' : 'IC Power', 
				'icinterface' : 'IC Interface'}
def prettify(s):
    words = s.lower().replace('_', ' ').split()
    return ' '.join([PRETTYDICT.get(word, word.capitalize()) for word in words])

def save_config(config, filename):
    with open(filename, 'w') as fp:
        for key, value in config.items():
            # Config values must be basic types, timedeltas not allowed
            if isinstance(value, datetime.timedelta):
                value = int(total_seconds(value))
            fp.write('%s = %s\n' % (key, repr(value)))

def svnjoin(*parts):
    return '/'.join([part.strip('/') for part in parts])

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
        except Exception as e:
            print("Exception in ThreadWorker: %s" % e)

class SVNLibrary(ThreadWorker):
    def __init__(self, update_rate=10.0):
        super(SVNLibrary, self).__init__(self.continuous_update, update_rate)
        self.svn_url = None
        self.svn_sym_path = None
        self.svn_ftpt_path = None
        self.sym_index = {}
        self.ftpt_index = {}
        if update_rate:
            self.start()
    
    @property
    def sym(self):
        return self.sym_index.keys()
    
    @property
    def ftpt(self):
        return self.ftpt_index.keys()
    
    def continuous_update(self, update_rate):
        while True:
            self.update()
            time.sleep(update_rate)
    
    def check(self):
        try:
            self.update(silent=False)
            return None
        except Exception as e:
            return str(e)
            
    def update_svn(self):
        from altium import app
        url = app.config['ALTIUM_SVN_URL']
        sym_path = app.config['ALTIUM_SYM_PATH']
        ftpt_path = app.config['ALTIUM_FTPT_PATH']
        if (self.svn_url != url) or (self.svn_sym_path != sym_path) or (self.svn_ftpt_path != ftpt_path):
            self.tmp_dir = tempfile.mkdtemp()
            print("Checking SVN repository %s into %s" % (url,self.tmp_dir))
            r = svn.remote.RemoteClient(url)
            r.checkout(self.tmp_dir)
            self.svn_repos = r
            self.svn_url = url
            self.svn_sym_path = sym_path
            self.svn_ftpt_path = ftpt_path
            return r
        else:
            print("Updating cached SVN repository")
            self.svn_repos.run_command('update',[self.tmp_dir], return_binary=True)
            return self.svn_repos

    def update(self, silent=True):
        from altium import app
        sym_path = app.config['ALTIUM_SYM_PATH']
        ftpt_path = app.config['ALTIUM_FTPT_PATH']
        try:
            repos = self.update_svn()
            indices = []
            for path, ext in [(sym_path, '.schlib'), (ftpt_path, '.pcblib')]:
                all_paths = list(repos.list(extended=True, rel_path=path))
                file_objects = list(filter(lambda x : x['kind'] == 'file' and x['name'].lower().endswith(ext), all_paths))
                file_paths = [os.path.join(path, entry['name']) for entry in file_objects]
                last_authors = [entry['author'] for entry in file_objects]
                file_sizes = [entry['size'] for entry in file_objects]
                file_names = [os.path.split(s)[1] for s in file_paths]
                base_names = [os.path.splitext(s)[0] for s in file_names]
                index = {}
                for name, path, author, size in zip(base_names, file_paths, last_authors, file_sizes):
                    index[name] = {'path': path, 'author':author, 'size':size}
                indices.append(index)
            self.sym_index, self.ftpt_index = indices
        except Exception as e:
            import traceback, sys
            traceback.print_exc(file=sys.stderr)
            self.sym_index, self.ftpt_index = ({},{})
            if not silent:
                raise e

    def get_symbol_file(self, name):
        fullpath = self.sym_index[name]['path']
        filename = fullpath.split('/')[-1]
        return filename, self.svn_repos.cat(fullpath)
    
    def get_footprint_file(self, name):
        svn_client = pysvn.Client()
        fullpath = self.ftpt_index[name]['path']
        filename = fullpath.split('/')[-1]
        return filename, self.svn_repos.cat(fullpath)
        
if __name__ == "__main__":
    s = SVNLibrary(update_rate=None)
    s.check()
