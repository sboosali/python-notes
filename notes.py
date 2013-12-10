import re
import io

from util import *
import parse
import Graph
import query
import syntax
from Line import Line


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
        '''Note : {head: str, body: [str]} => [str]'''
        yield self.head
        yield from self.body
    def __bool__(self):
        return bool(self.head.strip())
    def __repr__(self):
        #TODO fields = OrderedDict(self) # show only if truthy like Op
        #TODO but ** casts to (unordered) dict
        if not self.file:
            return 'Note(head=%r, body=%r)' % (self.head, self.body)
        else:
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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

sep = '\n\n'
div = '-  -  -  -  -  -  -  -  -  -  -  -  -  -  -'

def is_div(line):
    return ('-----' in line) or ('- - -' in line) or ('-  -  -' in line)

def is_line(line):
    return line.strip() and not is_div(line)

def make_lines(block):
    return [line.strip() for line in block if is_line(line)]

@strict
def number_lines(file: [Note]) -> [Note]:
    linenos = count()
    for note in file:
        yield [Line.Line(line, lineno=next(linenos)) for line in note]

whitespace_regex = r'^\s*$'
def is_white(line):
    '''
    # >>> is_white("")
    # True
    # >>> is_white("\n\t\r ")
    # True
    # >>> is_white("\n\t\r x")
    # False
    '''
    return bool(re.search(whitespace_regex, line))

def is_sep(line):
    return is_white(line) or is_div(line)

def read(text: str, file='') -> [Note]:
    '''

    >>> text = """
    ...
    ... A2
    ... = x3
    ... : y4
    ...
    ... B6
    ... ~ z7
    ...
    ... """

    >>> for note in read(text): print(note)
    Note(head=Line('A2', lineno=2), body=[Line('= x3', lineno=3), Line(': y4', lineno=4)])
    Note(head=Line('B6', lineno=6), body=[Line('~ z7', lineno=7)])

    '''
    # before
    lines = io.StringIO(text).readlines()
    block = []

    # during
    for lineno, line in enumerate(lines):
        line = Line(line.strip(), lineno=lineno, file=file)
        if line:
            block.append(line)

        if is_sep(line):
            if block:
                head, *body = block
                note = Note(head=head, body=body, file=file)
                yield note
            block = []

    # after
    #HACK need better pattern than "reset and last"
    if block:
        head, *body = block
        note = Note(head=head, body=body, file=file)
        yield note

def make_notes(files):
    notes = []

    for file, chars in files:
        blocks = read(chars)
        notes.extend(filter(bool, (notify(file, line) for line in blocks)))

    return notes

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def notify(file, lines):
    """makes Notes"""
    if not lines: return
    head, *body = lines
    note = Note(head=head, body=body, file=file)
    return note

def partition_arcs(arcs):
    '''
    : edges => nodes, edges
    '''
    _, edges = partition(is_node, arcs)
    edges = list(edges)
    nodes = list({node for _, *nodes in edges for node in nodes})
    return nodes, edges

def write(note):
    lines = parse.note(note, lines=True)
    arcs = parse.edges(lines)
    nodes, edges = partition_arcs(arcs)

    for node in nodes:
        Graph.save_node(node)

    for edge in edges:
        Graph.save_edge(edge)

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

def write_notes_to_database(notes):
    for note in notes:
        note.print()
        nodes, edges = write(note)
        for node in nodes:
            print('[node]', node)
        for edge in edges:
            print('[edge]', edge)
    print()

def print_notes(notes):
    for note in notes:
        print()
        print()

        print('>>>> %s' % note.head)
        head, body = parse.note(note)
        for edge in (head.graph.edges or []):
            print('     %s' % str(edge))

        for line, limb in zip(note.body, body):
            print('>>>> %s' % line)
            for edge in (limb.graph.edges or []):
                print('     %s' % str(edge))

    print()
    print()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
