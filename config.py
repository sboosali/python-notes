import yaml
from collections import defaultdict


db = yaml.load(open('db.yaml'))


syntax = yaml.load(open('syntax.yaml'))

operators = syntax['operators']

order = syntax['order']

default_min_spaces = syntax['default_min_spaces']
min_spaces = defaultdict(lambda: default_min_spaces, syntax['min_spaces'])


semantics = yaml.load(open('semantics.yaml'))

default_verb = semantics['default_verb']
meaning = semantics['meaning']
for op, verb in meaning.items():
    if not verb:
        verb = default_verb
    if not isinstance(verb, list):
        verb = [verb]
    meaning[op] = verb
meaning = defaultdict(lambda: default_verb, meaning)

chaining = semantics['chaining']
default_chain = semantics['default_chain']
chaining = defaultdict(lambda: default_chain, chaining)
