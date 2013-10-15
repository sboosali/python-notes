from operator import itemgetter

import config


def reduce_node(node, _):
    return node
def reduce_edge(edge, nodes):
    operator = edge.symbol
    reducer = config.chain[operator]
    reducer = globals()[reducer]
    return reducer(edge, nodes)
def reduce(edge, nodes):
    return reduce_edge(edge, nodes) if nodes else reduce_node(edge, nodes)

def left(_, xs): return xs[0]
def right(_, xs): return xs[-1]
def join(x, ys): return (' %s ' % x).join(ys)
