from util import *
import config
import op


def is_binop(op):
    '''
    >>> assert is_binop('->')
    >>> assert is_binop(['=>', '==>'])
    '''
    if isinstance(op, str):
        return len(op.split())==1
    if isinstance(op, list):
        return True

def is_narop(op):
    '''
    >>> assert is_narop(['.', '.'])
    '''
    if isinstance(op, list):
        return len(op)==2 and op[0]==op[1]

def is_ternop(op):
    '''
    >>> assert is_ternop('< where')
    '''
    if isinstance(op, str):
        return len(op.split())==2

def munge_operator(operator: 'str|list') -> op.Op:
    '''
    groups operators by precedence:
    the longer operators must come before the shorter ones,
    for regexes like "( ==> | => )" to work right.
    '''

    if is_narop(operator):
        operator, _ = operator
        return op.Narop(operator)

    elif is_binop(operator):
        if isinstance(operator, str):
            return op.Binop(operator)
        if isinstance(operator, list):
            return op.Binop(*operator)

    elif is_ternop(operator):
        l, r = operator.split()
        return op.Ternop(l,r)

    else:
        raise PatternExhausted

CHARS = '123456789' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 'abcdefghijklmnopqrstuvwxyz' + '-/._' + '#$%^'

PREPOSITIONS = 'of in to with as at for on by from'.split()
VERBS = 'is was has had want should can could will would do'.split()
CONNECTIVES = 'and or not but while'.split()
INTERROGATIVES = 'who what where when why how'.split()

#: [Op]
OPERATORS = [munge_operator(op) for op in config.operators]
assert has_no_duplicates(OPERATORS)
#: [str]
SYMBOLS = flatten(config.operators)

if __name__=='__main__':
    import doctest
    doctest.testmod()

    for operator in OPERATORS:
        print(operator)
    print(SYMBOLS)
