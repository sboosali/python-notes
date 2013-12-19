import pymongo

from util import *
import config
import Edge


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
    collection(_default_collection)

def collection(name :str =None) -> 'Collection':
    ''': box'''
    global _collection

    # setter
    if name is not None:
        _collection = name

    # getter
    return database[_collection]

collection().create_index('node')
collection().create_index('edge')

# # # # # # # # # # # # # # # # # # # # # # # # # #

def find(query=None, **kwargs):
    '''

    e.g.
    >>> nodes = db.find({'node': {'$exists': True}})

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
    edges = [Edge.from_list(edge) for edge in edges]

    return nodes, edges


# @typecheck
# def get(head: str):
#     """get a note by one of its heads from the database if it exists
#     (exclude mongo's "_id")
#     """
#     select = {'head': {'$all': [head]}}
#     exclude = {'_id':False}
#     note = collection().find_one(select, exclude)

#     if note:
#         note['head'] = head
#     else:
#         note = {'head': head, 'body': [], 'file': []}
#     return note

# # @typecheck
# # def add(heads: list, body: list, file: list = ()):
# #     """add a note """
# #     select = {'head': {'$all': heads}}
# #     update = {'head': heads,
# #               'body': body,
# #               'file': file}
# #     collection().update(select, update, upsert=True)
# #     return collection().update(select, update, upsert=True, multi=True)

# @typecheck
# def put(head: str, body: list, file: str = ''):
#     return puts([head], body, [file])

# @typecheck
# def puts(heads: list, body: list, files: list = ()):
#     select = {'head': {'$all': heads}}

#     update = {'$addToSet': {'head': {'$each': heads}}}
#     collection().update(select, update, upsert=True, multi=True)

#     update = {'$addToSet': {'file': {'$each': files}},
#               '$pushAll': {'body': body}}
#     collection().update(select, update, multi=True)
