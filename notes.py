from util import *
import parse
import graph
import query
import syntax


sep = '\n\n'
div = '-  -  -  -  -  -  -  -  -  -  -  -  -  -  -'

def is_div(line):
    return ('-----' in line) or ('- - -' in line) or ('-  -  -' in line)

def is_line(line):
    return line.strip() and not is_div(line)

def make_lines(block):
    return [line.strip() for line in block if is_line(line)]

@typecheck
def read(text: str, as_note=False) -> list:
    '''

    >>> text = """
    ...
    ... A
    ... x
    ...
    ... B
    ... y
    ... z
    ...
    ... """
    >>> read(text)
    [['A', 'x'], ['B', 'y', 'z']]
    >>> read(text, as_note=True)
    [Note(head='A', body=['x'], file=''), Note(head='B', body=['y', 'z'], file='')]

    '''

    blocks = [block.split('\n') for block in text.split('\n\n')]
    blocks = [make_lines(block) for block in blocks]
    blocks = [block for block in blocks if block]

    if as_note:
        notes = [Note(head, body) for head, *body in blocks]
        return notes

    return blocks

def make_notes(files):
    notes = []

    for file, chars in files:
        blocks = read(chars)
        notes.extend(filter(bool, (notify(file, line) for line in blocks)))

    return notes

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
        #TODO fields = OrderedDict(self) # show only if truthy like Op
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
    _, edges = partition(is_node, arcs)
    edges = list(edges)
    nodes = list({node for _, *nodes in edges for node in nodes})
    return nodes, edges

def write(note):
    head, body = parse.note(note.head, note.body)

    arcs = head.edges
    for limb in body:
        for arc in limb.edges:
            arcs.append(arc)

    nodes, edges = partition_arcs(arcs)

    for node in nodes:
        graph.save_node(node)

    for edge in edges:
        graph.save_edge(edge)

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
        head, body = parse.note(note.head, note.body)
        for edge in (head.edges or []):
            print('     %s' % str(edge))

        for line, limb in zip(note.body, body):
            print('>>>> %s' % line)
            for edge in (limb.edges or []):
                print('     %s' % str(edge))

    print()
    print()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
