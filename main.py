#!/usr/bin/python3
from __future__ import division
import glob
import os
import argparse
from util import *
from notes import Note, notify, div, sep
from parsing import parse_head


def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--head', action='store_true',
                      help='show all heads')
    args.add_argument('--parse', action='store_true',
                      help='parse all heads')
    args.add_argument('--freqs', action='store_true',
                      help='show operator frequencies')
    args.add_argument('--write', action='store_true',
                      help='write to database')
    args.add_argument('files', nargs='*',
                      help='zero or more `.note` files (defaults to Dropbox)')
    args = args.parse_args()
    return args

def get_dropbox_notes():
    files = '~/Dropbox/*.note'
    files = glob.glob(os.path.expanduser(files))
    files += [os.path.expanduser('~/Dropbox/.note')]
    return files

def main():
    args = get_args()

    files = args.files if args.files else get_dropbox_notes()

    files = [open(file).read() for file in files]
    chars = '\n\n'.join(files)
    lines = chars.split('\n')
    sects = chars.split(div)
    notes = notify(chars)

    blocks = chars.split(sep)
    blocks = [block.split('\n') for block in blocks]
    for lines in blocks:
        notify(lines)
    notes = Note.notes.values()

    if args.head:
        print_heads(notes)

    if args.freqs:
        print_first_token_frequencies(notes)

    if args.parse:
        for note in notes:
            print()
            print(note.head)
            print(parse_head(note.head))

if __name__=='__main__':
    main()
