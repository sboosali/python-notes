from util import *
import parse
import graph
import query
import syntax


sep = '\n\n'
div = '-  -  -  -  -  -  -  -  -  -  -  -  -  -  -'
def is_div(line):
    return ('-----' in line) or ('- - -' in line) or ('-  -  -' in line)

def is_note(s):
    return s.strip() and s != sep and s != div

def aliases(head):
    return head.split(' , ')

def is_line(line):
    return line.strip() and not is_div(line)

def is_noun_phrase(line):
    pass

def is_verb_phrase(line):
    pass

class Note:
    '''

    e.g. note

        -  -  -  -  -  -  -  -
        A , B < C
        = D
        -> x -> y
        . words

    '''

    @typecheck
    def __init__(self, head: str, body: list= None, file: str= ''):
        if body is None: body = []
        self.head = head.strip()
        self.file = file
        self.body = [line.strip() for line in body if line.strip()]

    def __iter__(self):
        '''for `dict()`'''
        yield 'head', self.head
        yield 'body', self.body
        yield 'file', self.file
    def __bool__(self):
        return bool(self.head.strip())
    def __repr__(self):
        return 'Note(head=%r, body=%r, file=%r)' % (self.head, self.body, self.file)
    def __hash__(self):
        return hash(self.head)
    def __cmp__(self, other):
        return cmp(self.head, other.head)

    def print(self):
        print()
        print('[head]', self.head)
        print('[file]', self.file)
        for line in self.body:
            print('[body]', line)

    @property
    def lines(self):
        return [self.head] + self.body

def notify(file, lines):
    """makes Notes"""
    if not lines: return
    head, *body = lines
    note = Note(head=head, body=body, file=file)
    return note

def partition_arcs(arcs):
    nodes, edges = partition(is_node, arcs)
    return list(nodes), list(edges)

def write(note):
    head, body = parse.note(note.head, note.body)

    arcs = head.edges
    for limb in body:
        for arc in limb.edges:
            arcs.append(arc)

    nodes, edges = partition_arcs(arcs)

    for node in nodes:
        graph.save(node)

    for edge in edges:
        graph.save(*edge)

    return nodes, edges

def get(line):
    '''

    e.g.
    query   "_ -> + ACh"
    parsed  ('causes', '_', '+ ACh')
    schema  {'edge': 'causes',
             'nodes': [... ['causes', 'piracetam', '+ ACh'], ...]}

    '''
    results = query.get(line)
    for result in results:
        label, *nodes = result

        if label:
            operator = syntax.meaning[label]
            edge = operator.format(*nodes)
            yield edge
        else:
            node, = nodes
            yield node
