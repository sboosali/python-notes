'''


hypergraph
----------

hypergraph  <  bipartite graph  where A=nodes B=edges


node schema
-----------

{'node': str,
 'edges': [[str]]}


edge schema
-----------

{'edge': str,
 'nodes': [[str]]}


'''
from util import *
import db


def save(*edge, collection=None):
    '''

    >>> db.test()

    # motivation: "x , y < z"
    >>> save(',', 'x', 'y')
    >>> pp(db.find_one({'node': 'y'}))
    {'edges': [[',', 'x', 'y']], 'node': 'y'}

    >>> save('<', 'y', 'z')
    >>> pp(db.find_one({'node': 'y'}))
    {'edges': [[',', 'x', 'y'], ['<', 'y', 'z']], 'node': 'y'}

    >>> pp(db.find_one({'node': 'x'}))
    {'edges': [[',', 'x', 'y']], 'node': 'x'}

    >>> pp(db.find_one({'edge': ','}))
    {'edge': ',', 'nodes': [[',', 'x', 'y']]}

    >>> pp(db.find_one({'edge': '<'}))
    {'edge': '<', 'nodes': [['<', 'y', 'z']]}

    # hyperedge: "a < b where c"
    >>> save('< where', 'a', 'b', 'c')
    >>> pp(db.find_one({'edge': '< where'}))
    {'edge': '< where', 'nodes': [['< where', 'a', 'b', 'c']]}

    >>> db.untest()

    '''
    if not collection: collection = db.collection

    label, *nodes = edge
    if is_node(edge):
        save_node(label, collection=collection)
    else:
        save_edge(edge, collection=collection)

def save_edge(edge, collection=None):
    if not collection: collection = db.collection
    label, *nodes = edge

    query = {'edge': label}
    update = {'$addToSet': {'nodes': edge}}
    collection.update(query, update, upsert=True)

    for node in nodes:
        save_node(node, edge, collection)

def save_node(node, edge=None, collection=None):
    if not collection: collection = db.collection

    query = {'node': node}
    update = {'$addToSet': {'edges': edge}} if edge else {}
    collection.update(query, update, upsert=True)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
