""" spec
operators
eg "x -> y"

whitespace grouping
eg   5  /  1*2 + 3*4   ==   5/((1*2)+(3*4))
implement. "." " . " "  .  " ... (works if operators aren't adjacent)
implement. preprocess, find max num spaces, put parens on either side of the most-spaced operator, recur

chaining operators
eg "_ -> _ -> ..."
~ ∞-ary operator with same operator

TODO n-ary operators
eg "_ < _ where _"
eg "_ ~ _ as _ ~ _"

TODO head prefixing
eg
x
-> y

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

def parse(is_op, ops, line):
    """

    assert parse(['-'], '1+2') == '1+2'
    assert parse(['+'], '1+2') == ['1','+','2']
    assert parse(['+', '-'], '1+2-3') == ['1','+','2','-','3']
    assert parse(['+'], ['1+2', '*', '3+4']) == [['1','+','2'], '*', ['3','+','4']]

    """
    # ~ functor
    if isinstance(line, list):
        return list(map(lambda subtree: parse(is_op, ops, subtree), line))

    # already parsed
    if is_op(line): return line

    regex = get_regex(ops)
    tree = re.split(regex, line)
    return tree if len(tree)>1 else line

def parse_head(line: str, v=False) -> list:
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
        tree = parse(is_op, prec, tree)

    return tree

def unparse(tree: list) -> str:
    line = ''.join(flatten(tree))
    return line
