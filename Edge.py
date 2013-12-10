from multimethod import multimethod

from util import *
import op
import config
from Line import Line


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

def get(operator, operands):
    '''
    usage: `import edge; edge.get()`
    return the generator, over which the caller iterates
    '''
    edge = operator.means
    edge = edges[edge]
    return edge(operator, operands)

class Edge(tuple):
    def __new__(cls, label: str, nodes: [str], line: Line= None):
        if line is None: line = Line('')

        self = super().__new__(cls, (label,) + tuple(nodes))
        self.__dict__ = {} #HACK for mutability so we don't need to thread the line through each parsing transformation

        self.label = label
        self.nodes = nodes
        self.line = line

        return self

def from_list(edge: iter) -> Edge:
    label, *nodes = edge
    return Edge(label, nodes)

@edge
def default(operator, operands):
    '''the default edge
    '''
    label = operator.means
    nodes = operands
    yield Edge(label, nodes)

def default_unop(operator, operands):
    symbol = str(operator)
    label = operator.means
    node, = operands
    nodes = [node, '%s %s' % (symbol, node)]
    yield Edge(label, nodes)

@edge
def more(operator, operands):
    return default_unop(operator, operands)

@edge
def less(operator, operands):
    return default_unop(operator, operands)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
