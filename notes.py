#!/usr/bin/python
from __future__ import division
from util import *
import db
import parse


""" e.g. note
-  -  -  -  -  -  -  -
A , B
< C
: x
= y
-> a
=> b
--> c
~> d
. words

"""

sep = '\n\n'
div = '-  -  -  -  -  -  -  -  -  -  -  -  -  -  -'
def is_div(line):
    return ('-----' in line) or ('- - -' in line) or ('-  -  -' in line)

def is_note(s):
    return s.strip() and s != sep and s != div

def aliases(head):
    return head.split(' , ')

def is_noun_phrase(line):
    pass

def is_verb_phrase(line):
    pass

class Note:
    """
    """
    notes = {} # the registry

    @typecheck
    def __new__(cls, head: str, body: list, file:str = ''):
        """
        : singleton factory

        : idempotent
        i.e.
        >>> data = {'head': 'head', 'body': ['body']}
        >>> assert Note(**data) == Note(**data)
        and Note must the same internally
        """
        body = [line.strip() for line in body if line.strip()]

        if head in cls.notes:
            note = cls.notes[head]
            note.body = merge(note.body, body)
        else:
            note = super().__new__(cls)
            note.head = head
            note.body = body
            cls.notes[head] = note

        note.file = file
        return note

    def __iter__(self):
        yield 'head', self.head
        yield 'body', self.body
        yield 'file', self.file
    def __bool__(self):
        return bool(self.head.strip())
    def __str__(self):
        return 'Note(head="%s")' % self.head
    def __hash__(self):
        return hash(self.head)
    def __cmp__(x, y):
        return cmp(x.head, y.head)

    def print(self):
        print()
        print('[head]', self.head)
        print('[file]', self.file)
        for line in self.body:
            print('[body]', line)

    @property
    def lines(self):
        return [self.head] + self.body
    @property
    def index(self):
        return self.head

def notify(file, lines):
    """TODO parses text => creates Note => updates DB
    """
    if not lines: return

    head = lines[0].strip()
    body = lines[1:] if len(lines)>1 else []

    if not head: return
    if is_div(head): notify(file, body)

    note = Note(head=head, body=body, file=file)
    return note

def get_notes():
    return list(Note.notes.values())

@typecheck
def get(query: str) -> Note:
    """fuzzy search, where the fuzz are:
    *TODO aliases
    *TODO synonyms
    *TODO typos
    """
    data = db.get(query)
    note = Note(**data)
    return note
