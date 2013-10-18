from collections import defaultdict
import functools
import inspect
from multimethod import multimethod
import builtins


def h1(text):
    print()
    print('----- %s ------' % text)
    print()

def odd(x): return (x%2)==1

def has_no_duplicates(l):
    return len(l) == len(set(l))

@multimethod(object)
def flatten(x): return [x]
@multimethod(list)
def flatten(l):
    '''
    >>> flatten([[1],[[2,[3]],[4]],5])
    [1,2,3,4,5]
    '''
    if not l: return []
    return functools.reduce(lambda xs,ys: xs+ys, map(flatten, l))

def stagger(xs, ys):
    """
    stagger(['a','b','c'], [1,2]) == ['a', 1, 'b', 2, 'c']
    """
    xs = iter(xs)
    ys = iter(ys)
    zs = [next(xs)]
    for (y,x) in zip(ys,xs):
        zs.append(y)
        zs.append(x)
    return zs

def print_first_token_frequencies(notes):
	counts = defaultdict(int)
	for note in notes:
		for line in note.body:
			line = line.strip()
			if line:
				token = line.split()[0]
				counts[token] += 1
	counts = sorted(counts.items(),
	                key=(lambda fuckguido: fuckguido[1]))
	for token,count in counts:
		print(token, count, sep='\t')

def merge(xs,ys):
    """merge two iterables, that may have duplicates,
    TODO while preserving order.
    """
    xs = list(set(xs + ys))
    return xs

def merge_dicts(x:dict, y:dict):
    return dict(list(x.items()) + list(y.items()))

def typecheck(f):

    def typechecked(*args, **kwargs):
        types = f.__annotations__
        positionals = inspect.getfullargspec(f).args
        values = merge_dicts(kwargs, dict(zip(positionals, args)))
        vars = set(types) & set(values)
        for var, val, typ in [(x, values[x], types[x]) for x in vars]:
            if not isinstance(val, typ):
                msg = 'in "{f}(... {var}:{typ} ...)", "{var}" was "{val}"'
                msg = msg.format(**{'f': f.__name__, 'var':var, 'val':val, 'typ':typ})
                raise TypeError(msg)

        return_val = f(*args, **kwargs)

        if 'return' in types:
            return_type = types['return']
            if not isinstance(return_val, return_type):
                msg = 'in "{f}(...) -> {typ}", return value was "{val}"'
                msg = msg.format(**{'f': f.__name__, 'val':return_val, 'typ':return_type})
                raise TypeError(msg)

        return return_val

    return typechecked

def strict(f):
    '''turns an iterator into a function that returns a list.

    >>> @strict
    ... def f():
    ...    """docstring"""
    ...    yield 1
    ...    yield 2
    >>> assert f.__doc__ == 'docstring'
    >>> assert f() == [1,2]

    '''
    def strict_f(*args, **kwargs):
        return list(f(*args, **kwargs))
    strict_f.__name__ = f.__name__
    strict_f.__doc__ = f.__doc__
    return strict_f

def memoize(f, cache=None):
    if cache is None: cache = {}

    def memoized(*args, **kwargs):
        if args not in cache:
            cache[args] = f(*args, **kwargs)
        return cache[args]

    memoized.__name__ = f.__name__
    memoized.__doc__ = f.__doc__
    memoized.__cache__ = cache
    return memoized

class PatternExhausted(Exception): pass

def min(xs, x=0):
    xs = list(xs)
    if xs:
        return builtins.min(xs)
    else:
        return x


if __name__ == "__main__":
    import doctest
    doctest.testmod()
