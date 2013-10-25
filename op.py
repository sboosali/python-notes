'''

>>> Unop('+').format('ACh')
'+ ACh'

>>> Binop('-').format(1,2)
'1 - 2'

>>> Ternop('<', 'where').format('x','y','z')
'x < y where z'

>>> Narop('.').format('a','b','c','d')
'a . b . c . d'

'''
import re

from util import *
import config


def is_unop(operator):
    return re.match(r'(?P<op>\S+) _', operator)

def is_binop(operator):
    '''
    >>> assert is_binop('->')
    >>> assert is_binop(['=>', '==>'])
    '''
    if isinstance(operator, str):
        return len(operator.split())==1
    if isinstance(operator, list):
        return True

def is_narop(operator):
    '''
    >>> assert is_narop(['.', '.'])
    '''
    if isinstance(operator, list):
        return len(operator)==2 and operator[0]==operator[1]

def is_ternop(operator):
    '''
    >>> assert is_ternop('< where')
    '''
    if isinstance(operator, str):
        return len(operator.split())==2


class Op(tuple):
    def __new__(cls, operator):
        '''
        groups operators by precedence:
        the longer operators must come before the shorter ones,
        for regexes like "( ==> | => )" to work right.

        #TODO parse string and return subclass's object
        # >>> Op('')
        # Nulop()
        # >>> Op('+ _')
        # Unop('+')
        # >>> Op('_ -> _')
        # Binop('->')
        # >>> Op('_ .')
        # Narop('.')
        # >>> Op('_ < _ where _')
        # Ternop('<', 'where')

        '''

        if not operator:
            return Nulop()

        elif is_narop(operator):
            operator, _ = operator
            return Narop(operator)

        elif is_binop(operator):
            if isinstance(operator, str):
                return Binop(operator)
            if isinstance(operator, list):
                return Binop(*operator)

        elif is_unop(operator):
            operator, = operator.split()
            return Unop(operator)

        elif is_ternop(operator):
            l, r = operator.split()
            return Ternop(l,r)

        else:
            msg = '{} does not match any Op'
            raise PatternExhausted(msg.format(operator))

    def format(self, *operands):
        operands = tuple(escape(str(_)) for _ in operands)
        operators = escape(str(self)).replace('_', '%s')
        return operators % operands

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

    def __new__(cls):
        return tuple.__new__(cls)

    def __str__(self):
        return ''

    def __repr__(self):
        return 'Nulop()'


class Unop(Op):
    '''a unary operator.
    '''
    def __new__(cls, symbol):
        return tuple.__new__(cls, (symbol,))

    def __str__(self):
        return '%s _' % self

    def __repr__(self):
        return 'Unop(%r)' % self


class Binop(Op):
    '''a binary operator. each symbol shares the same precedence.

    if at the start of a phrase, a Binop acts as a unary operator.
    e.g. "piracetam -> + ACh" may be parsed as "['piracetam', '->', ['+', 'ACh']]" which may be interpreted as "piracetam causes more acetylcholine" (i.e. unary "+" may mean "more" while binary "+" means "plus")
    '''

    def __new__(cls, *symbols):
        symbols = sorted(symbols, key=len, reverse=True)
        self = tuple.__new__(cls, symbols)
        self.min_spaces = min(config.min_spaces[_] for _ in self)
        return self

    def __str__(self):
        return '_ %s _' % (' _ '.join(self))

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
        self = tuple.__new__(cls, (l, r))
        self.min_spaces = config.min_spaces[self.symbol]
        return self

    def __str__(self):
        return '_ %s _ %s _' % self

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


class Narop(Op):
    '''an n-ary operator. like binary, is chainable. unlike binary, it is not left-associated, so the 2+ operands are all passed to the verb.
    '''
    def __new__(cls, symbol):
        self = tuple.__new__(cls, (symbol,))
        self.min_spaces = config.min_spaces[self.symbol]
        return self

    def __str__(self):
        return '_ %s' % self

    def __repr__(self):
        op, = self
        return 'Narop(%r)' % op

    def format(self, *operands):
        operands = map(str, operands)
        operator, = self
        operator = ' %s ' % operator
        return operator.join(operands)

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


if __name__=='__main__':
    import doctest
    doctest.testmod()
