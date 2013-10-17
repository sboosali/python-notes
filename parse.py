'''
=> associate => strip_infix => left_associate => edges =>

use "import parse" to document the parsing functions like so: "parse.head()"

    : :infix => :prefix

    x        => (node x)
    x , y    => (aliases x y ...)
    x ~ y    => (like x y ...)
    x = y    => (equals x y ...)
    x := y   => (define x y)
    x < y    => (subset x y ...)
    x : y    => (is_a x y)
    x -> y   => (edge "->" x y ...)

    x . y    => (conjunction x y ...)
    x ... y  => (ellipses x y)
    [x]      => (context x)
    word. x  => (parser "word" x)
    . x      => (comment x)

>>> line = 'x , y , z : a = b'
>>> tree = CST(line)

>>> tree
Tree((Binop(' = '), [(Binop(' : '), [(Binop(' , '), ['x', ' , ', 'y', ' , ', 'z']), ' : ', 'a']), ' = ', 'b']))
>>> unparse(tree)
'x , y , z : a = b'

>>> tree = AST(tree)
>>> tree
Tree((Binop('='), [(Binop(':'), [(Binop(','), [(Binop(','), ['x', 'y']), 'z']), 'a']), 'b']))

'''
from operator import itemgetter
import itertools
import re
from multimethod import multimethod
from collections import OrderedDict
from collections import namedtuple

from util import *
import grammar
from grammar import Op, Nulop, Unop, Narop, Binop, Ternop
import config
import make
from tree import Tree
import chain


def get_max_spaces(line: str):
    '''returns the maximum number of spaces in the line.

    >>> get_max_spaces('  ')
    2
    '''
    if ' ' in line:
        return max(len(list(xs))
                   for x,xs
                   in itertools.groupby(line)
                   if x==' ')
    else:
        return 0

def get_spacing(line, min_spaces=0):
    '''returns an iterator counting down from `max_spaces` to `min_spaces`

    >>> list(get_spacing(' '*2, min_spaces=1))
    [2, 1]
    '''
    max_spaces = max(get_max_spaces(line), min_spaces)
    spacing = reversed(range(min_spaces, 1+max_spaces))
    return spacing

@strict
def get_operators(operators, line):
    '''returns an operator of each precedence given the line to parse. 'precedence' means 'number of spaces', bounded below by the operator definition and bounded above by the number of spaces in the line.
    '''
    for num_spaces in get_spacing(line):
        for operator in operators:
            if operator.min_spaces <= num_spaces:
                yield operator.whiten(num_spaces)

class Sym(str):
    def __getattribute__(self, attr):
        '''transparently return a Sym for any str method call that returns a str.

        the line (regex) parsers wrap operators in Sym's, and the tree (recursive) parsers skip Sym's (meaning, "already parsed").

        >>> isinstance(Sym('Sym').strip(), Sym)
        True
        >>> isinstance(Sym('Sym').split(), list)
        True
        '''

        attr = super().__getattribute__(attr)
        if hasattr(attr, '__call__'):
            def symbolize(*args, **kwargs):
                ret = attr(*args, **kwargs)
                ret = Sym(ret) if isinstance(ret, str) else ret
                return ret
            return symbolize
        else:
            return attr

def unparse(tree):
    '''
    >>> line = '3   =   1+2 * 3+4   /   7'
    >>> assert unparse(CST(line)) == line
    '''
    return ''.join(flatten(tree.leaves()))

def parse_binop(op, line):
    '''parses a line with a binary operator.

    wraps the operator(s) in Sym to say "this token has been parsed as a symbol of some operator, don't reparse it".

    cleans the output
    e.g. ['1 ', ' + ', ' 2'] => ['1', Sym('+'), '2']

    >>> parse_binop(Binop(' -> '), 'x -> y -> z')
    Tree((Binop(' -> '), ['x', ' -> ', 'y', ' -> ', 'z']))
    '''

    regex = op.regex()
    trees = re.split(regex, line)

    # declare already parsed
    trees = [Sym(word) if word in op else word
            for word in trees]
    # e.g. ['', '+', 'ACh'] => ['+', 'ACh']
    trees = [word for word in trees if word.strip()]

    if len(trees)==1:
        # nothing parsed
        return Tree(line)

    elif len(trees)==2:
        # unary operator
        # op, _ = trees
        # op = Unop(op)
        return Tree(line)

    else:
        # binary operator
        return Tree((op, trees))

def parse_ternop(op, line):
    '''parses a line with a ternary operator.

    filter away empty matches
    e.g. '[head]' =match=> ['', '[', 'head', ']', ''] =filter=> ['[', 'head', ']']

    wraps the operator(s) in Sym to say "this token is a symbol of an operator, don't reparse it".

    cleans the output
    e.g. ['', ' [ ', 'head', ' ] ', ''] => ['[', 'head', ']']

    >>> op = Ternop('~', 'but')
    >>> assert parse_ternop(op, 'x ~ y but z') == Tree((op, ['x ', '~', ' y ', 'but', ' z']))
    '''
    regex = op.regex()
    match = re.search(regex, line)

    if match:
        match = match.groupdict()
        operators = op
        operands = [match['A'], match['B'], match['C']]
        trees = stagger(operands, operators)

        # declare operator symbols have been parsed
        trees = [Sym(word) if word in op else word
                for word in trees]
        # e.g. ['', '[', 'context', ']', ''] => ['[', 'context', ']]
        trees = [word for word in trees if word.strip()]

        return Tree((op, trees))

    else:
        return Tree(line)

@typecheck
def parse_op(op: Op, tree: Tree):
    '''parses a line (tree leaf) with some operator.

    tries to match some operators to a line,
    returning a Tree if it can, and
    the line itself if it can't.

    one step of a top-down operator-precedence parse.
    each pass may or may not 'deepen' the tree.

    >>> tree = Tree('line : str')
    >>> op = Binop(':')
    >>> assert parse_op(op, tree) == Tree((op, ['line', ' : ', 'str']))

    >>> parse_op(Binop('-'), '1+2')
    '1+2'
    >>> parse_op(Binop(' + '), '1+2')
    '1+2'
    >>> parse_op(Binop('+'), '1+2')
    ['1','+','2']
    >>> parse_op(Binop('+', '-'), '1+2-3')
    ['1','+','2','-','3']
    >>> parse_op(Ternop(' ? ', ' : '), 'cond ? then : else')
    ['cond', ' ? ', 'then', ' : ', 'else']

    '''
    line, _ = tree

    if isinstance(line, Sym):
        # already parsed
        return tree

    if isinstance(op, Binop) or isinstance(op, Narop):
        return parse_binop(op, line)

    if isinstance(op, Ternop):
        return parse_ternop(op, line)

    return tree

def CST(line: str) -> Tree:
    '''parse via recursive regex, into a concrete syntax tree.

    >>> CST('a -> b , c , d -> e').leaves()
    ['a', ' -> ', ['b', ' , ', 'c', ' , ', 'd'], ' -> ', 'e']
    '''

    # e.g. [Binop('=>', '==>'), Ternop('<', 'where')]
    operators = get_operators(grammar.OPERATORS, line)
    tree = Tree(line)

    for operator in operators:
        tree = tree.tmap(f=lambda leaf: parse_op(operator, leaf))

    if tree.is_leaf():
        # nothing parsed
        tree = Tree((Nulop(), [tree]))

    return tree

@typecheck
def left_associate(tree: Tree) -> Tree:
    value, trees = tree

    if isinstance(value, Binop):
        x, (op, _), y, *zs = trees

        x = left_associate(x)
        y = left_associate(y)
        left = Tree((Binop(op), [x, Tree(op), y]))

        if not zs:
            return left
        else:
            trees = [left] + zs
            return left_associate(Tree((value, trees)))

    else:
        trees = [left_associate(tree) for tree in trees]
        return Tree((value, trees))

def AST(tree):
    def is_noun(word): return not isinstance(word, Sym)

    tree = left_associate(tree) # n-ary tree => unary|binary|ternary tree
    tree = tree.filter(f=is_noun, g=bool) # infix => prefix
    tree = tree.map(f=lambda _: _.strip(), g=bool) # ' , ' => ','
    return tree

def Graph(tree):
    f = memoize(chain.reduce, cache=OrderedDict())
    tree.fold(f)
    graph = [(edge, nodes) for ((edge, nodes), _) in f.__cache__.items()]

    edges = [(edge, nodes) for (edge, nodes) in graph if nodes]
    head = f(*edges[-1])
    nodes = [node for (node, _) in graph if not _]

    return head, nodes, edges

def Verbs(edges):
    return [(config.verbs[edge.symbol],) + nodes for (edge, nodes) in edges]

Parsed = namedtuple('Parsed', 'head line cst ast nodes edges verbs')

@typecheck
def head(line: str) -> Parsed:
    cst = CST(line)
    ast = AST(cst)
    head, nodes, edges = Graph(ast)
    verbs = Verbs(edges)
    return Parsed(head, line, cst, ast, nodes, edges, verbs)

@typecheck
def body(line, head='') -> Parsed:
    tokens = line.split()
    starts_with_op = tokens[0] in config.operators
    prefix = head + get_max_spaces(line) if starts_with_op else ''
    line = prefix + line
    return parse.head(line)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
