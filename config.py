import yaml
from collections import defaultdict


db = yaml.load(open('db.yaml'))

syntax = yaml.load(open('syntax.yaml'))
operators = syntax['operators']
min_spaces = defaultdict(
    lambda: syntax['default_min_spaces'],
    syntax['min_spaces'])

semantics = yaml.load(open('semantics.yaml'))
meaning = defaultdict(
    lambda: None,
    semantics['meaning'])
