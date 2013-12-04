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
import notes
import parse
import visualization


app = flask.Flask('Notes', static_folder='static', static_url_path='')

@app.route('/parse', methods=['POST'])
def parse_notes():
    '''

    e.g.
    curl  "http://127.0.0.1:5000/parse"  -H "Content-Type:text/json"  -d @test.json

    '''
    text = request.get_json(force=True)['notes']
    response = _parse_notes(text)
    return flask.jsonify(**response)

def _parse_notes(text):
    edges = []
    for note in notes.read(text):
        head, *body = note
        arcs = parse.note(head, body, as_edges=True)
        edges.extend(arcs)
    return {'edges': edges}

@app.route('/draw', methods=['POST'])
def draw_graph():
    text = request.get_json(force=True)['notes']
    response = _draw_graph(text)
    return flask.jsonify(**response)

def _draw_graph(text):
    parseds = list(parse.parse(text))
    edges = remove_duplicates(edge for _ in parseds for edge in _.graph.edges)
    nodes = remove_duplicates(node for _ in parseds for node in _.graph.nodes)
    graph = visualization.logic_graph_to_visual_graph(nodes, edges)
    return graph


if __name__ == "__main__":
    app.run(debug=True)
