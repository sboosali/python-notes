import re
from copy import copy

from util import *
from op import Op, Nulop, Unop, Narop, Binop, Ternop
from tree import Tree
import syntax
import tokens


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
            if num_spaces in operator.spacing:
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

    >>> parse_binop(Unop('+ '), '+ x')
    Tree((Unop('+ '), ['+ ', 'x']))

    >>> parse_binop(Narop(' . '), 'x . y . z')
    Tree((Narop(' . '), ['x', ' . ', 'y', ' . ', 'z']))

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

    if len(trees)==2 and isa(op, Unop):
        # unary operator
        return Tree((op, trees))

    elif len(trees)>=3 and (isa(op, Binop) or isa(op, Narop)):
        # binary operator
        return Tree((op, trees))

    else:
        # nothing parsed
        return Tree(line)

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

    if isa(op, Unop) or isa(op, Binop) or isa(op, Narop):
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
    operators = get_operators(syntax.precedence, line)
    tree = Tree(line)

    for operator in operators:
        # parse top-down: grow tree on each regex match
        tree = tree.tmap(lambda leaf: parse_op(operator, leaf))

    if tree.is_leaf():
        # nothing parsed
        tree = Tree((syntax.nulop, [tree]))

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
        operator = copy(value)
        operator = syntax.operators[op.strip()][0]
        operands = [x, Tree(op), y]
        left = Tree((operator, operands))

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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
