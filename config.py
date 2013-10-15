import yaml
from collections import defaultdict


db = yaml.load(open('db.yaml'))


syntax = yaml.load(open('syntax.yaml'))

operators = syntax['operators']

order = syntax['order']

default_min_spaces = syntax['min_spaces'].pop('__default__')
min_spaces = defaultdict(lambda: default_min_spaces, syntax['min_spaces'])

default_chain = syntax['chain'].pop('__default__')
chain = defaultdict(lambda: default_chain, syntax['chain'])


semantics = yaml.load(open('semantics.yaml'))
default_verb = semantics['default_verb']
verbs = defaultdict(lambda: default_verb, semantics['verbs'])
