import nltk

from util import *


# grammar = nltk.parse_fcfg(open('grammar.fcfg'))
# parser = nltk.parse.featurechart.FeatureChartParser(grammar, trace=2)
# def parse(s):
#     trees = parser.nbest_parse(s.split())
#     return trees[0] if trees else None
# line = 'this is a sentence'
# tree = parse(line)
# print(line)
# print(tree)

def txt_to_cfg(pos):
    file = 'grammar/%s' % pos
    lines = open(file).readlines()
    for line in lines:
        word = line.strip()
        word = word.replace(' ', '_')
        rule = "%s -> '%s'" % (pos, word)
        yield rule

parts_of_speech = ['N', 'V', 'DT']

def munge_terminals():
    for pos in parts_of_speech:
        yield '\n'
        yield from txt_to_cfg(pos)

def munge_grammar():
    cfg = open('grammar/rules').readlines()
    cfg.extend(munge_terminals())
    cfg = '\n'.join(cfg)
    grammar = nltk.parse_cfg(cfg)
    return grammar

grammar = munge_grammar()


if __name__=='__main__':
    print()
    print(grammar)
