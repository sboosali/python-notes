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
from op import Op, Nulop, Unop, Narop, Binop, Ternop
import config
import make
from tree import Tree
import context
import tokens
import graph


Parsed = namedtuple('Parsed',
                    'line cst ast nouns verbs nodes edges head parser')

_parsers = {}
@decorator
def parser(f):
    '''decorated by `parser` means:

    * its name is in the conifg
    * it returns a `Parsed`
    * its called by `parse.head`
    '''
    _parsers[f.__name__] = f
    assert f.__name__ in config.parsers
    f.__annotations__.update({'return': Parsed, 'line': str})
    f = typecheck(f)
    return f

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

class Symbol(str):
    def __getattribute__(self, attr):
        '''transparently return a Symbol for any str method call that returns a str.

        >>> isinstance(Symbol('Symbol').strip(), Symbol)
        True
        >>> isinstance(Symbol('Symbol').split(), list)
        True
        '''

        attr = super().__getattribute__(attr)
        if hasattr(attr, '__call__'):
            def symbolize(*args, **kwargs):
                ret = attr(*args, **kwargs)
                ret = Symbol(ret) if isinstance(ret, str) else ret
                return ret
            return symbolize
        else:
            return attr

class Operator(Symbol):
    '''the line (regex) parsers wrap operators in Operator's, and the tree parsers skips them (meaning, "already parsed").
    '''

class Operand(Symbol):
    '''the tree parsers skips them (meaning, "already parsed").
    '''

def unparse(tree):
    '''
    >>> line = '3   =   1+2 * 3+4   /   7'
    >>> assert unparse(CST(line)) == line
    '''
    return ''.join(flatten(tree.leaves()))

def parse_binop(op, line):
    '''parses a line with a binary operator.

    wraps the operator(s) in Operator to say "this token has been parsed as a symbol of some operator, don't reparse it".

    cleans the output
    e.g. ['1 ', ' + ', ' 2'] => ['1', Operator('+'), '2']

    >>> parse_binop(Binop(' -> '), 'x -> y -> z')
    Tree((Binop(' -> '), ['x', ' -> ', 'y', ' -> ', 'z']))
    '''

    regex = op.regex()
    trees = re.split(regex, line, re.UNICODE)

    # declare already parsed
    trees = [Operator(word) if word in op else word
            for word in trees]
    # e.g. ['', '+', 'ACh'] => ['+', 'ACh']
    trees = [word for word in trees if word.strip()]

    if len(trees)==1:
        # nothing parsed
        return Tree(line)

    elif len(trees)==2:
        # unary operator
        return Tree(line)

    else:
        # binary operator
        return Tree((op, trees))

def parse_ternop(op, line):
    '''parses a line with a ternary operator.

    filter away empty matches
    e.g. '[head]' =match=> ['', '[', 'head', ']', ''] =filter=> ['[', 'head', ']']

    wraps the operator(s) in Operator to say "this token is a symbol of an operator, don't reparse it".

    empty operands are kept for the other operands' positions
    e.g. "(x) y" => ['', '(', 'x', ')', 'y']

    >>> op = Ternop('~', 'but')
    >>> parse_ternop(op, 'x ~ y but z').leaves()
    ['x ', '~', ' y ', 'but', ' z']
    '''
    regex = op.regex()
    match = re.search(regex, line, re.UNICODE)

    if match:
        match = match.groupdict()
        operators = op
        operands = [match['A'], match['B'], match['C']]
        trees = stagger(operands, operators)

        # declare operator symbols have been parsed
        trees = [Operator(word) if word in op else word
                for word in trees]

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

    if not line:
        return Tree(line)

    if isinstance(line, Operand) or isinstance(line, Operator):
        # already parsed
        return Tree(line)

    if not op.spaces:
        # 0-space operators must not parse apart tokens
        if tokens.has_tokens(line):
            return Tree(Operand(line))

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
        # parse top-down: grow tree on each regex match
        tree = tree.tmap(lambda leaf: parse_op(operator, leaf))

    if tree.is_leaf():
        # nothing parsed
        tree = Tree((Nulop(), [tree]))

    return tree

@typecheck
def left_associate(tree: Tree) -> Tree:
    ''': n-ary tree => binary tree
    (only associates Binops, not Narops)
    '''
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
    '''the Abstract Syntax Tree
    '''
    def is_operand(word): return not isinstance(word, Operator)

    tree = left_associate(tree)
    tree = tree.filter(f=is_operand, g=bool) # infix => prefix
    tree = tree.map(f=lambda _: _.strip(), g=bool) # ' , ' => ','
    return tree

@parser
def default(line):
    '''the default parser for heads.
    cst ~ associate the line into a tree
    ast ~ clean up and binarize the Binop subtrees
    graph ~ get edges from the parse tree
    '''
    cst = CST(line)
    ast = AST(cst)
    nouns, verbs, nodes, edges = graph.Graph(ast)
    head = graph.Head(nouns, verbs)
    return Parsed(line, cst, ast, nouns, verbs, nodes, edges, head, 'default')

@parser
def ellipsis(line):
    '''doesn't parse the head, only changes how the body is parsed.
    '''
    _ = None
    return Parsed(line, _, _, _, _, _, _, line, 'ellipsis')

@parser
def comment(line):
    '''don't parse'''
    _ = None
    return Parsed(line, _, _, _, _, _, _, line, 'comment')

@typecheck
def parse_head(line: str) -> Parsed:
    '''gets parser by matching regex to line => head

    before the line is really parsed, it is checked against regular expressions (defined in `config.parsers`). whichever first matches (they are ordered), its parser is found (by string) and . it's dynamic in that a function must be found by name, but static in that everything can be checked before much code is run (just imports and `config.py`).
    '''
    for parser, regex in config.parsers.items():
        if re.search(regex, line): break
    parse = _parsers[parser]

    return parse(line)

@typecheck
def parse_body(parsed: Parsed, line: str) -> Parsed:
    '''put body in context wrt head => parse

    create a "context" from the head and the body (given the parser that parsed the head). put the body into that context with formatting and parse it.
    '''
    holes = context.get(parsed.parser, parsed.head, line)
    line = holes % escape(line)
    return default(line)

def note(head: str, body: str= []) -> (Parsed, Parsed):
    head = parse_head(head)
    body = [parse_body(head, line) for line in body]
    return head, body


if __name__ == "__main__":
    import doctest
    doctest.testmod()
