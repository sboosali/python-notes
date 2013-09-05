#!/usr/bin/python3
from __future__ import division
import glob
import os
import argparse
import db
from util import *
from notes import Note, notify, div, sep
from parsing import parse_head


def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--head', action='store_true',
                      help='show all heads')
    args.add_argument('--freqs', action='store_true',
                      help='show operator frequencies')
    args.add_argument('--parse', action='store_true',
                      help='parse all heads')
    args.add_argument('--write', action='store_true',
                      help='write to database')
    args.add_argument('--test', action='store_true',
                      help='integration tests all options')
    args.add_argument('files', nargs='*',
                      help='zero or more `.note` files (defaults to Dropbox)')
    args = args.parse_args()
    return args

def get_dropbox_notes():
    files = '~/Dropbox/*.note'
    files = glob.glob(os.path.expanduser(files))
    files += [os.path.expanduser('~/Dropbox/.note')]
    return files

def write_notes_to_database(notes):
    for note in notes:
        note.print()
        db.upsert(dict(note))

def main():
    args = get_args()

    if args.test:
        h1('TESTING...')
        args.files = ['tests/test.note']
        args.head = True
        args.freqs = True
        args.parse = True
        args.write = True

    files = args.files if args.files else get_dropbox_notes()

    files = [open(file).read() for file in files]
    chars = '\n\n'.join(files)
    lines = chars.split('\n')
    sects = chars.split(div)

    blocks = chars.split(sep)
    blocks = [block.split('\n') for block in blocks]
    for lines in blocks:
        notify(lines)
    notes = list(Note.notes.values())

    if args.head:
        h1('HEAD')
        print_heads(notes)

    if args.freqs:
        h1('FREQS')
        print_first_token_frequencies(notes)

    if args.parse:
        h1('PARSE')
        for note in notes:
            print()
            print(note.head)
            print(parse_head(note.head))

    if args.write:
        h1('WRITE')
        write_notes_to_database(notes)

if __name__=='__main__':
    main()
