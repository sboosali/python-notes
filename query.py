'''

'''
from util import *
import db
import parse


class Aught:
    def __eq__(self, other):
        return True
    def __repr__(self):
        return '_'
_ = Aught()

def querify(edges):
    '''

    >>> querify([('more', 'ACh', '+ ACh'), ('causes', '_', '+ ACh')])
    ([['causes', _, '+ ACh']], [['more', 'ACh', '+ ACh']])

    '''
    constants = [list(edge) for edge in edges if '_' not in edge]
    variables = [edge for edge in edges if '_' in edge]
    variables = [list(replace('_', _, edge)) for edge in variables]

    return variables, constants

def match():
    pass

def get(line):
    '''

    >>> db.test()
    >>> import graph
    >>> graph.save('causes', 'piracetam', '+ ACh')
    >>> graph.save('causes', 'choline', '+ ACh')

    >>> list(get('_ -> + ACh'))
    [['causes', 'piracetam', '+ ACh'], ['causes', 'choline', '+ ACh']]

    >>> db.untest()

    '''

    parsed = parse.head(line)
    variable_edges, constant_edges = querify(parsed.edges)

    for edge in variable_edges:
        label, *nodes = edge
        hyperedge = db.find_one({'edge': label})

        if hyperedge:
            _edges = hyperedge['nodes']

            for _edge in _edges:
                if edge==_edge:
                    yield _edge


if __name__ == "__main__":
    import doctest
    doctest.testmod()
