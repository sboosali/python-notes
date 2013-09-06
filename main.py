#!/usr/bin/python3
import argparse
import glob
import os

from util import *
import parse
import db
import notes as N


def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--test', action='store_true',
                      help='integration tests all options')
    args.add_argument('--head', action='store_true',
                      help='show all heads')
    args.add_argument('--freqs', action='store_true',
                      help='show operator frequencies')
    args.add_argument('--parse', action='store_true',
                      help='parse all heads')
    args.add_argument('--write', action='store_true',
                      help='write to database')
    args.add_argument('--get', type=str,
                      help='return the body of the head given')
    args.add_argument('--aliases', action='store_true',
                      help='shows all aliases')
    args.add_argument('--destroy', action='store_true',
                      help='destroy all documents in "notes" collection')
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
        db.upsert(**dict(note))

def main():
    args = get_args()

    if args.test:
        h1('TESTING...')
        args.files = ['tests/test.note']
        args.head = True
        args.freqs = True
        args.parse = True
        args.write = True
        args.aliases = True
        args.get = 'leonard cohen'

    files = args.files if args.files else get_dropbox_notes()

    for file in files:
        chars = open(file).read()
        blocks = chars.split('\n\n')
        blocks = [block.split('\n') for block in blocks]
        for lines in blocks:
            N.notify(file, lines)

    notes = N.get_notes()

    if args.destroy:
        h1('DESTROY')
        print(db.remove_collection())

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
            print(parse.head(note.head))

    if args.write:
        h1('WRITE')
        write_notes_to_database(notes)

    if args.get:
        h1('GET')
        note = N.get(args.get)
        note.print()

    if args.aliases:
        h1('ALIASES')
        for note in notes:
            aliases = parse.aliases(note.head)
            if aliases:
                print()
                print(note.head)
                print(aliases)


if __name__=='__main__':
    main()
