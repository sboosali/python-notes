from collections import defaultdict
import functools
import inspect
from multimethod import multimethod
import builtins
import pprint
import itertools
from itertools import filterfalse
from itertools import tee

from recipes import OrderedSet


def decorator(old_decorator):
    '''

    >>> @decorator
    ... def twice(f):
    ...     def twiced(*args, **kwargs):
    ...         x = f(*args, **kwargs)
    ...         return x,x
    ...     return twiced

    >>> @twice
    ... def double(x):
    ...     """docstring"""
    ...     return x+x

    >>> double.__name__
    'double'
    >>> double.__doc__
    'docstring'
    >>> double(2)
    (4, 4)
    '''
    def new_decorator(f, **kwargs):
        g = old_decorator(f, **kwargs)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__module__ = f.__module__
        g.__annotations__ = f.__annotations__
        return g
    return new_decorator

def h1(text):
    print()
    print('----- %s ------' % text)
    print()

def odd(x): return (x%2)==1

def remove_duplicates(xs):
    return list(OrderedSet(xs))

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

def dict_merge(x:dict, y:dict):
    '''
    >>> sorted(dict_merge({'a': 1, 'b': 2}, {'a': 11, 'c': 3}).items())
    [('a', 11), ('b', 2), ('c', 3)]
    '''
    return dict(list(x.items()) + list(y.items()))

@decorator
def typecheck(f):

    def typechecked(*args, **kwargs):
        types = f.__annotations__
        types = {var: typ for var, typ in types.items() if not isinstance(typ, str)}
        positionals = inspect.getfullargspec(f).args
        values = dict_merge(kwargs, dict(zip(positionals, args)))
        vars = set(types) & set(values)
        for var, val, typ in [(x, values[x], types[x]) for x in vars]:
            if not isinstance(val, typ):
                msg = 'in "{f}(... {var}:{typ} ...)", {var} was {val}'
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

@decorator
def strict(f):
    '''turns an iterator into a function that returns a list.

    >>> @strict
    ... def f():
    ...    """docstring"""
    ...    yield 1
    ...    yield 2
    >>> assert f() == [1,2]

    '''
    def strict_f(*args, **kwargs):
        return list(f(*args, **kwargs))
    return strict_f

@decorator
def memoize(f, cache=None):
    if cache is None: cache = {}

    def memoized(*args, **kwargs):
        if args not in cache:
            cache[args] = f(*args, **kwargs)
        return cache[args]

    memoized.__cache__ = cache
    return memoized

class PatternExhausted(Exception): pass

def min(xs, x=0):
    xs = list(xs)
    if xs:
        return builtins.min(xs)
    else:
        return x

_ = None

isa = isinstance

def escape(line):
    '''escapes "%" (good for one format application)
    the code needs them for formatting.
    the text needs it for (e.g.) notes about python code.

    identity
    ∀ line . escape(line) % () == line

    >>> line = '50%'
    >>> escape(line) % () == line
    True
    '''
    return line.replace('%', '%%')

def pp(o: object):
    return pprint.PrettyPrinter(indent=4).pprint(o)

class Range:
    def __init__(self, min=float('-inf'), max=float('+inf')):
        self.min = min
        self.max = max
    def __contains__(self, x):
        '''
        >>> assert 0 not in Range(1,2)
        >>> assert 1 in Range(1,2)
        >>> assert 2 in Range(1,2)
        >>> assert 3 not in Range(1,2)

        >>> assert float('-inf') in Range()
        >>> assert float('+inf') in Range()
        '''
        return self.min <= x <= self.max
    def __repr__(self):
        '''
        >>> Range(1,2)
        Range(1, 2)
        '''
        return 'Range(%r, %r)' % (self.min, self.max)

def dict_diff(a: dict, b: dict):
    '''relative complement between dicts `a \ b`
    returns dict with all keyvals in `b` but not `a`

    >>> dict_diff({'a': 1, 'b': 2}, {})
    {}
    >>> difference = dict_diff({'a': 1, 'b': 2, 'c': 3}, {'a': 1, 'b': 22, 'd': 4})
    >>> sorted(difference.items())
    [('b', 22), ('d', 4)]

    '''
    c = {}
    for k,v in b.items():
        if k not in a or a[k]!=v:
            c[k] = v
    return c

@strict
def complement(xs: iter, ys: iter):
    '''
    >>> complement(['a', 'b'], ['b', 'c'])
    ['a']
    '''
    ys = set(ys)
    for x in xs:
        if x not in ys:
            yield x

def replace(this, that, xs):
    '''replace `this` with `that` in the stream `xs`

    >>> list(replace(1, 'x', [1,2,1]))
    ['x', 2, 'x']

    '''
    for x in xs:
        yield that if x==this else x

def partition(predicate, iterable):
    '''

    >>> ts, fs = partition(lambda _: _%2==0, range(5))
    >>> list(ts)
    [0, 2, 4]
    >>> list(fs)
    [1, 3]

    '''
    i1, i2 = tee(iterable)
    return filter(predicate, i1), filterfalse(predicate, i2)

def is_node(arc):
    label, *vertices = arc
    return not label or len(vertices)==1

def print_list(xs, **kwargs):
    for x in xs:
        print(x, **kwargs)

def pairs(xs):
    '''
    >>> list(pairs([1,2,3]))
    [(1, 2), (1, 3), (2, 3)]
    '''
    for ys in itertools.combinations(xs, 2):
        yield ys

def callgraph(f):
    import pycallgraph
    with pycallgraph.PyCallGraph(output=pycallgraph.output.GraphvizOutput()):
        f()

def print_note(note: dict):
    print('[head]', note['head'])
    for line in note['file']:
        print('[file]', line)
    for line in note['body']:
        print('[body]', line)

def print_heads(notes):
    for note in notes:
        print()
        print(note.head)
    print()

def print_parse(parsed):
    width = max(len(key) for key in parsed._fields)
    print()

    for key, val in parsed._asdict().items():
        first = True
        key = str(key).ljust(width)
        print(' '.ljust(width) + ' |')

        if isinstance(val, list):
            for _ in val:
                if first:
                    print('%s |' % key + (' %s' % (_,)))
                    first = False
                else:
                    print(' '.ljust(width) + ' |'  + (' %s' % (_,)))

        else:
            print('%s | %s' % (key, val))

    print()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
