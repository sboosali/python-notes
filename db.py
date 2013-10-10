import pymongo
from util import *
from notes import Note
import config


host = config.db['mongo_host']
port = config.db['mongo_port']

client = pymongo.MongoClient(host, port)
database = client.notes
collection = database.notes

collection.create_index('head')


def stats():
    """(all sizes in bytes)"""
    return database.command('collstats', 'notes')

@typecheck
def get(head: str):
    """get a note by one of its heads from the database if it exists
    (exclude mongo's "_id")
    """
    select = {'head': {'$all': [head]}}
    exclude = {'_id':False}
    note = collection.find_one(select, exclude)

    if note:
        note['head'] = head
    else:
        note = {'head': head, 'body': [], 'file': []}
    return note

# @typecheck
# def add(heads: list, body: list, file: list = ()):
#     """add a note """
#     select = {'head': {'$all': heads}}
#     update = {'head': heads,
#               'body': body,
#               'file': file}
#     collection.update(select, update, upsert=True)
#     return collection.update(select, update, upsert=True, multi=True)

@typecheck
def put(head: str, body: list, file: str = ''):
    return puts([head], body, [file])

@typecheck
def puts(heads: list, body: list, files: list = ()):
    select = {'head': {'$all': heads}}

    update = {'$addToSet': {'head': {'$each': heads}}}
    collection.update(select, update, upsert=True, multi=True)

    update = {'$addToSet': {'file': {'$each': files}},
              '$pushAll': {'body': body}}
    collection.update(select, update, multi=True)
