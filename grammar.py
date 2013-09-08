""" spec
a `prec` is a list of `op` that share the same precedence
an 'op' is an operator

"""
from util import *


class Binop(list):
    """

    assert isinstance(Binop(':='), Binop)
    assert isinstance(Binop(['->','<-']), Binop)
    assert Binop('==') == ['==']

    """
    def __init__(self, ops):
        if isinstance(ops, str): ops = [ops]
        super().__init__(ops)
    def __hash__(self):
        return hash(' '.join(self))

class Ternop(tuple):
    """

    assert isinstance(Ternop('<', 'where'), Ternop)
    assert Ternop('~', 'but') == ('~', 'but')

    """
    def __new__(cls, l, r):
        assert is_ternop(l + ' ' + r)
        return super().__new__(cls, (l, r))

def is_binop(op):
    return len(op.split())==1

def are_binops(ops):
    return all(is_binop(op) for op in ops)

def is_ternop(op):
    return len(op.split())==2

def order_operators(ops):
    """groups operators by precedence.
    the longer operators must come before the shorter ones,
    for regexes like "( ==> | => )" to work right.
    """
    for op in ops:
        if isinstance(op, list):
            if are_binops(op):
                yield Binop(sorted(op, key=len, reverse=True))
        if isinstance(op, str):
            if is_binop(op):
                yield Binop(op)
            if is_ternop(op):
                yield Ternop(*op.split())

CHARS = '123456789' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 'abcdefghijklmnopqrstuvwxyz' + '-/._' + '#$%^'

PREPOSITIONS = 'of in to with as at for on by from'.split()
VERBS = 'is was has had want should can could will would do'.split()
CONNECTIVES = 'and or not but while'.split()
INTERROGATIVES = 'who what where when why how'.split()

#: list of str|list|tuple
OPERATORS = list(order_operators([
 '< where',
 '~ but',

 ':=',
 ':-',
 ['<', '>'],
 ':',
 '=',
 '~',
 'v',

 ['<-', '->'],
 ['<--', '-->'],
 ['<=', '=>', '<==', '==>'],
 ['<~', '~>'],

 ['+', '-'],
 ['*', '/'],
 '^',

 '.',
 ',',

 '[ ]',
 '( )',
 '{ }',

]))

assert has_no_duplicates(OPERATORS)

if __name__=='__main__':
    for operator in OPERATORS: print(operator)
