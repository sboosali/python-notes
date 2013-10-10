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

def is_line(line):
    return line.strip() and not is_div(line)

def is_noun_phrase(line):
    pass

def is_verb_phrase(line):
    pass

class Note:
    notes = [] # the registry

    @typecheck
    def __new__(cls, head: str, body: list, file: str = ''):
        self = super().__new__(cls)
        cls.notes.append(self)

        self.head = head.strip()
        self.file = file
        self.body = [line.strip() for line in body if line.strip()]
        return self

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
    def __cmp__(self, other):
        return cmp(self.head, other.head)

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
    """makes Notes"""
    if not lines: return
    head, *body = lines
    note = Note(head=head, body=body, file=file)
    return note
