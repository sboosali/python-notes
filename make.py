from util import *
import parse
import db


def alias(heads, body, file):
    for head in heads:
        head = parse.unparse(head)
        db.upsert(head, body, file)
