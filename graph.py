from collections import OrderedDict

from util import *
from op import Op
import reduce
import config


def Graph(tree):
    '''get edges from the parse

    memoization saves each subtree as it's reduced (whose leaves are by construction other reduced subtrees).
    '''
    f = memoize(reduce.reduce, cache=OrderedDict())
    tree.fold(f)

    graph = [(verb, nouns) for ((verb, nouns), _) in f.__cache__.items()]

    verbs = [(verb, nouns) for (verb, nouns) in graph if isinstance(verb, Op)]

    edges = [(config.edges[verb.symbol],) + nouns for (verb, nouns) in verbs]

    nouns = [noun for (noun, _) in graph if isinstance(noun, str)]

    nodes = nouns

    return nouns, verbs, nodes, edges

def Head(nouns, verbs):
    verb, _nouns = verbs[-1]
    if _nouns:
        head = reduce.reduce(verb, _nouns)
    else:
        head = nouns[0]

    return head


if __name__ == "__main__":
    import doctest
    doctest.testmod()
