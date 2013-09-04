#!/usr/bin/python3
from __future__ import division
import glob
import os
import argparse
from util import *
from notes import *


def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--head', action='store_true')
    args.add_argument('--parse', action='store_true')
    args.add_argument('--write', action='store_true')
    args.add_argument('--freqs', action='store_true')
    args = args.parse_args()
    return args

def debug_on_error(f):
    def debugged_on_error(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except Exception as e:
            print();print();print();
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())
            print();print();print();
            import pdb;pdb.set_trace()
            raise

    debugged_on_error.__name__ = 'debug_on_error(%s)' % f.__name__
    #import pdb; pdb.set_trace()
    return debugged_on_error

#@debug_on_error
def main():
    args = get_args()

    files = '~/Dropbox/*.note'
    files = glob.glob(os.path.expanduser(files))
    files += [os.path.expanduser('~/Dropbox/.note')]
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
        for note in notes:
            print()
            print(note.head)

    if args.parse:
        for note in notes:
            print()
            print(note.head)
            print(parse_head(note.head))

    if args.freqs:
        print_first_token_frequencies(notes)

if __name__=='__main__':
    main()
