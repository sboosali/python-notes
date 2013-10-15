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
>>> tree = associate(line)

# >>> tree
# ([' = '], [([' : '], [([' , '], ['x', ' , ', 'y', ' , ', 'z']), ' : ', 'a']), ' = ', 'b'])
>>> tree.unparse() == line
True

>>> tree = AST(tree)
>>> tree == Tree((('=',), [((':',), [((',',), [((',',), ['x', 'y']), 'z']), 'a']), 'b']))
True

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

    TODO test
    '''
    for num_spaces in get_spacing(line):
        for operator in operators:
            if operator.min_spaces <= num_spaces:
                yield operator.whiten(num_spaces)

def get_regex_from_binop(op):
    '''binary operators (unlike multinary operators):
    are chainable (e.g. 'x -> y -> z')
    can be on same line even if different (e.g. 'x => y ==> z')

    >>> assert get_regex_from_binop(Binop(' => ')) == r'(\ \=\>\ )'
    >>> assert get_regex_from_binop(Binop('==>', '=>')) == r'(\=\=\>|\=\>)'

    '''
    return '(%s)' % '|'.join(map(re.escape, op))

def get_regex_from_ternop(op):
    '''

    >>> assert get_regex_from_ternop(Ternop(' < ', ' where ')) == r'((?P<A>.*)\ \<\ (?P<B>.*)\ where\ (?P<C>.*))'

    '''
    operators = map(re.escape, op)
    operands = {'A': r'(?P<A>.*)',
                'B': r'(?P<B>.*)',
                'C': r'(?P<C>.*)'}
    regex = r'({A}{0}{B}{1}{C})'
    regex = regex.format(*operators, **operands)
    return regex


class CST(list):
    '''concrete syntax tree'''

    def __init__(self, op, tree):
        super().__init__(tree)
        self.op = op

    def map(self, f):
        '''maps a function onto each leaf (i.e. token or unparsed line) of the CST.
        `t` is either a leaf or a subtree
        CST : functor
        '''
        op = self.op
        tree = [f(t)
                if not isinstance(t, CST)
                else t.map(f)
                for t in self]
        return CST(op, tree)


def unparse(tree):
    '''
    >>> line = '3   =   1+2 * 3+4   /   7'
    >>> assert unparse(associate(line)) == line
    '''
    return ''.join(flatten(tree))

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

def parse_binop(op, line) -> 'str | CST str':
    '''parses a line with a binary operator.

    wraps the operator(s) in Sym to say "this token has been parsed as a symbol of some operator, don't reparse it".

    cleans the output
    e.g. ['1 ', ' + ', ' 2'] => ['1',Sym('+'),'2']

    >>> op = Binop('->')
    >>> assert parse_binop(op, 'x -> y -> z') == CST(op, ['x ', '->', ' y ', '->', ' z'])

    '''
    regex = get_regex_from_binop(op)
    tree = re.split(regex, line)

    # declare already parsed
    tree = [Sym(word) if word in op else word
            for word in tree]
    # e.g. ['', '+', 'ACh'] => ['+', 'ACh']
    tree = [word for word in tree if word.strip()]

    if len(tree)==1:
        # nothing parsed
        return line

    elif len(tree)==2:
        # unary operator
        # op, _ = tree
        # op = Unop(op)
        # return CST(op, tree)
        return line

    else:
        # binary operator
        return CST(op, tree)

def parse_ternop(op, line) -> 'str | CST str':
    '''parses a line with a ternary operator.

    filter away empty matches
    e.g. '[head]' =match=> ['', '[', 'head', ']', ''] =filter=> ['[', 'head', ']']

    wraps the operator(s) in Sym to say "this token is a symbol of an operator, don't reparse it".

    cleans the output
    e.g. ['', ' [ ', 'head', ' ] ', ''] => ['[', 'head', ']']

    >>> op = Ternop('~', 'but')
    >>> parse_ternop(op, 'x ~ y but z') == CST(op, ['x ', '~', ' y ', 'but', ' z'])
    True

    '''
    regex = get_regex_from_ternop(op)
    match = re.search(regex, line)
    if match:
        match = match.groupdict()
        operators = op
        operands = [match['A'], match['B'], match['C']]
        tree = stagger(operands, operators)

        # declare already parsed
        tree = [Sym(word) if word in op else word
                for word in tree]
        # e.g. ['', '[', 'context', ']', ''] => ['[', 'context', ']]
        tree = [word for word in tree if word.strip()]

        return CST(op, tree)

    else:
        return line

@typecheck
def parse_op(op: Op, line: str): # -> 'str | CST str':
    '''parses a line with some operator.

    tries to match some operators to a line,
    returning a Tree if it can, and
    the line itself if it can't.

    one step of a top-down operator-precedence parse.

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

    if isinstance(line, Sym):
        # already parsed
        return line

    if isinstance(op, Binop) or isinstance(op, Narop):
        return parse_binop(op, line)

    if isinstance(op, Ternop):
        return parse_ternop(op, line)

    return line

def associate(line: str) -> Tree:
    '''parse via recursive regex, into a concrete syntax tree.

    >>> associate('a -> b , c , d -> e').leaves()
    ['a', ' -> ', ['b', ' , ', 'c', ' , ', 'd'], ' -> ', 'e']
    '''

    # e.g. [Binop('<', '>'), Ternop('<', 'where')]
    operators = get_operators(grammar.OPERATORS, line)

    tree = line #Tree((Nulop(), [line]))
    for operator in operators:
        # each pass may or may not 'deepen' the tree
        if isinstance(tree, str):
            tree = parse_op(operator, tree)
        elif isinstance(tree, list):
            tree = tree.map(f=lambda line: parse_op(operator, line)) # g=lambda _: not _)
        else:
            raise PatternExhausted

    if not isinstance(tree, CST):
        tree = CST(Nulop(), [tree])

    return tree

@multimethod(str)
def _AST(s): return s
@multimethod(CST)
def _AST(cst):
    '''cast a CST to a Tree'''
    value = cst.op
    trees = [_AST(tree) for tree in cst]
    return Tree((value, trees))

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
    '''
    >>> cst = 'nullary'
    >>> ast = Tree('nullary')
    >>> AST(cst) == ast
    True

    >>> cst = [' + ', 'unary']
    >>> ast = Tree((Unop('+'), ['unary']))
    >>> AST(cst) == ast
    True

    >>> cst = ['a', ' -> ', ['b', ' , ', 'c', ' , ', 'd'], ' -> ', 'e']
    >>> ast = Tree((Op('->'), [(Op('->'), ['a', (Op(','), [(Op(','), ['b', 'c']), 'd'])]), 'e']))
    >>> AST(cst) == ast
    True
    '''
    def is_noun(word): return not isinstance(word, Sym)

    tree = _AST(tree)
    tree = left_associate(tree) # n-ary tree => unary|binary|ternary tree
    tree = tree.filter(f=is_noun, g=bool) # infix => prefix
    tree = tree.map(f=lambda _: _.strip(), g=bool) # ' , ' => ','
    return tree

def Graph(tree):
    '''
    '''
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
    cst = associate(line)
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

def note(lines):
    '''TODO'''


if __name__ == "__main__":
    import doctest
    doctest.testmod()
