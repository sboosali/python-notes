'''

'''
from util import *
import parse


class Aught:
    def __eq__(self, other):
        return True
    def __repr__(self):
        return '_'
_ = Aught()

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

def get_edges(edge):
    label, *nodes = edge
    hyperedge = db.find_one({'edge': label})

    if hyperedge:
        hyperedges = hyperedge['nodes']

        for hyperedge in hyperedges:
            if edge==hyperedge:
                yield hyperedge

def get_edges_from_node(node):
    hypernode = db.find_one({'node': node})
    if hypernode:
        for edge in hypernode['edges']:
            yield edge

def get(line):
    global db #HACK
    import db
    '''

    >>> db.test()
    >>> import Graph
    >>> Graph.save('causes', 'piracetam', '+ ACh')
    >>> Graph.save('causes', 'choline', '+ ACh')

    >>> list(get('piracetam'))
    [['causes', 'piracetam', '+ ACh']]

    >>> list(get('_ -> + ACh'))
    [['causes', 'piracetam', '+ ACh'], ['causes', 'choline', '+ ACh']]

    >>> db.untest()

    '''

    parsed = parse.string(line)
    variable_edges, constant_nodes, constant_edges = querify(parsed.graph.edges)

    for node in constant_nodes:
        yield from get_edges_from_node(node)

    for edge in variable_edges:
        yield from get_edges(edge)

    for edge in constant_edges:
        yield from get_edges(edge)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
