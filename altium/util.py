prettydict = {  'esr' : 'ESR',
                'uuid' : 'UUID',
                'bjt' : 'BJT',
                'mosfet' : 'MOSFET',
                'ic' : 'IC'}

def prettify(s):
    words = s.lower().replace('_', ' ').split()
    return ' '.join([prettydict.get(word, word.capitalize()) for word in words])
