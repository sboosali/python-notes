from operator import itemgetter

import config


def reduce(op, words):
    reducer = config.chain[op] #TODO
    reducer = globals()[reducer]
    return op if not words else reducer(words)

left = itemgetter(0)
right = itemgetter(-1)
