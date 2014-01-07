'''
the DB API's output

use `store.edge()`

'''
from util import *
from Edge import Edge
import db


@typecheck
def edge(arc: Edge, collection=None):
    '''

    # motivation: "x , y < z"
    >>> save(',', 'x', 'y')
    >>> pp(db.find_one({'node': 'y'}))
    {'edges': [[',', 'x', 'y']], 'node': 'y'}

    >>> save('<', 'y', 'z')
    >>> pp(db.find_one({'node': 'y'}))
    {'edges': [[',', 'x', 'y'], ['<', 'y', 'z']], 'node': 'y'}

    >>> pp(db.find_one({'node': 'x'}))
    {'edges': [[',', 'x', 'y']], 'node': 'x'}

    >>> pp(db.find_one({'edge': ','}))
    {'edge': ',', 'nodes': [[',', 'x', 'y']]}

    >>> pp(db.find_one({'edge': '<'}))
    {'edge': '<', 'nodes': [['<', 'y', 'z']]}

    # hyperedge: "a < b where c"
    >>> save('< where', 'a', 'b', 'c')
    >>> pp(db.find_one({'edge': '< where'}))
    {'edge': '< where', 'nodes': [['< where', 'a', 'b', 'c']]}

    '''
    if not collection: collection = db.collection()

    #TODO addToSet duplicates
    for vertex in arc.nodes:
        query = {'node': vertex}
        update = {'$addToSet': {'edges': arc.json}}
        collection.update(query, update, upsert=True)


if __name__ == "__main__":
    import db
    with db.testing():
        import doctest
        doctest.testmod()
