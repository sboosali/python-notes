from util import *
import parse
import db
from operator import itemgetter

left = itemgetter(0)
right = itemgetter(-1)

def alias(nodes, body, file):
    nodes = [parse.unparse(head) for head in nodes]
    db.puts(nodes, body, [file])

def edge(nodes):
    return nodes
