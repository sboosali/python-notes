import pymongo
from util import *
from notes import Note


client = pymongo.MongoClient('localhost', 27017)
database = client.notes
collection = database['notes']

collection.create_index('head', unique=True)


@typecheck
def get(head: str):
    """get a note by its head from the database if it exists
    (exclude mongo's "_id")
    """
    db_note = collection.find_one({'head':head}, {'_id':False})
    return db_note if db_note else {'head':head, 'body': []}

@typecheck
def upsert(new_note: dict):
    """syncs the database with the python Note class,
    merging the bodies of notes who share heads.
    """
    head = new_note['head']
    old_note = get(head)
    body = merge(old_note['body'], new_note['body'])
    new_note = dict(Note(head=head, body=body))

    return collection.update({'head':head}, new_note, upsert=True)
