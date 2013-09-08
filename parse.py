"""
use "import parse" to document the parsing functions like so: "parse.head()"
"""
import itertools
import re
from util import *
from grammar import Binop, Ternop
from grammar import OPERATORS


def whiten(op, n):
    """

    assert whiten(Binop('->'), 1) == [' -> ']
    assert whiten(Binop(['->', '<-']), 1) == [' -> ', ' <- ']

    """
    if isinstance(op, Binop):
        return Binop([' '*n + sym + ' '*n for sym in op])
    if isinstance(op, Ternop):
        l, r = op
        l = ' '*n + l + ' '*n
        r = ' '*n + r + ' '*n
        return Ternop(l, r)

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

def get_operators(operators, line):
    for n_spaces in get_spacing(line):
        for operator in operators:
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

def parse_binop(op, line):
    regex = get_regex_from_binop(op)
    tree = re.split(regex, line)
    return tree if len(tree)>1 else line

def parse_ternop(op, line):
    """
    filter away empty matches
    e.g. '[head]' =match=> ['', '[', 'head', ']', ''] =filter=> ['[', 'head', ']']
    """
    regex = get_regex_from_ternop(op)
    match = re.search(regex, line)
    if match:
        match = match.groupdict()
        operators = op
        operands = [match['A'], match['B'], match['C']]
        tree = stagger(operands, operators)
        tree = list(filter(bool, tree))
        return tree
    else:
        return line

def aliases(line):
    tree = line.split(' , ')
    return tree if len(tree)>1 else None

def conjunction(line):
    tree = line.split(' . ')
    return tree if len(tree)>1 else None

def unparse(tree: list) -> str:
    line = ''.join(flatten(tree))
    return line

def _head(is_op, op, line):
    """tries to match a list of ops to a line,
    returning a Tree if it can match and
    the line itself if it can't match.

    one step of a top-down operator-precedence parse.

    >>> def is_op(line): return line in ['-', '+']
    >>> assert _head(is_op, ['-'], '1+2') == '1+2'
    >>> assert _head(is_op, ['+'], '1+2') == ['1','+','2']
    >>> assert _head(is_op, ['+', '-'], '1+2-3') == ['1','+','2','-','3']
    >>> assert _head(is_op, ['+'], ['1+2', '*', '3+4']) == [['1','+','2'], '*', ['3','+','4']]

    """
    # ~ functor
    if isinstance(line, list):
        return list(map(lambda subtree: _head(is_op, op, subtree), line))

    # if the line itself is an op, it was already parsed
    if is_op(line):
        return line

    if isinstance(op, Binop):
        return parse_binop(op, line)

    if isinstance(op, Ternop):
        return parse_ternop(op, line)

    return line

def head(line: str, v=False) -> list:
    """
    parses a head step-by-step.

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

    operators = list(get_operators(OPERATORS, line))
    all_operators = {symbol for operator in operators for symbol in operator}
    def is_op(line): return line in all_operators

    tree = line
    for operator in operators:
        if v: print('', tree, operator, sep='\n')
        tree = _head(is_op, operator, tree)
    return tree

def body(tree: list, line: str) -> list:
    """TODO"""
    return _head([unparse(tree), line])
