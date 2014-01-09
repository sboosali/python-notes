#!/usr/bin/python3
'''
HTTP API

(POST because of length)

POST /parse

POST /draw

GET /query

'''
import flask
from flask import request

from util import *
import notes as N
import parse
import visualization
import query
import db


app = flask.Flask('Notes', static_folder='static', static_url_path='')


@app.route('/parse', methods=['POST'])
def API_parse_notes():
    '''
    : text => edges

    $
    curl  "http://127.0.0.1:5000/parse"  -H "Content-Type:text/json"  -d '{"notes": "\n\nA2\n= x3\n: y4\n\nB6\n~ z7\n"}'

    '''
    text = request.get_json(force=True)['notes']
    edges = parse_notes(text)
    response = {'edges': edges}
    return flask.jsonify(**response)

@strict
def parse_notes(text):
    for edge in text_to_edges(text):
        yield edge_to_json(edge)

def text_to_edges(text):
    for note in N.read(text):
        lines = parse.note(note, lines=True)
        yield from parse.edges(lines)

def edge_to_json(edge):
    lineno = edge.line.lineno
    return {'edge': edge, 'lineno': lineno}


@app.route('/draw', methods=['POST'])
def API_draw_graph():
    '''
    : text => edges

    $
    curl  "http://127.0.0.1:5000/draw"  -H "Content-Type:text/json"  -d '{"notes": "\n\nA2\n= x3\n: y4\n\nB6\n~ z7\n"}'

    '''
    text = request.get_json(force=True)['notes']
    data = draw_graph(text)

    # None not a collection
    csrft = request.cookies.get('csrft')
    if csrft not in db.database.collection_names():
        csrft = random_string()

    files = [(text, '(client)')]
    notes = N.make_notes(files)
    with db.as_collection(csrft):
        db.collection().remove() # drops all documents, keeps collection
        N.write_notes_to_database(notes)
        #TODO expire collection

    response = flask.jsonify(**data)
    response.set_cookie('csrft', csrft)
    return response

def draw_graph(text):
    return text_to_graph(text)

def line_to_edges(parsed):
    edges = parsed.graph.edges
    for edge in edges:
        edge.line = parsed.line
        yield edge

def text_to_graph(text):
    lines = list(parse.parse(text))

    edges = [edge for line in lines for edge in line_to_edges(line)]
    nodes = remove_duplicates(node for line in lines for node in line.graph.nodes)
    graph = visualization.logic_graph_to_visual_graph(nodes, edges)

    return graph


@app.route('/query', methods=['POST'])
def API_query():
    '''
    : text => edges

    $
    curl  "http://127.0.0.1:5000/query"  -H "Content-Type:text/json"  -d '{"query": "_ -> + ACh"}'

    '''
    data = request.get_json(force=True)
    q = data['query']
    csrft = request.cookies.get('csrft')

    if not csrft:
        return

    with db.as_collection(csrft):
        results = list(edge.format() for edge in query.get(q))

    response = {'results': results}
    response = flask.jsonify(**response)
    return response


if __name__ == "__main__":
    import argparse
    args = argparse.ArgumentParser()
    args.add_argument('-p', '--port',
                      type=int, default=5000,
                      help='the port')
    args = args.parse_args()

    app.run(debug=True, port=args.port)
