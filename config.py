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

def exclude_first(regex):
    return not isinstance(regex, dict)
tokens = syntax['tokens'].items()
tokens = [(thing, sorted(regexes, key=exclude_first))
          for thing, regexes in tokens]

semantics = yaml.load(open('semantics.yaml'))
default_verb = semantics['default_verb']
verbs = defaultdict(lambda: default_verb, semantics['verbs'])
