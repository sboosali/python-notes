from collections import OrderedDict
from multimethod import multimethod

from util import *
import op
import reduce
import config


edges = defaultdict(lambda: default)
@decorator
def edge(f):
    '''decorated by `edge` means:

    * it receives an operator with its operands
    * it streams edges

    '''
    edges[f.__name__] = f
    f.__annotations__.update({'operator': op.Op,
                              'operands': tuple,
                              'return': '[Edge]'})
    f = typecheck(f)
    return f

def Graph(tree):
    '''get edges from the parse

    memoization saves each subtree as it's reduced (whose leaves are by construction other reduced subtrees).
    '''
    f = memoize(reduce.reduce, cache=OrderedDict())
    tree.fold(f)

    graph = [(verb, nouns) for ((verb, nouns), _) in f.__cache__.items()]

    verbs = [(verb, nouns) for (verb, nouns) in graph if isinstance(verb, op.Op)]

    edges = [edge for (verb, nouns) in verbs for edge in get_edges(verb, nouns)]

    nouns = [noun for (noun, _) in graph if isinstance(noun, str)]

    nodes = remove_duplicates(node for edge in edges for node in edge.nodes)

    return nouns, verbs, nodes, edges

def Head(nouns: [str], verbs: [(str, [str])]) -> str:
    '''returns a noun from a noun list and a verb list. which comes from a line, that the next line might use it.
    '''

    verb, _nouns = verbs[-1]
    if _nouns:
        head = reduce.reduce(verb, _nouns)
    else:
        head = nouns[0]

    return head


def get_edges(operator, operands):
    edge = operator.means
    edge = edges[edge]
    # return the generator, over which the caller iterates
    return edge(operator, operands)

class Edge(tuple):
    def __new__(cls, label: str, nodes: [str]):
        self = super().__new__(cls, (label,) + tuple(nodes))
        self.label = label
        self.nodes = nodes
        return self

@edge
def default(operator, operands):
    '''the default edge
    '''
    label = operator.means
    nodes = operands
    yield Edge(label, nodes)

@edge
def more(operator, operands):
    label = operator.means
    node, = operands
    # TODO "+" -> awkward semantics-on-syntax dependency
    nodes = [node, '+ %s' % node]
    yield Edge(label, nodes)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
