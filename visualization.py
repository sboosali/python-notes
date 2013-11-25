import json

from util import *
import db
import config


def curry(edge, i, j):
    label, *nodes = edge
    return label

@strict
def cliquify(arc: 'edge') -> ['edge']:
    '''

    >>> cliquify(['< where', 'x', 'y', 'z'])
    [['< where', 'x', 'y'], ['< where', 'x', 'z'], ['< where', 'y', 'z']]

    '''
    label, *nodes = arc

    if len(nodes)==2:
        yield arc

    else:
        for (i,x), (j,y) in pairs(enumerate(nodes)):
            label = curry(arc, i,j)
            edge = [label, x, y]
            yield edge

def logic_graph_to_visual_graph(nodes, edges) -> json:
    '''
    : (n≥2)-ary edges => binary edges via cliques
    : python Edge/tuple => json object/dict

    d3 graph API
    force.nodes([nodes])
    force.links([links])
    link ~ binary edge
    link.source : node
    link.target : node
    (javascript dict = javascript object)

    V,S,O ~ verb, subject, object
    '''

    edges = [edge for arc in edges for edge in cliquify(arc)]
    links = [{'source': nodes.index(S), 'label': V, 'target': nodes.index(O)} for V,S,O in edges]
    nodes = [{'name': node} for node in nodes]
    graph = {'nodes': nodes, 'links': links}

    return json.dumps(graph)


if __name__ == "__main__":
    # import doctest
    # doctest.testmod()

    nodes, edges = db.graph()
    print(logic_graph_to_visual_graph(nodes, edges))
