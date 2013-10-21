import re
from util import *
import config


class Op(tuple):
    def __new__(cls, *xs):
        return super().__new__(cls, xs)

    @property
    def symbol(self) -> str:
        return ' '.join(_.strip() for _ in self)
    @property
    def spaces(self):
        return min(sum(1 for _ in _ if _==' ')//2 for _ in self)

    def strip(self):
        return self.__class__(*[_.strip() for _ in self])
    def regex(self): pass
    def whiten(self): pass

class Nulop(Op):
    '''the nullary operator.
    '''
    def __repr__(self):
        return 'Nulop()'

class Unop(Op):
    '''a unary operator.
    '''
    def __new__(cls, symbol):
        return super().__new__(cls, symbol)

    def __repr__(self):
        return 'Unop(%r)' % self

class Narop(Op):
    '''an n-ary operator. like binary, is chainable. unlike binary, it is not left-associated, so the 2+ operands are all passed to the verb.
    '''
    def __new__(cls, symbol):
        return super().__new__(cls, symbol)

    def __init__(self, symbol):
        self.min_spaces = config.min_spaces[self.symbol]

    def __repr__(self):
        op, = self
        return 'Narop(%r)' % op

    def whiten(self, n):
        """decrease precedence of operator by adding `n` spaces.

        >>> assert Narop('->').whiten(1) == Narop(' -> ')
        """
        op, = self
        return Narop(' '*n + op + ' '*n)

    def regex(self):
        '''n-ary operators are chainable (e.g. 'x -> y -> z')

        >>> assert Narop(' -> ').regex() == r'(\ \-\>\ )'

        '''
        op, = self
        return '(%s)' % re.escape(op)

class Binop(Op):
    '''a binary operator. each symbol shares the same precedence.

    if at the start of a phrase, a Binop acts as a unary operator.
    e.g. "piracetam -> + ACh" may be parsed as "['piracetam', '->', ['+', 'ACh']]" which may be interpreted as "piracetam causes more acetylcholine" (i.e. unary "+" may mean "more" while binary "+" means "plus")
    '''

    def __new__(cls, *symbols):
        symbols = sorted(symbols, key=len, reverse=True)
        return tuple.__new__(cls, symbols)

    def __init__(self, *symbols):
        self.min_spaces = min(config.min_spaces[_] for _ in self)

    def __repr__(self):
        if len(self)==1:
            return 'Binop(%r)' % self[0]
        else:
            return 'Binop%r' % (tuple(self),)

    def whiten(self, n):
        """decrease precedence of operator by adding `n` spaces.

        >>> assert Binop('->').whiten(1) == Binop(' -> ')
        """
        ops = [' '*n + op + ' '*n for op in self]
        return Binop(*ops)

    def regex(self):
        '''binary operators are chainable (e.g. 'x => y ==> z')
        can be on same line even if different.

        >>> assert Binop(' => ').regex() == r'(\ \=\>\ )'
        >>> assert Binop('==>', '=>').regex() == r'(\=\=\>|\=\>)'

        '''
        return '(%s)' % '|'.join(map(re.escape, self))


class Ternop(Op):
    '''a ternary operator.'''
    def __new__(cls, l, r):
        return tuple.__new__(cls, (l, r))

    def __init__(self, l, r):
        self.min_spaces = config.min_spaces[self.symbol]

    def __repr__(self):
        return 'Ternop(%r, %r)' % self

    def whiten(self, n):
        """decrease precedence of operator by adding spaces.

        >>> assert Ternop('<', 'where').whiten(1) == Ternop(' < ', ' where ')

        """
        l, r = self
        l = ' '*n + l + ' '*n
        r = ' '*n + r + ' '*n
        return Ternop(l, r)

    def regex(self):
        '''
        >>> assert Ternop(' < ', ' where ').regex() == r'((?P<A>.*)\ \<\ (?P<B>.*)\ where\ (?P<C>.*))'
        '''
        operators = map(re.escape, self)
        operands = {'A': r'(?P<A>.*)',
                    'B': r'(?P<B>.*)',
                    'C': r'(?P<C>.*)'}
        regex = r'({A}{0}{B}{1}{C})'
        regex = regex.format(*operators, **operands)
        return regex


if __name__=='__main__':
    import doctest
    doctest.testmod()
