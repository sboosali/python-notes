notes
=====

e.g.
====
./command_line.py -t
curl  "http://127.0.0.1:5000/draw"  -H "Content-Type:text/json"  -d '{"notes": "\n\nA2\n= x3\n: y4\n\nB6\n~ z7\n"}'

repr
====
edge ∈ mongodb = {'edge': '<', 'nodes': [{'nodes': ['x', 'y'], 'lineno': 0}]}
edge ∈ python = Edge(label='<', nodes=['x', 'y'], lineno=0)
edge ∈ javascript = {'name': '<', 'source': _.index('x'), 'target': _.index('y'), 'lineno': 0}
