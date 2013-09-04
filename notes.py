#!/usr/bin/python
from __future__ import division
from util import *


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

    notes = {} # registry
    def __new__(cls, head='', body=()):
        """
        : singleton factory
        """
        if head in cls.notes:
            note = cls.notes[head]
            note.body += body
        else:
            note = super().__new__(cls)
            note.head = head
            note.body = body
            cls.notes[head] = note
        return note

    def __bool__(self):
        return bool(self.head.strip())
    def __str__(self):
        return 'Note(head="%s")' % self.head
    def __hash__(self):
        return hash(self.head)
    def __cmp__(x, y):
        return cmp(x.head, y.head)

    @property
    def lines(self):
        return [self.head] + self.body
    @property
    def index(self):
        return self.head

def notify(lines):
    """ Takes a paragraph of text to a Note
    parses head
    parses each line in body
    """
    head = lines[0].strip()
    body = lines[1:] if len(lines)>1 else []

    if not head: return
    if is_div(head): return

    note = Note(head=head, body=body)
    return note

def get_aliases(line):
    aliases = line.split(', ')
    return aliases if len(aliases)>1 else None
