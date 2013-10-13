#!/usr/bin/python3
import argparse
import glob
import os

from util import *
import parse
import db
import notes as N
import make


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
    args.add_argument('--parse',
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

def write_notes_to_database(notes):
    db.collection.remove()
    for note in notes:
        note.print()
        tree = parse.AST(parse.head(note.head))
        if 'alias' in tree.verbs:
            make.alias(tree.nouns, note.body, note.file)
        else:
            db.put(**dict(note))

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
    print()
    print('[head]', note['head'])
    for line in note['file']:
        print('[file]', line)
    for line in note['body']:
        print('[body]', line)

def print_aliases(notes):
    for note in notes:
        cst = parse.head(note.head)
        ast = parse.AST(cst)
        if 'alias' in ast.verbs:
            print()
            print(note.head)
            print(cst.op, '=>', ast.verbs)
            print(ast)

def print_heads(notes):
    for note in notes:
        cst = parse.head(note.head)
        if len(cst)>1:
            print()
            print(cst)

def main():
    args = get_args()

    if args.test:
        h1('TESTING...')
        args.files = ['tests/test.note']
        args.head = True
        args.freqs = True
        args.parse_all = True
        args.write = True
        args.aliases = True
        args.get = 'leonard cohen'
        db.collection = db.database.test

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

    # if args.write:
    #     if args.test: h1('WRITE')
    #     write_notes_to_database(notes)

    # if args.aliases:
    #     if args.test: h1('ALIASES')
    #     print_aliases(notes)

    if args.parse_all:
        if args.test: h1('PARSE')
        for note in notes:
            print()
            print(note.head)
            tree = parse.head(note.head)
            print(tree)

    if args.parse:
        for parsed in parse._head(args.parse):
            print(parsed)

    if args.get:
        if args.test: h1('GET')
        note = db.get(args.get)
        print_note(note)


if __name__=='__main__':
    main()
