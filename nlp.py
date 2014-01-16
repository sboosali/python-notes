import nltk

from util import *
from grammar import grammar


parser = nltk.parse.ShiftReduceParser(grammar, trace=0)
def parse(s): yield from parser.nbest_parse(s.split())

def show(line, trees):
    print()
    print(line)
    print(''.join('-' for _ in line))
    for i, tree in enumerate(trees):
        print('%s. %s' % (i+1, tree))
    print()


if __name__=='__main__':
    line = 'the dog eats the cat'
    trees = parse(line)
    show(line, trees)
