'''
the DB API's input
'''
from util import *
import db
import parse
from Edge import Edge
import store


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

def from_edge(edge):
    '''
    take the first node, match input to each its edges
    '''
    edge = tuple(edge)
    label, *nodes = edge
    node = next(node for node in nodes if isa(node, str))

    vertex = db.find_one({'node': node})

    if vertex:
        arcs = vertex['edges']

        for arc in arcs:
            arc = Edge(**arc)
            if arc==edge:
                yield arc

def from_node(node):
    vertex = db.find_one({'node': node})
    if vertex:
        for arc in vertex['edges']:
            arc = Edge(**arc)
            yield arc

@typecheck
def get(line: str):
    '''
    generates all edges in a query, with some nodes variable,

    >>> store.save('causes', 'piracetam', '+ ACh')
    >>> store.save('causes', 'choline', '+ ACh')

    >>> list(get('piracetam'))
    [('causes', 'piracetam', '+ ACh')]

    >>> list(get('_ -> + ACh'))
    [('causes', 'piracetam', '+ ACh'), ('causes', 'choline', '+ ACh')]

    '''

    parsed = parse.string(line)
    variable_edges, constant_nodes, constant_edges = querify(parsed.graph.edges)

    for edge in variable_edges:
        yield from from_edge(edge)

    for edge in constant_edges:
        yield from from_edge(edge)

    for node in constant_nodes:
        yield from from_node(node)


if __name__ == "__main__":
    with db.testing():
        import doctest
        doctest.testmod()
