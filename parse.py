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

>>> tree.map(f=lambda _: _.default(), g=lambda _: _)
Tree((Binop(' = '), [(Binop(' : '), [(Binop(' , '), ['x', ' , ', 'y', ' , ', 'z']), ' : ', 'a']), ' = ', 'b']))

>>> tree = AST(tree)
>>> tree.map(f=lambda _: _.default(), g=lambda _: _)
Tree((Binop('='), [(Binop(':'), [(Binop(','), [(Binop(','), ['x', 'y']), 'z']), 'a']), 'b']))

'''
import re
from operator import itemgetter
import itertools
from multimethod import multimethod
from collections import OrderedDict
from collections import namedtuple

from util import *
from parsing import CST, AST
import config
import context
import Graph
import Edge
import notes
import Line


Parsed = namedtuple(
    'Parsed',
    'line cst ast nodes edges head parser'
)

parsers = {}
@decorator
def parser(f):
    '''decorated by `parser` means:

    * its name is in the config
    * its type is "str => Parsed"
    * its called by `parse.head`
    '''
    parsers[f.__name__] = f
    assert f.__name__ in config.parsers
    f.__annotations__.update({'return': Parsed, 'line': str})
    f = typecheck(f)
    return f

@parser
def default(line):
    '''the default parser for heads.
    cst ~ associate the line into a tree
    ast ~ clean up and binarize the Binop subtrees
    graph ~ get edges from the parse tree
    '''
    cst = CST(line)
    ast = AST(cst)
    head, (nodes, edges) = Graph.Graph.harvest(ast)
    return Parsed(line, cst, ast, nodes, edges, head, 'default')

@parser
def ellipsis(line):
    '''doesn't parse the head, only changes how the body is parsed.
    '''
    _ = None
    return Parsed(line, (), (), [], [], line, 'ellipsis')

@parser
def comment(line):
    '''don't parse'''
    _ = None
    return Parsed(line, (), (), [], [], line, 'comment')

@typecheck
def head(line: str) -> Parsed:
    '''gets parser by matching regex to line => head

    before the line is really parsed, it is checked against regular expressions (defined in `config.parsers`). whichever first matches (they are ordered), its parser is found (by string) and . it's dynamic in that a function must be found by name, but static in that everything can be checked before much code is run (just imports and `config.py`).
    '''
    for parser in config.parser_precedence:
        definition = config.parsers[parser]
        regex = definition['regex']
        if re.search(regex, line): break

    parse = parsers[parser]
    return parse(line)

@typecheck
def body(parsed: Parsed, body_line: str) -> Parsed:
    '''put body in context wrt head => parse

    create a "context" from the head and the body (given the parser that parsed the head). put the body into that context with formatting and parse it.
    '''
    head_parser = parsed.parser
    definition = config.parsers[head_parser]
    body_parser = definition['body']
    parse = parsers[body_parser]

    #HACK
    if re.search(config.parsers['comment']['regex'], body_line):
        return parsers['comment'](body_line)

    head_line = parsed.head
    holes = context.get(head_parser, head_line, body_line)
    line = holes % escape(body_line)

    return parse(line)

def attach(h, b):
    return [h] + b

@strict
def edges(h: Parsed, b: Parsed) -> [Edge]:
    lines = attach(h, b)
    for line in lines:
        for edge in line.edges:
            yield edge

def note(h: str, b: str = (), as_edges=False) -> (Parsed, Parsed):
    h = head(h)
    b = [body(h, line) for line in b]

    if as_edges: return edges(h, b)

    return h, b

def parse(text: str) -> [Parsed]:
    '''
    '''
    for _ in notes.read(text, as_note=True):
        head, body = note(_.head, _.body)

        yield head
        yield from body


if __name__ == "__main__":
    import doctest
    doctest.testmod()
