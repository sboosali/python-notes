from multimethod import multimethod

from util import *
import op
import config
from Line import Line
import syntax


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

class Edge(tuple):
    def __new__(cls, label: str, nodes: [str], line: Line = None):
        '''

        >>> edge = Edge('like', ['x','y'])
        >>> Edge(**edge.json) == edge
        True

        '''
        if line is None: line = Line('')
        if isa(line, dict): line = Line(**line)

        self = super().__new__(cls, (label,) + tuple(nodes))

        self.label = label
        self.nodes = nodes
        self.line = line

        return self

    @property
    def json(self):
        '''
        from Line import Line
        >>> line = Line('x < y where z', 'test.note', 1)
        >>> edge = Edge('subset_where', ['x','y','z'], line=line)
        >>> pp(edge.json)
        {   'label': 'subset_where',
            'line': {'file': 'test.note', 'text': 'x < y where z', 'lineno': 1},
            'nodes': ['x', 'y', 'z']}

        # identity
        >>> data = {'label': 'like', 'nodes': ['x', 'y'], 'line': {'text': 'x ~ y', 'file': '', 'lineno': 0}}
        >>> Edge(**data).json == data
        True

        '''
        return {'label': self.label,
                'nodes': self.nodes,
                'line': self.line.json}

    def format(self):
        operator = syntax.symbol[self.label]
        operands = self.nodes
        return operator.format(*operands)

    @classmethod
    def from_json(cls, edge):
        '''

        # identity
        >>> edge = Edge('like', ['x', 'y'])
        >>> Edge.from_json(edge.json) == edge
        True

        '''
        return Edge(**edge)

    @classmethod
    def from_iter(cls, edge):
        label, *nodes = edge
        return Edge(label, nodes)

    @classmethod
    def get(cls, operator, operands):
        '''
        return the generator, over which the caller iterates
        '''
        edge = operator.means
        edge = edges[edge]
        return edge(operator, operands)

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
