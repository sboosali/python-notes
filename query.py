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

def is_node(edge):
    label, *_ = edge
    return not label

def querify(edges):
    '''

    >>> querify([('', 'piracetam')])
    ([], ['piracetam'], [])

    >>> querify([('more', 'ACh', '+ ACh'), ('causes', '_', '+ ACh')])
    ([['causes', _, '+ ACh']], [], [['more', 'ACh', '+ ACh']])

    '''
    constants = [edge for edge in edges if '_' not in edge]
    variables = [edge for edge in edges if '_' in edge]
    variables = [list(replace('_', _, edge)) for edge in variables]

    constant_nodes, constant_edges = partition(is_node, constants)
    constant_nodes = [node for _, node in constant_nodes]
    constant_edges = [list(_) for _ in constant_edges]

    return variables, constant_nodes, constant_edges

def match():
    pass

def get(line):
    '''

    >>> db.test()
    >>> import graph
    >>> graph.save('causes', 'piracetam', '+ ACh')
    >>> graph.save('causes', 'choline', '+ ACh')

    >>> list(get('piracetam'))
    [['causes', 'piracetam', '+ ACh']]

    >>> list(get('_ -> + ACh'))
    [['causes', 'piracetam', '+ ACh'], ['causes', 'choline', '+ ACh']]

    >>> db.untest()

    '''

    parsed = parse.head(line)
    variable_edges, constant_nodes, constant_edges = querify(parsed.edges)

    for node in constant_nodes:
        hypernode = db.find_one({'node': node})
        if hypernode:
            for edge in hypernode['edges']:
                yield edge

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
