'''


hypergraph
----------

hypergraph  <  bipartite graph  where A=nodes B=edges


node schema
-----------

{'node': str,
 'edges': [[str]]}


edge schema
-----------

{'edge': str,
 'nodes': [[str]]}


'''
from collections import OrderedDict

from util import *
import db
import reduce
import op
import Edge


class Graph(tuple):

    def __new__(cls, nodes, edges):
        self = super().__new__(cls, (nodes, edges))
        self.nodes = nodes
        self.edges = edges
        return self

    @classmethod
    def harvest(cls, tree):
        '''*harvest* edges from the parse *tree*

        memoization saves each subtree as it's reduced (whose leaves are by construction other reduced subtrees).
        '''
        f = memoize(reduce.reduce, cache=OrderedDict())
        tree.fold(f)

        graph = [(verb, nouns) for ((verb, nouns), _) in f.__cache__.items()]

        verbs = [(verb, nouns) for (verb, nouns) in graph if isinstance(verb, op.Op)]

        edges = [edge for (verb, nouns) in verbs for edge in Edge.get(verb, nouns)]

        nouns = [noun for (noun, _) in graph if isinstance(noun, str)]

        nodes = remove_duplicates(node for edge in edges for node in edge.nodes)
        head = Head(nouns, verbs)

        graph = Graph(nodes, edges)

        return head, graph

def Head(nouns: [str], verbs: [(str, [str])]) -> str:
    '''returns a noun from a noun list and a verb list.
    which comes from a line, that the next line might use it.
    '''

    verb, arguments = verbs[-1] # wikipedia.org/wiki/Argument_(linguistics)
    if arguments:
        head = reduce.reduce(verb, arguments)
    else:
        head = nouns[0] if nouns else None

    return head

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def save(*edge, collection=None):
    '''

    >>> db.test()

    # motivation: "x , y < z"
    >>> save(',', 'x', 'y')
    >>> pp(db.find_one({'node': 'y'}))
    {'edges': [[',', 'x', 'y']], 'node': 'y'}

    >>> save('<', 'y', 'z')
    >>> pp(db.find_one({'node': 'y'}))
    {'edges': [[',', 'x', 'y'], ['<', 'y', 'z']], 'node': 'y'}

    >>> pp(db.find_one({'node': 'x'}))
    {'edges': [[',', 'x', 'y']], 'node': 'x'}

    >>> pp(db.find_one({'edge': ','}))
    {'edge': ',', 'nodes': [[',', 'x', 'y']]}

    >>> pp(db.find_one({'edge': '<'}))
    {'edge': '<', 'nodes': [['<', 'y', 'z']]}

    # hyperedge: "a < b where c"
    >>> save('< where', 'a', 'b', 'c')
    >>> pp(db.find_one({'edge': '< where'}))
    {'edge': '< where', 'nodes': [['< where', 'a', 'b', 'c']]}

    >>> db.untest()

    '''
    if not collection: collection = db.collection()

    label, *nodes = edge
    if is_node(edge):
        save_node(label, collection=collection)
    else:
        save_edge(edge, collection=collection)

def save_edge(edge, collection=None):
    if not collection: collection = db.collection()
    label, *nodes = edge

    query = {'edge': label}
    update = {'$addToSet': {'nodes': edge}}
    collection.update(query, update, upsert=True)

    for node in nodes:
        save_node(node, edge, collection)

def save_node(node, edge=None, collection=None):
    if not collection: collection = db.collection()

    query = {'node': node}
    update = {'$addToSet': {'edges': edge}} if edge else {}
    collection.update(query, update, upsert=True)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
