import yaml


db = yaml.load(open('db.yaml'))

syntax = yaml.load(open('syntax.yaml'))
operators = syntax['operators']
min_spaces = syntax['min_spaces']

semantics = yaml.load(open('semantics.yaml'))
concrete = semantics['concrete']
