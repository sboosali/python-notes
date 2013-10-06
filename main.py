#!/usr/bin/python3
import argparse
import glob
import os

from util import *
import parse
from parse import AST
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
    db.remove_collection() #TODO
    for note in notes:
        note.print()
        tree = parse.AST(parse.head(note.head))
        if 'alias' in tree.edges:
            make.alias(tree.nodes, note.body, note.file)
        else:
            db.upsert(**dict(note))

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

def print_aliases(notes):
    for note in notes:
        cst = parse.head(note.head)
        ast = AST(cst)
        if 'alias' in ast.edges:
            print()
            print(note.head)
            print(cst.op, '=>', ast.edges)
            print(ast)

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

    files = args.files if args.files else get_dropbox_notes()
    notes = make_notes(files)

    if args.destroy:
        h1('DESTROY')
        print(db.remove_collection())

    if args.head:
        h1('HEAD')
        print_heads(notes)

    if args.freqs:
        h1('FREQS')
        print_first_token_frequencies(notes)

    if args.write:
        h1('WRITE')
        write_notes_to_database(notes)

    if args.aliases:
        h1('ALIASES')
        print_aliases(notes)

    if args.parse_all:
        h1('PARSE')
        for note in notes:
            print()
            print(note.head)
            tree = parse.head(note.head, v=args.v)
            print(tree)

    if args.parse:
        print(parse.head(args.parse))

    if args.get:
        h1('GET')
        note = N.get(args.get)
        note.print()

if __name__=='__main__':
    main()
