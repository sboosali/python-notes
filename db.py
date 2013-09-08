import pymongo
from util import *
from notes import Note
import yaml


config = yaml.load(open('config.yaml'))
host = config['mongo_host']
port = config['mongo_port']

client = pymongo.MongoClient(host, port)
database = client.notes
collection = database.notes

collection.create_index('head', unique=True)


def stats():
    """(all sizes in bytes)"""
    return database.command('collstats', 'notes')

@typecheck
def get(head: str) -> dict:
    """get a note by its head from the database if it exists
    (exclude mongo's "_id")
    """
    note = collection.find_one({'head':head}, {'_id':False})
    return note if note else {'head':head, 'body': []}

@typecheck
def upsert(head: str, body: list, file: str):
    """syncs the database with the python Note class,
    merging the bodies of notes who share heads.
    """
    old_note = get(head)
    body = merge(old_note['body'], body)
    new_note = dict(Note(head=head, body=body, file=file))

    return collection.update({'head':head}, new_note, upsert=True)

def remove_collection():
    return collection.remove()
