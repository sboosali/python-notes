import json

from util import *
import config
from Edge import Edge


def curry(edge, i, j):
    label, *nodes = edge
    return label

@strict
def cliquify(arc: Edge) -> [Edge]:
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
            edge = Edge(label, [x, y], line=arc.line)
            yield edge

def logic_edge_to_visual_link(nodes, edge):
    V,S,O = edge
    link = {'source': nodes.index(S),
            'name': V,
            'target': nodes.index(O),
            'lineno': edge.line.lineno}
    return link

def logic_graph_to_visual_graph(nodes, edges) -> json:
    '''
    : (n≥2)-ary edges => binary edges via cliques
    : python Edge => json object

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
    links = [logic_edge_to_visual_link(nodes, edge) for edge in edges]
    nodes = [{'name': node} for node in nodes]
    graph = {'nodes': nodes, 'links': links}

    return graph


if __name__ == "__main__":
    #TODO doctest bug . trailing unseen char
    # import doctest
    # doctest.testmod()

    import db
    nodes, edges = db.graph()
    pp(logic_graph_to_visual_graph(nodes, edges))
