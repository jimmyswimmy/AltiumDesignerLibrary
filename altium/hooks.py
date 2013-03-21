from flask import url_for
from altium import app
import urlparse
from util import prettify

def static(path):
    root = app.config.get('STATIC_ROOT')
    if root is None:
        return url_for('static', filename=path)
    else:
        return urlparse.urljoin(root, path)

def table_image(table):
    return static('images/%s.jpg' % table)

def sizeof(num):
    for x in ('bytes','kB','MB','GB','TB'):
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "Real Big"

@app.context_processor
def context_processor():
    return dict(static=static, table_image=table_image, prettify=prettify, zip=zip, sizeof=sizeof)
