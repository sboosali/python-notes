'''
`reduce.reducers['reducer']` gets a reducer by name

e.g. left reduction
x , y , z
(x , y) , z
x , z
x


'''
from operator import itemgetter

from util import *
import config


reducers = {}
@decorator
def reducer(f):
    '''decorated by `reducer` means:

    * it takes a flat tree to a value
      (flat tree = value + list of values)
      (e.g. flat tree: operator + list of operands)

    '''
    reducers[f.__name__] = f
    f.__annotations__.update({'x': object, 'ys': tuple})
    f = typecheck(f)
    return f

def reduce_operand(operand, _):
    return operand

def reduce_operator(operator, operands):
    reducer = operator.reduce
    return reducer(str(operator), operands)

def reduce(operator, operands):
    '''
    '''
    if operands:
        return reduce_operator(operator, operands)
    else:
        return reduce_operand(operator, operands)

@reducer
def left(x, ys): return ys[0]
@reducer
def right(x, ys): return ys[-1]
@reducer
def join(x, ys): return '(%s)' % (' %s ' % x).join(y for y in ys if y)
@reducer
def prefix(x, ys): return '%s %s' % (x, ' '.join(ys))
