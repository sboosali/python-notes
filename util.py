from collections import defaultdict
import functools


def has_no_duplicates(l):
    return len(l) == len(set(l))

def flatten(l):
    """eg [[1],[[2,[3]],[4]],5] => [1,2,3,4,5]

    each case returns a flat list
    """
    if not isinstance(l, list): return [l]
    if l==[]: return []
    return functools.reduce(lambda xs,ys: xs+ys, map(flatten, l))

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
