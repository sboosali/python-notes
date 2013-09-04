""" spec
a `prec` is a list of `op` that share the same precedence
an 'op' is an operator

"""
from util import *


def op(symbols):
    return tuple(symbols.split())

def order_operators(operators):
    """groups operators by precedence.
    the longer operators must come before the shorter ones,
    for regexes like "( ==> | => )" to work right.
    """
    for ops in operators:
        if isinstance(ops, tuple):
            yield [ops]
        if isinstance(ops, list):
            yield ops
        if isinstance(ops, str):
            yield sorted(ops.split(), key=len, reverse=True)

CHARS = '123456789' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 'abcdefghijklmnopqrstuvwxyz' + '-/._' + '#$%^'

PREPOSITIONS = 'of in to with as at for on by from'
VERBS = 'is was has had want should can could will would do'
CONNECTIVES = 'and or not but while'
INTERROGATIVES = 'who what where when why how'

PRECS = list(order_operators([
 ':=',
 ':-',
 '< >',
 ':',
 '=',
 '~',
 'v',

 [op('< where'), op('~ but')],
 op('~ as ~'),

 '<- ->',
 '<-- -->',
 '<= => <== ==>',
 '<~ ~>',

 '+ -',
 '* /',
 '^',

 '.',
 ',',
 '[ ]',
 '( )',
 '{ }',

 VERBS,
 PREPOSITIONS,
 CONNECTIVES,
# INTERROGATIVES,
]))

assert has_no_duplicates(flatten(PRECS))

if __name__=='__main__':
    for prec in PRECS: print(prec)
