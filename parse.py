"""
use "import parse" to document the parsing functions like so: "parse.head()"
"""
import itertools
import re
from util import *
from grammar import Op, Nulop, Binop, Ternop, Quatrop
from grammar import OPERATORS
import config


def whiten(op, n):
    """

    assert whiten(Binop('->'), 1) == [' -> ']
    assert whiten(Binop(['->', '<-']), 1) == [' -> ', ' <- ']

    """
    if isinstance(op, Binop):
        return Binop([' '*n + sym + ' '*n for sym in op],
                     min_spaces=op.min_spaces)
    if isinstance(op, Ternop):
        l, r = op
        l = ' '*n + l + ' '*n
        r = ' '*n + r + ' '*n
        return Ternop(l, r,
                     min_spaces=op.min_spaces)
    if isinstance(op, Quatrop):
        l, m, r = op
        l = ' '*n + l + ' '*n
        m = ' '*n + m + ' '*n
        r = ' '*n + r + ' '*n
        return Quatrop(l, m, r,
                     min_spaces=op.min_spaces)

def get_spacing(line, min_spaces=0):
    """
    TODO tradeoffs between spaced versus flush operators

    [min_spaces = 0]
    (good) -> '1+2' => ['1', '+', '2']
    (bad) -> '5-HT' => ['5', '-', 'HT']
    (good) -> '[head]' => ['[', 'head', ']']
    (bad) -> 'Na+' => WRONG (tries to match binary operator)

    [min_spaces = 1]
    (bad) -> '1+2' => '1+2'
    (good) -> '5-HT' => '5-HT'
    (bad) -> '[head]' => '[head]'
    (good) -> 'Na+' => 'Na+'
    """
    if ' ' in line:
        max_spaces = max(len(list(xs))
                         for x,xs
                         in itertools.groupby(line)
                         if x==' ')
    else:
        max_spaces = min_spaces
    spacing = reversed(range(min_spaces, 1+max_spaces))
    return spacing

@as_list
def get_operators(operators, line):
    """returns an operator of each precedence given the line to parse. 'precedence' means 'number of spaces', bounded below by the operator definition and bounded above by the number of spaces in the line.
    """
    for n_spaces in get_spacing(line):
        for operator in operators:
            if operator.min_spaces <= n_spaces:
                yield whiten(operator, n_spaces)

def get_regex_from_binop(op):
    """binary operators (unlike multinary operators):
    are chainable (e.g. 'x -> y -> z')
    can be on same line even if different (e.g. 'x => y ==> z')

    >>> assert get_regex_from_binop(Binop(' => ')) == r'\ \=\>\ '
    >>> assert get_regex_from_binop(Binop(['==>', '=>'])) == r'(\=\>|\=\=\>)'

    """
    return '(%s)' % '|'.join(map(re.escape, op))

def get_regex_from_ternop(op):
    """

    >>> assert get_regex_from_ternop(Ternop(' < ', ' where ')) == r'((?P<A>.*)\ \<\ (?P<B>.*)\ where\ (?P<C>.*))'

    """
    operators = map(re.escape, op)
    operands = {'A': r'(?P<A>.*)',
                'B': r'(?P<B>.*)',
                'C': r'(?P<C>.*)'}
    regex = r'({A}{0}{B}{1}{C})'
    regex = regex.format(*operators, **operands)
    return regex


def get_regex_from_quatrop(op):
    """

    >>> assert get_regex_from_quatrop(Quatrop(' ~ ', ' as ', ' ~ ')) == r'((?P<A>.*)\ \~\ (?P<B>.*)\ as\ (?P<C>.*)\ \~\ (?P<D>.*))'

    """
    operators = map(re.escape, op)
    operands = {'A': r'(?P<A>.*)',
                'B': r'(?P<B>.*)',
                'C': r'(?P<C>.*)',
                'D': r'(?P<D>.*)'}
    regex = r'({A}{0}{B}{1}{C}{2}{D})'
    regex = regex.format(*operators, **operands)
    return regex

class CST(list):
    """concrete syntax tree"""
    @typecheck
    def __init__(self, op: Op, tree: list):
        super().__init__(tree)
        self.op = op

    def map(self, f):
        """maps a function onto each leaf (i.e. token or unparsed line) of the CST.
        `t` is either a leaf or a subtree
        CST : functor

        >>> assert Tree([Tree([1]), Tree([2,3,Tree([4])]), 5]).map(lambda x: x+1) == [[2], [3,4,[5]], 6]

        """
        op = self.op
        tree = [f(t)
                if not isinstance(t, CST)
                else t.map(f)
                for t in self]
        return CST(op, tree)

class Sym(str):
    def __getattribute__(self, attr):
        """transparently return a Sym for any str method call that returns a str.

        the line (regex) parsers wrap operators in Sym's, and the tree (recursive) parsers skip Sym's (meaning, "already parsed").

        >>> assert isinstance(Sym('Sym').strip(), Sym)
        >>> assert isinstance(Sym('Sym').split(), list)

        """
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
    """
    wraps the operator(s) in Sym to say "this token has been parsed as a symbol of some operator, don't reparse it".

    cleans the output
    e.g. ['1 ', ' + ', ' 2'] => ['1',Sym('+'),'2']

    >>> assert parse_binop(Binop('->'), 'x -> y -> z') == CST(['->'], ['x ', '->', ' y ', '->', ' z'])

    """
    regex = get_regex_from_binop(op)
    tree = re.split(regex, line)

    if len(tree)>1:
        tree = [Sym(word) if word in op else word
                for word in tree]
        tree = [word.strip() for word in tree if word.strip()]
        return CST(op, tree)
    else:
        return line

def parse_ternop(op, line) -> 'str | CST str':
    """
    filter away empty matches
    e.g. '[head]' =match=> ['', '[', 'head', ']', ''] =filter=> ['[', 'head', ']']

    wraps the operator(s) in Sym to say "this token is a symbol of an operator, don't reparse it".

    cleans the output
    e.g. ['', ' [ ', 'head', ' ] ', ''] => ['[', 'head', ']']

    >>> assert parse_ternop(Ternop('~', 'but'), 'x ~ y but z') == CST(('~', 'but'), ['x ', '~', ' y ', 'but', ' z'])

    """
    regex = get_regex_from_ternop(op)
    match = re.search(regex, line)
    if match:
        match = match.groupdict()
        operators = op
        operands = [match['A'], match['B'], match['C']]
        tree = stagger(operands, operators)

        # clean
        tree = [word.strip() for word in tree if word.strip()]
        tree = [Sym(word) if word in op else word
                for word in tree]

        return CST(op, tree)

    else:
        return line

def parse_quatrop(op, line) -> 'str | CST str':
    """

    >>> assert parse_quatrop(Quatrop(' ~ ', ' as ', ' ~ '), 'a ~ b as x ~ y') == CST((' ~ ', ' as ', ' ~ '), ['a', ' ~ ', 'b', ' as ', 'x', ' ~ ', 'y'])

    """

    regex = get_regex_from_quatrop(op)
    match = re.search(regex, line)
    if match:
        match = match.groupdict()
        operators = op
        operands = [match['A'], match['B'], match['C'], match['D']]
        tree = stagger(operands, operators)

        # clean
        tree = [word.strip() for word in tree if word.strip()]
        tree = [Sym(word) if word in op else word
                for word in tree]

        return CST(op, tree)

    else:
        return line

@typecheck
def _head(op: Op, line: str): # -> 'str | CST str':
    """tries to match a list of ops to a line,
    returning a Tree if it can match and
    the line itself if it can't match.

    one step of a top-down operator-precedence parse.

    >>> assert _head(Binop(['-']), '1+2') == '1+2'
    >>> assert _head(Binop([' + ']), '1+2') == '1+2'
    >>> assert _head(Binop(['+']), '1+2') == ['1','+','2']
    >>> assert _head(Binop(['+', '-']), '1+2-3') == ['1','+','2','-','3']
    >>> assert _head(Ternop(' ? ', ' : '), 'cond ? then : else') == ['cond', ' ? ', 'then', ' : ', 'else']

    """

    if isinstance(line, Sym):
        # already parsed
        return line

    if isinstance(op, Binop):
        return parse_binop(op, line)

    if isinstance(op, Ternop):
        return parse_ternop(op, line)

    if isinstance(op, Quatrop):
        return parse_quatrop(op, line)

    return line

@typecheck
def head(line: str, v=False) -> CST:
    """
    parses a head step-by-step.
    returns the parse tree.

    `v` = verbose option to print each step

    : :infix => :prefix

    x        => (node x)
    x , y    => (aliases x y ...)
    x . y    => (conjunction x y ...)
    x ~ y    => (like x y ...)
    x = y    => (equals x y ...)
    x := y   => (define x y)
    x < y    => (subset x y ...)
    x : y    => (is_a x y)

    x ... y  => (ellipses x y)
    [x]      => (context x)
    word. x  => (parser "word" x)
    . x      => (comment x)
    x -> y   => (edge "->" x y ...)

    """

    # e.g. = [Binop(['<', '>']), Ternop('<', 'where')]
    operators = get_operators(OPERATORS, line)

    # nothing parsed
    _tree = CST(Nulop(), [line])

    # try to parse every subtree with each operator at each precedence
    tree = _tree
    for operator in operators:
        if v: print('', tree, operator, sep='\n')
        # each pass may or may not 'deepen' the tree
        tree = tree.map(lambda line: _head(operator, line))

    # something parsed
    if tree != _tree: tree = tree[0]

    return tree

def body(tree: list, line: str) -> list:
    """TODO"""

def unparse(tree: list) -> str:
    line = ''.join(flatten(tree))
    return line

def is_alias(tree):
    """a parse tree is an alias if the top-level operator is the alias operator.
    """
    alias_op = config.concrete['alias']
    return tree.op.eqv(alias_op)
