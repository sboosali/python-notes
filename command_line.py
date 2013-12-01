#!/usr/bin/python3
import argparse

from util import *
import parse
import notes as N
import db
import visualization
import disk


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
    args.add_argument('--aliases',
                      action='store_true',
                      help='shows all aliases')
    args.add_argument('--note', '-n',
                      action='store_true',
                      help='parse notes')
    args.add_argument('--edges', '-e',
                      action='store_true',
                      help='takes .note files and visualizes the edges')

    args.add_argument('--get',
                      type=str,
                      help='return the body of the head given')
    args.add_argument('--write',
                      action='store_true',
                      help='write to database')
    args.add_argument('--destroy',
                      action='store_true',
                      help='destroy all documents in "notes" collection')
    args.add_argument('--visualize',
                      type=str,
                      default='',
                      help='visualize a collection in the database by printing json for d3')

    args.add_argument('-p',
                      type=str,
                      default='',
                      help='takes a string and parses it')
    args.add_argument('--parse',
                      type=str,
                      default='',
                      help='takes a file and parses it')

    args.add_argument('files',
                      nargs='*',
                      help='zero or more `.note` files (defaults to Dropbox)')
    args = args.parse_args()
    return args

def main():
    args = get_args()

    if args.test:
        print()
        print('= = = = = = = = = = = = = = = = = = = = ')
        print('= = = = = = = = TESTING = = = = = = = =')
        print('= = = = = = = = = = = = = = = = = = = = ')
        print()
        args.files = ['test/example.note']
        args.note = True
        args.write = True
        args.visualize = True
        db.test()

    if args.parse:
        args.files = [args.parse]

    files = disk.read_files(args.files)
    notes = N.make_notes(files)

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
        N.write_notes_to_database(notes)

    if args.p:
        head, _ = parse.note(args.p)
        print_parse(head)

    if args.parse:
        print()
        for note in notes:
            head, body = parse.note(note.head, note.body)
            print(head.edges)
            for limb in body:
                print(limb.edges)
            print()

    if args.get:
        if args.test: h1('GET')

        print()
        results = N.get(args.get)

        for result in results:
            print(result)

        print()

    if args.note:
        if args.test: h1('NOTES')
        N.print_notes(notes)

    if args.visualize:
        if args.test: h1('GRAPH')
        nodes, edges = db.graph()
        graph = visualization.logic_graph_to_visual_graph(nodes, edges)
        print(graph)
        print()


if __name__=='__main__':
    main()