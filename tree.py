from multimethod import multimethod
from collections import OrderedDict


def strict(f):
    def g(*args, **kwargs):
        return list(f(*args, **kwargs))
    return g

class Tree(tuple):
    '''
    Tree α : (α, [Tree α])
    '''
    def __new__(cls, tree):
        if not isinstance(tree, tuple):
            tree = (tree, ()) # leaf => tree

        value, trees = tree
        trees = tuple(Tree(tree) for tree in trees)

        return super().__new__(cls, (value, trees))

    def repr(self):
        '''nicens leaves and puts brackets around children.
        i.e. ('leaf', ()) => 'leaf'
        i.e. ('value', ('leaf')) => ('value', ['leaf'])
        '''
        value, trees = self
        if not trees:
            return value
        else:
            return (value, [tree.repr() for tree in trees])

    def __repr__(self):
        return 'Tree(%r)' % (self.repr(),)

    @strict
    def preorder(self):
        '''pre-order traversal'''
        value, trees = self

        yield value

        for tree in trees:
            for value in tree.preorder():
                yield value

    @strict
    def inorder(self):
        '''in-order traversal
        changes notation from infix to prefix for syntax trees
        '''
        value, trees = self

        if not trees:
            yield value

        else:
            trees = iter(trees)
            for t in trees:
                for v in t.inorder():
                    yield v
                break
            for t in trees:
                yield value
                for v in t.inorder():
                    yield v

    def is_leaf(self):
        value, trees = self
        return not trees

    def leaves(self):
        '''return just the leaves, with the tree's structure'''
        value, trees = self
        lists = [Tree((v, t)).leaves() if t else v for (v, t) in trees]
        return lists

    def map(self: 'Tree α', f: 'α -> β', g=lambda _: True) -> 'Tree β':
        value, trees = self

        trees = [tree.map(f, g) for tree in trees]
        value = f(value) if g(trees) else value

        return Tree((value, trees))

    def tmap(self, f: 'Tree α -> α | Tree α'):
        '''can 'grow' a tree by turning leaves into branches'''
        value, trees = self
        if not trees:
            return f(self)
        else:
            return Tree((value, [tree.tmap(f) for tree in trees]))

    def fold(self: 'Tree α', f: 'α, [α] -> α') -> 'α':
        value, trees = self

        values = tuple(tree.fold(f) for tree in trees)
        value = f(value, values)

        return value

    def filter(self: 'Tree α', f: 'α -> bool', g=lambda _: False) -> 'Tree α':
        '''skips root -> always returns Tree
        whenever `g` is true on the trees, ignore `f` on the value.
        '''
        value, trees = self

        trees = tuple(Tree((v,ts)).filter(f) for (v,ts) in trees if g(ts) or f(v))

        return Tree((value, trees))

def memoize(f, cache=None):
    if cache is None: cache = {}

    def memoized(*args, **kwargs):
        if args not in cache:
            cache[args] = f(*args, **kwargs)
        return cache[args]

    memoized.__name__ = f.__name__
    memoized.cache = cache
    return memoized

def Graph(tree, f):
    f = memoize(f, cache=OrderedDict())
    tree.fold(f)

    graph = [(verb,) + (nouns) for ((verb, nouns), _) in f.cache.items()]
    edges = [edge for edge in graph if len(edge)>1]
    nodes = [node for (node, *_) in graph if not _]
    return nodes, edges


if __name__=='__main__':
    import doctest
    doctest.testmod()


    tree = (':',
            ((',', (('x', ()),
                    ('y', ()))),
             ('z', ())))
    assert Tree(tree) == tree

    sugar_tree = (':',
                  [(',', ['x', 'y']),
                   'z'])
    assert Tree(sugar_tree) == Tree(tree)

    t = Tree(tree)


    preorder = t.preorder()
    assert preorder == [':', ',', 'x', 'y', 'z']

    inorder = t.inorder()
    assert inorder == ['x', ',', 'y', ':', 'z']


    _ = None
    t = Tree((_, ['a', (_, ['b', 'c']), 'd']))
    assert t.leaves() == ['a', ['b', 'c'], 'd']


    @multimethod(str)
    def f(x): return x.strip()
    @multimethod(int)
    def f(x): return x+1

    t = Tree((' + ', [0, 1]))
    assert t.map(f) == Tree(('+', [1, 2]))


    @multimethod(int, tuple)
    def f(op, words):
        return op
    @multimethod(str, tuple)
    def f(op, words):
        if ',' in op: return words[0]
        if '->' in op: return words[-1]

    t = Tree((',', [(',', [1, 2]), 3]))
    assert t.fold(f) == 1

    t = Tree(('->', [('->', [1, 2]), 3]))
    assert t.fold(f) == 3


    t = Tree((True, [(False, [1, 2]), 3]))
    assert t.filter(bool) == Tree((True, [3]))
    assert t.filter(lambda _: True) == t

    t = Tree((False, []))
    assert t.filter(bool) == t


    def f(op, words):
        if not words: return op
        if ',' in op: return words[0]
        if '->' in op: return words[-1]

    text = 'a -> b -> c -> d'

    line = text.split()
    ['a', ' -> ', 'b', ' , ', 'c', ' , ', 'd', ' -> ', 'e']

    cst = ['a', ' -> ', ['b', ' , ', 'c', ' , ', 'd'], ' -> ', 'e']

    ast = Tree(('->',
                [('->', ['a', (',', [(',', ['b', 'c']), 'd'])]),
                 'e']))
    assert ast.inorder() == ['a', '->', 'b', ',', 'c', ',', 'd', '->', 'e']


    # print()
    # print('Binary Tree')
    binary_tree = Tree(('->', [('->', ['a', (',', [(',', ['b', 'c']), 'd'])]), 'e']))
    nodes, edges = Graph(binary_tree, f)
    # print(ast)
    # print(nodes)
    # print(edges)
    assert nodes == ['a', 'b', 'c', 'd', 'e']
    assert edges == [(',', 'b', 'c'), (',', 'b', 'd'), ('->', 'a', 'b'), ('->', 'b', 'e')]

    # print()
    # print('n-ary Tree')
    nary_tree = Tree(('->', ['a', (',', ['b', 'c', 'd']), 'e']))
    nodes, edges = Graph(nary_tree, f)
    # print(ast)
    # print(nodes)
    # print(edges)
    assert nodes == ['a', 'b', 'c', 'd', 'e']
    assert edges == [(',', 'b', 'c', 'd'), ('->', 'a', 'b', 'e')]

    def left(op, words): return words[0] if words else op
    line = 'x , y , z : a = b'.split()
    tree = Tree(('=', [(':', [(',', [(',', ['x', 'y']), 'z']), 'a']), 'b']))
    nodes, edges = Graph(tree, left)
    assert edges == [(',', 'x', 'y'), (',', 'x', 'z'), (':', 'x', 'a'), ('=', 'x', 'b')]

    print(tree)
