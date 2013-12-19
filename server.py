'''
HTTP API

(POST because of length)

POST /parse
: text => edges

POST /draw
: text => graph

'''
import flask
from flask import request

from util import *
import notes as N
import parse
import visualization


app = flask.Flask('Notes', static_folder='static', static_url_path='')

@app.route('/parse', methods=['POST'])
def API_parse_notes():
    '''

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

    $
    curl  "http://127.0.0.1:5000/draw"  -H "Content-Type:text/json"  -d '{"notes": "\n\nA2\n= x3\n: y4\n\nB6\n~ z7\n"}'

    '''
    text = request.get_json(force=True)['notes']
    response = draw_graph(text)
    return flask.jsonify(**response)

def draw_graph(text):
    return text_to_graph(text)

def line_to_edges(line):
    edges = line.graph.edges
    for edge in edges:
        edge.line = line.line
        yield edge

def text_to_graph(text):
    lines = list(parse.parse(text))

    edges = [edge for line in lines for edge in line_to_edges(line)]
    nodes = remove_duplicates(node for line in lines for node in line.graph.nodes)
    graph = visualization.logic_graph_to_visual_graph(nodes, edges)

    return graph


if __name__ == "__main__":
    import argparse
    args = argparse.ArgumentParser()
    args.add_argument('-p', '--port',
                      type=int, default=5000,
                      help='the port')
    args = args.parse_args()

    app.run(debug=True, port=args.port)
