#!/usr/bin/python3
import argparse
import glob
import os

from util import *
import parse
import notes as N
import db


def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--test', '-t',
                      action='store_true',
                      help='integration tests all options')
    args.add_argument('-v',
                      action='store_true',
                      help='verbose option')
    args.add_argument('--head',
                      action='store_true',
                      help='show all heads')
    args.add_argument('--freqs',
                      action='store_true',
                      help='show operator frequencies')
    args.add_argument('--parse-all',
                      action='store_true',
                      help='parse all heads')
    args.add_argument('--parse', '-p',
                      type=str,
                      default='',
                      help='takes a string and parses it')
    args.add_argument('--write',
                      action='store_true',
                      help='write to database')
    args.add_argument('--get',
                      type=str,
                      help='return the body of the head given')
    args.add_argument('--aliases',
                      action='store_true',
                      help='shows all aliases')
    args.add_argument('--destroy',
                      action='store_true',
                      help='destroy all documents in "notes" collection')
    args.add_argument('--note', '-n',
                      action='store_true',
                      help='parse all notes')
    args.add_argument('files',
                      nargs='*',
                      help='zero or more `.note` files (defaults to Dropbox)')
    args = args.parse_args()
    return args

def get_dropbox_notes():
    files = '~/Dropbox/*.note'
    files = glob.glob(os.path.expanduser(files))
    files += [os.path.expanduser('~/Dropbox/.note')]
    return files

def make_lines(block):
    return [line.strip() for line in block if N.is_line(line)]

def make_blocks(chars):
    blocks = [block.split('\n') for block in chars.split('\n\n')]
    blocks = [make_lines(block) for block in blocks]
    return blocks

def make_notes(files):
    notes = []

    for file in files:
        chars = open(file).read()
        blocks = make_blocks(chars)
        notes.extend(filter(bool, (N.notify(file, line) for line in blocks)))

    return notes

def print_note(note: dict):
    print('[head]', note['head'])
    for line in note['file']:
        print('[file]', line)
    for line in note['body']:
        print('[body]', line)

def write_notes_to_database(notes):
    pass

def print_heads(notes):
    for note in notes:
        print()
        print(note.head)
    print()

def print_notes(notes):
    for note in notes:
        print()
        print()

        print('>>>> %s' % note.head)
        head, body = parse.note(note.head, note.body)
        for edge in (head.edges or []):
            print('     %s' % str(edge))

        for line, limb in zip(note.body, body):
            print('>>>> %s' % line)
            for edge in (limb.edges or []):
                print('     %s' % str(edge))

    print()
    print()

def print_parse(parsed):
    width = max(len(key) for key in parsed._fields)
    print()

    for key, val in parsed._asdict().items():
        first = True
        key = str(key).ljust(width)
        print(' '.ljust(width) + ' |')

        if isinstance(val, list):
            for _ in val:
                if first:
                    print('%s |' % key + (' %s' % (_,)))
                    first = False
                else:
                    print(' '.ljust(width) + ' |'  + (' %s' % (_,)))

        else:
            print('%s | %s' % (key, val))

    print()

def main():
    args = get_args()

    if args.test:
        print()
        print('= = = = = = = = = = = = = = = = = = = = ')
        print('= = = = = = = = TESTING = = = = = = = =')
        print('= = = = = = = = = = = = = = = = = = = = ')
        print()
        args.files = ['test.note']
        args.note = True
        db.test()

    files = args.files if args.files else get_dropbox_notes()
    notes = make_notes(files)

    if args.destroy:
        if args.test: h1('DESTROY')
        print(db.collection.remove())

    if args.head:
        if args.test: h1('HEAD')
        print_heads(notes)

    if args.freqs:
        if args.test: h1('FREQS')
        print_first_token_frequencies(notes)

    if args.write:
        if args.test: h1('WRITE')
        write_notes_to_database(notes)

    if args.note:
        if args.test: h1('NOTES')
        print_notes(notes)

    if args.parse:
        head, _ = parse.note(args.parse)
        print_parse(head)

    if args.get:
        if args.test: h1('GET')
        note = db.get(args.get)
        print_note(note)


if __name__=='__main__':
    try:
        main()
    finally:
        db.untest()
