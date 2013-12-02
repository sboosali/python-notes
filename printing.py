from util import *

def h1(text):
    print()
    print('----- %s ------' % text)
    print()

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

def pp(o: object):
    return pprint.PrettyPrinter(indent=4).pprint(o)

def print_list(xs, **kwargs):
    for x in xs:
        print(x, **kwargs)

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
