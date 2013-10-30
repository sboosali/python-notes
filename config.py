import yaml
from collections import defaultdict
from collections import OrderedDict
from multimethod import multimethod
from copy import copy

from util import *


db = yaml.load(open('db.yaml'))

syntax = yaml.load(open('syntax.yaml'))

operators = yaml.load(open('operators.yaml'))
default_operator, = operators.pop('__default__')

operator_precedence = syntax['precedence']


visualization = yaml.load(open('visualization.yaml'))
order = visualization['order']


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


parser_precedence = syntax['parsers']

parsers = yaml.load(open('parsers.yaml'))
default_parser = parsers['default']
for parser, definition in copy(parsers).items():
    definition = dict_merge(default_parser, definition)
    parsers[parser] = definition


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    pp(parsers)
