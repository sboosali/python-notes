from contextlib import contextmanager

import pymongo

from util import *
import config
from Edge import Edge


host = config.db['mongo_host']
port = config.db['mongo_port']

client = pymongo.MongoClient(host, port)
database = client.notes

_default_collection = 'notes'
_test_collection = 'test'
_collection = _default_collection

def test():
    collection(_test_collection)

def untest():
    collection(_test_collection).remove()

@contextmanager
def testing():
    test()
    yield
    untest()

def collection(name :str = None) -> 'Collection':
    ''': box'''
    global _collection

    # setter
    if name is not None:
        _collection = name

    # getter
    return database[_collection]

@contextmanager
def as_collection(new):
    old = collection().name
    collection(new)
    yield
    collection(old)

collection().create_index('node')

# # # # # # # # # # # # # # # # # # # # # # # # # #

def find(query=None, **kwargs):
    '''

    e.g. nodes = db.find({'node': {'$exists': True}})

    '''
    if query is None: query = {}
    fields = dict_merge({'_id': False}, kwargs.pop('fields', {}))
    return list(collection().find(query, fields=fields, **kwargs))

def find_one(query, **kwargs):
    fields = dict_merge({'_id': False}, kwargs.pop('fields', {}))
    return collection().find_one(query, fields={'_id': False}, **kwargs)

def stats():
    """(all sizes in bytes)"""
    return database.command('collstats', 'notes')

def graph():
    nodes = find({'node': {'$exists': True}})
    nodes = [_['node'] for _ in nodes]

    edges = find({'edge': {'$exists': True}})
    edges = [edge for _ in edges for edge in _['nodes']]
    edges = [Edge.from_iter(edge) for edge in edges]

    return nodes, edges

@typecheck
def put(edge: Edge):
    '''
    : idempotent

    >>> put(Edge('like', ['x', 'y']))

    >>> x_node = find_one({'node': 'x'})
    >>> x_edges = x_node['edges']
    >>> pp(x_edges)
    [   {   'label': 'like',
            'line': {'file': '', 'text': '', 'lineno': 0},
            'nodes': ['x', 'y']}]

    '''
    for node in edge.nodes:
        put_in_node(node, edge)

def put_in_node(node, edge):
    query = {'node': node}
    update = {'$addToSet': {'edges': edge.json}}
    collection().update(query, update, upsert=True, multi=True)


if __name__ == "__main__":
    import doctest
    test()
    doctest.testmod()
#    with testing():
#        doctest.testmod()
