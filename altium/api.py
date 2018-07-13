from flask import request, make_response
from altium import app
from . import models

@app.route('/api/parts/get', methods=['GET'])
# Get part by uuid
def parts_get():
    tables = list(models.components.keys())
    _format = request.args.get('format', 'json')
    data = get_table_dataset(table)
    
    exported_data = data.json
    
    # Export in appropriate format    
    response = make_response(exported_data)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = 'attachment; filename=%s.%s' % (table, _format)
    
    return response

# Update part with uuid
