from util import *
import parse
import db


def alias(nodes, body, file):
    nodes = [parse.unparse(head) for head in nodes]
    db.puts(nodes, body, [file])

def edge(nodes):
    return nodes
