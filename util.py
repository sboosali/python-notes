from collections import defaultdict
import functools
import inspect


def h1(text):
    print()
    print('----- %s ------' % text)
    print()

def has_no_duplicates(l):
    return len(l) == len(set(l))

def flatten(l):
    """eg [[1],[[2,[3]],[4]],5] => [1,2,3,4,5]

    each case returns a flat list
    """
    if not isinstance(l, list): return [l]
    if l==[]: return []
    return functools.reduce(lambda xs,ys: xs+ys, map(flatten, l))

def stagger(xs, ys):
    """
    stagger(['a','b','c'],[1,2]) == ['a',1,'b',2,'c']
    """
    xs = iter(xs)
    ys = iter(ys)
    zs = [next(xs)]
    for (y,x) in zip(ys,xs):
        zs.append(y)
        zs.append(x)
    return zs

def print_heads(notes):
    for note in notes:
        print()
        print(note.head)

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
    #TODO while preserving order.
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


def as_list(f):
    """ e.g.

    @as_list
    def f():
      \"\"\"docstring\"\"\"
      yield 1
      yield 2
    assert f.__doc__ == 'docstring'
    assert list(f()) == [1,2]

    """
    def casted_to_list(*args, **kwargs):
        return list(f(*args, **kwargs))
    casted_to_list.__name__ = f.__name__
    casted_to_list.__doc__ = f.__doc__
    return casted_to_list
