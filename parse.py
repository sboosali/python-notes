'''
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

>>> text = 'x , y , z : a = b'
>>> line = text.split()

>>> tree = _CST(line)
>>> tree
([' = '], [([' : '], [([' , '], ['x', ' , ', 'y', ' , ', 'z']), ' : ', 'a']), ' = ', 'b'])
>>> unparse(tree) == text
True

>>> tree = AST(tree)
>>> tree
(['='], [([':'], [([','], [([','], ['x', 'y']), 'z']), 'a']), 'b'])
TODO Op('==') == ['==']

'''
from operator import itemgetter
import itertools
import re
from multimethod import multimethod
from collections import OrderedDict

from util import *
import grammar
from grammar import Op, Nulop, Binop, Ternop
import config
import make
from tree import Tree
import chain


def get_max_spaces(line: str):
    '''returns the maximum number of spaces in the line.

    >>> assert get_max_spaces('  ') == 2
    '''
    if ' ' in line:
        return max(len(list(xs))
                   for x,xs
                   in itertools.groupby(line)
                   if x==' ')
    else:
        return 0

def get_spacing(line, min_spaces=0):
    '''returns a generator counting down from `max_spaces` to `min_spaces`'''
    max_spaces = max(get_max_spaces(line), min_spaces)
    spacing = reversed(range(min_spaces, 1+max_spaces))
    return spacing

@strict
def get_operators(operators, line):
    '''returns an operator of each precedence given the line to parse. 'precedence' means 'number of spaces', bounded below by the operator definition and bounded above by the number of spaces in the line.

    TODO test
    '''
    for n_spaces in get_spacing(line):
        for operator in operators:
            if operator.min_spaces <= n_spaces:
                yield operator.whiten(n_spaces)

def get_regex_from_binop(op):
    '''binary operators (unlike multinary operators):
    are chainable (e.g. 'x -> y -> z')
    can be on same line even if different (e.g. 'x => y ==> z')

    >>> assert get_regex_from_binop(Binop(' => ')) == r'(\ \=\>\ )'
    >>> assert get_regex_from_binop(Binop(['==>', '=>'])) == r'(\=\=\>|\=\>)'

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

#    @multimethod(list)
    def __init__(self, op, tree):
        super().__init__(tree)
        self.op = op

    # @multimethod(str)
    # def __init__(self, line):
    #     '''parse via recursive regex, into a concrete syntax tree.

    #     `v` = verbose option to print each step

    #     >>> line = 'a -> b , c , d -> e'
    #     >>> cst = _CST(line)
    #     >>> cst
    #     ['a', ' -> ', ['b', ' , ', 'c', ' , ', 'd'], ' -> ', 'e']
    #     '''

    #     # e.g. = [Binop(['<', '>']), Ternop('<', 'where')]
    #     operators = get_operators(grammar.OPERATORS, line)

    #     tree = line
    #     for operator in operators:
    #         if v: print('', tree, operator, sep='\n')
    #         # each pass may or may not 'deepen' the tree
    #         if isinstance(tree, str):
    #             tree = parse_op(operator, tree)
    #         elif isinstance(tree, CST):
    #             tree = tree.map(lambda line: parse_op(operator, line))
    #         else:
    #             assert False

    #     # nothing parsed
    #     if isinstance(tree, str): tree = CST(Nulop(), [tree])

    #     return tree

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

    def unparse(self):
        '''
        >>> line = '3   =   1+2 * 3+4   /   7'
        >>> assert _CST(line).unparse() == line
        '''
        return ''.join(flatten(self))

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

    if len(tree)>1:
        # declare already parsed
        tree = [Sym(word) if word in op else word
                for word in tree]
        # e.g. ['', '+', 'ACh'] => ['+', 'ACh']
        tree = [word for word in tree if word.strip()]

        return CST(op, tree)
    else:
        return line

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

    tries to match a list of ops to a line,
    returning a Tree if it can match and
    the line itself if it can't match.

    one step of a top-down operator-precedence parse.

    >>> assert parse_op(Binop(['-']), '1+2') == '1+2'
    >>> assert parse_op(Binop([' + ']), '1+2') == '1+2'
    >>> assert parse_op(Binop(['+']), '1+2') == ['1','+','2']
    >>> assert parse_op(Binop(['+', '-']), '1+2-3') == ['1','+','2','-','3']
    >>> assert parse_op(Ternop(' ? ', ' : '), 'cond ? then : else') == ['cond', ' ? ', 'then', ' : ', 'else']

    '''

    if isinstance(line, Sym):
        # already parsed
        return line

    if isinstance(op, Binop):
        return parse_binop(op, line)

    if isinstance(op, Ternop):
        return parse_ternop(op, line)

    return line

def _CST(line: str, v=False) -> CST:
    '''parse via recursive regex, into a concrete syntax tree.

    `v` = verbose option to print each step

    >>> line = 'a -> b , c , d -> e'
    >>> _CST(line)
    ['a', ' -> ', ['b', ' , ', 'c', ' , ', 'd'], ' -> ', 'e']
    '''

    # e.g. = [Binop(['<', '>']), Ternop('<', 'where')]
    operators = get_operators(grammar.OPERATORS, line)

    tree = line
    for operator in operators:
        if v: print('', tree, operator, sep='\n')
        # each pass may or may not 'deepen' the tree
        if isinstance(tree, str):
            tree = parse_op(operator, tree)
        elif isinstance(tree, CST):
            tree = tree.map(lambda line: parse_op(operator, line))
        else:
            assert False

    # nothing parsed
    if isinstance(tree, str): tree = CST(Nulop(), [tree])

    return tree

@multimethod(str)
def _AST(s): return s

@multimethod(CST)
def _AST(cst):
    value = cst.op
    trees = [_AST(tree) for tree in cst]
    return Tree((value, trees))

def AST(tree):
    '''

    >>> tree = ['a', ' -> ', ['b', ' , ', 'c', ' , ', 'd'], ' -> ', 'e']
    >>> AST(tree)
    (Op('->'), ['a', (Op(','), ['b', 'c', 'd']), 'e'])
    '''
    @multimethod(str)
    def strip(s): return s.strip()
    @multimethod(object)
    def strip(o): return o

    @multimethod(Sym)
    def is_noun(_): return False
    @multimethod(object)
    def is_noun(_): return True

    tree = _AST(tree)
    tree = tree.map(strip)
    tree = tree.filter(is_noun)
    return tree

def Graph(tree):
    f = memoize(chain.reduce, cache=OrderedDict())
    tree.fold(f)

    graph = [(verb,) + (nouns) for ((verb, nouns), _) in f.__cache__.items()]
    edges = [edge for edge in graph if len(edge)>1]
    nodes = [node for (node, *_) in graph if not _]
    return nodes, edges

def _head(line):
    cst = _CST(line)
    ast = AST(cst)
    nodes, edges = Graph(ast)
    return line, cst, ast, nodes, edges

@typecheck
def head(line: str) -> list:
    line, cst, ast, nodes, edges = _head(line)
    return edges

def body(line, head=''):
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
