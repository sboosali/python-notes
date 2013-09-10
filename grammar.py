""" spec
a `prec` is a list of `op` that share the same precedence
an 'op' is an operator

"""
import yaml
from util import *


class Op: pass

class Binop(list, Op):
    """

    assert isinstance(Binop(':='), Binop)
    assert isinstance(Binop(['->','<-']), Binop)
    assert Binop('==') == ['==']

    """
    def __init__(self, ops, min_spaces):
        if isinstance(ops, str): ops = [ops]
        super().__init__(ops)
        self.min_spaces = min_spaces
    def __hash__(self):
        return hash(' '.join(self))

class Ternop(tuple, Op):
    """

    assert isinstance(Ternop('<', 'where'), Ternop)
    assert Ternop('~', 'but') == ('~', 'but')

    """
    def __new__(cls, l, r, **kwargs):
        assert is_ternop(l + ' ' + r)
        return super().__new__(cls, (l, r))
    def __init__(self, *args, min_spaces=1):
        self.min_spaces = min_spaces

class Quatrop(tuple, Op):
    """

    assert isinstance(Quatrop('~', 'as, '~'), Quatrop)
    assert Quatrop('~', 'as, '~') == ('~', 'as, '~')

    """
    def __new__(cls, l, m, r, **kwargs):
        assert is_quatrop(' '.join([l,m,r]))
        return super().__new__(cls, (l, m, r))
    def __init__(self, *args, min_spaces=1):
        self.min_spaces = min_spaces

def is_binop(op):
    return len(op.split())==1

def are_binops(ops):
    return all(is_binop(op) for op in ops)

def is_ternop(op):
    return len(op.split())==2

def is_quatrop(op):
    return len(op.split())==3

def munge_syntax(syntax):
    """groups operators by precedence.
    the longer operators must come before the shorter ones,
    for regexes like "( ==> | => )" to work right.
    """
    operators = syntax['operators']
    min_spaces = defaultdict(lambda: syntax['default_min_spaces'],
                             syntax['min_spaces'])

    for op in operators:
        if isinstance(op, list):
            ops = op
            if are_binops(ops):
                yield Binop(sorted(ops, key=len, reverse=True),
                            min(min_spaces[op] for op in ops))

        if isinstance(op, str):
            if is_binop(op):
                yield Binop(op, min_spaces[op])
            if is_ternop(op):
                yield Ternop(*op.split(), min_spaces=min_spaces[op])
            if is_quatrop(op):
                yield Quatrop(*op.split(), min_spaces=min_spaces[op])

CHARS = '123456789' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 'abcdefghijklmnopqrstuvwxyz' + '-/._' + '#$%^'

PREPOSITIONS = 'of in to with as at for on by from'.split()
VERBS = 'is was has had want should can could will would do'.split()
CONNECTIVES = 'and or not but while'.split()
INTERROGATIVES = 'who what where when why how'.split()

#: [Op]
SYNTAX = yaml.load(open('syntax.yaml'))
OPERATORS = list(munge_syntax(SYNTAX))
assert has_no_duplicates(OPERATORS)

if __name__=='__main__':
    for operator in OPERATORS: print(operator)
