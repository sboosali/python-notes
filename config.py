from util import *
import yaml
from collections import defaultdict
from collections import OrderedDict
from multimethod import multimethod


db = yaml.load(open('db.yaml'))


syntax = yaml.load(open('syntax.yaml'))

operators = syntax['operators']

order = syntax['order']

default_min_spaces = syntax['min_spaces'].pop('__default__')
min_spaces = defaultdict(lambda: default_min_spaces, syntax['min_spaces'])

default_chain = syntax['chain'].pop('__default__')
chain = defaultdict(lambda: default_chain, syntax['chain'])


@multimethod(str)
def escape_verbose_regex(s):
    return s.replace('#', r'\#')
@multimethod(dict)
def escape_verbose_regex(d):
    return {key: escape_verbose_regex(val) for key,val in d.items()}
tokens = syntax['tokens']
tokens = [(token, [escape_verbose_regex(regex) for regex in regexes])
          for _ in tokens
          for token, regexes in _.items()]


semantics = yaml.load(open('semantics.yaml'))
default_verb = semantics['default_verb']
verbs = defaultdict(lambda: default_verb, semantics['verbs'])


parsers = syntax['parsers']
parsers = OrderedDict([(parser, regex)
                       for _ in parsers
                       for (parser, regex) in _.items()])

if __name__ == "__main__":
    import doctest
    doctest.testmod()
