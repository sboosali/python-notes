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
import reduce
import op
from Edge import Edge
from Line import Line


class Graph(tuple):

    def __new__(cls, nodes=None, edges=None):
        if nodes is None: nodes = []
        if edges is None: edges = []
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


if __name__ == "__main__":
    import db
    with db.testing():
        import doctest
        doctest.testmod()
