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
        return f(*args, **kwargs)
    return typechecked
