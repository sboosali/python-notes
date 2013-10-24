from operator import itemgetter

from util import *
import config


_reducers = {}
@decorator
def reducer(f):
    '''decorated by `reducer` means:

    * it takes a flat tree to a value
      (flat tree = value + list of values)
      (e.g. flat tree: operator + list of operands)

    '''
    _reducers[f.__name__] = f
    f.__annotations__.update({'x': object, 'ys': list})
    f = typecheck(f)
    return f

def reduce_noun(noun, _):
    return noun

def reduce_verb(verb, nouns):
    operator = verb.symbol
    reducer = config.reduce[operator]
    reducer = _reducers[reducer]
    return reducer(verb, nouns)

def reduce(verb, nouns):
    '''
    TODO verb : ?
    '''
    return reduce_verb(verb, nouns) if nouns else reduce_noun(verb, nouns)

@reducer
def left(x, ys): return ys[0]
@reducer
def right(x, ys): return ys[-1]
@reducer
def join(x, ys): return (' %s ' % x).join(y for y in ys if y)
