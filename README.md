notes
=====


e.g.
====

./command_line.py -t

python server.py

curl  "http://127.0.0.1:5000/draw"  -H "Content-Type:text/json"  -d '{"notes": "\n\nA2\n= x3\n: y4\n\nB6\n~ z7\n"}'


heroku
======

foreman start => exec Procfile => python server.py => import from requirements.txt


repr
====

edge ∈ mongodb = {'node': ..., 'edges': [{'nodes': ['x', 'y'], 'lineno': 0}]}

edge ∈ python = Edge(label='<', nodes=['x', 'y'], lineno=0)

edge ∈ javascript = {'name': '<', 'source': _.index('x'), 'target': _.index('y'), 'lineno': 0}


schema
======

{'node': str,
 'edges': [{'label': str,
            'nodes': [str],
            'line': {'text': str,
                     'lineno': int,
                     'file': str}
            }]}
