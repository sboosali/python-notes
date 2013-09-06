"""
use "import parse" to document the parsing functions like so: "parse.head()"
"""
import itertools
import re
from util import *
from grammar import PRECS


def whiten(s, n):
    if isinstance(s, str):
        return ' '*n + s + ' '*n
    if isinstance(s, tuple):
        return tuple(whiten(r,n) for r in s)

def get_spacing(line):
    if ' ' in line:
        max_spaces = max(len(list(xs))
                         for x,xs
                         in itertools.groupby(line)
                         if x==' ')
    else:
        max_spaces = 1
    spacing = reversed(range(1, 1+max_spaces))
    return spacing

def get_precedences(precses, line):
    for n_spaces in get_spacing(line):
        for precs in precses:
             yield [whiten(prec, n_spaces) for prec in precs]

def get_regex(ops):
    """

    assert get_regex(' => ') == r'\ \=\>\ '
    assert get_regex(['==>', '=>']) == r'(\=\>|\=\=\>)'
    assert get_regex(('<', 'where')) == r'(\<.*where)'

    """
    if isinstance(ops, str):
        return re.escape(ops)
    if isinstance(ops, list):
        return '(%s)' % '|'.join(map(get_regex, ops))
    if isinstance(ops, tuple):
        return '(%s)' % '.*'.join(map(get_regex, ops))

def _head(is_op, ops, line):
    """

    assert _head(['-'], '1+2') == '1+2'
    assert _head(['+'], '1+2') == ['1','+','2']
    assert _head(['+', '-'], '1+2-3') == ['1','+','2','-','3']
    assert _head(['+'], ['1+2', '*', '3+4']) == [['1','+','2'], '*', ['3','+','4']]

    """
    # ~ functor
    if isinstance(line, list):
        return list(map(lambda subtree: _head(is_op, ops, subtree), line))

    # already parsed
    if is_op(line): return line

    regex = get_regex(ops)
    tree = re.split(regex, line)
    return tree if len(tree)>1 else line

def head(line: str, v=False) -> list:
    """
    `v` = verbose option to print each step

    : :infix => :prefix

    x        => (node x y)
    x , y    => (aliases x y ...)
    x . y    => (conjunction x y ...)
    x ~ y    => (like x y ...)
    x = y    => (equals x y ...)
    x := y   => (defined x y)
    x < y    => (subset x y ...)
    x : y    => (is-a x y)

    x ... y  => (ellipses x y)
    [x]      => (context x)
    word. x  => (parser "word" x)
    . x      => (comment x)
    x -> y   => (edge "->" x y ...)

    """

    tree = line
    precs = list(get_precedences(PRECS, line))
    ops = set(flatten(precs))
    def is_op(line): return line in ops

    for prec in precs:
        if v: print('', tree, prec, sep='\n')
        tree = _head(is_op, prec, tree)

    return tree

def body(tree: list, line: str) -> list:
    """TODO"""
    return _head([unparse(tree), line])

def unparse(tree: list) -> str:
    line = ''.join(flatten(tree))
    return line

def aliases(line):
    tree = line.split(' , ')
    return tree if len(tree)>1 else None

def conjunction(line):
    tree = line.split(' . ')
    return tree if len(tree)>1 else None
