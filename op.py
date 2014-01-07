import re

from util import *
import config


def is_unop(operator):
    return len(operator.split())==1

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
    >>> assert is_narop('.')
    '''
    return len(operator.split())==1

def is_ternop(operator):
    '''
    >>> assert is_ternop('< where')
    '''
    if isinstance(operator, str):
        return len(operator.split())==2

def munge_spacing(spacing):
    '''
    >>> munge_spacing('')
    (0, inf)
    >>> munge_spacing(1)
    (1, 1)
    >>> munge_spacing('1,')
    (1, inf)
    >>> munge_spacing(',2')
    (0, 2)
    >>> munge_spacing('1,2')
    (1, 2)
    '''
    min_spaces = 0
    max_spaces = float('+inf')

    if isinstance(spacing, int):
        return spacing, spacing

    regex = r'(?P<min>[0-9]+)?,(?P<max>[0-9]+)?$'
    spacing = re.match(regex, spacing)

    if spacing:
        spacing = spacing.groupdict()
        if spacing['min']:
            min_spaces = int(spacing['min'])
        if spacing['max']:
            max_spaces = int(spacing['max'])

        min_spaces = max(0, min_spaces)

    return min_spaces, max_spaces


class Op(tuple):
    def __new__(cls, operator, **definition):
        '''

        >>> Op('')
        Nulop()
        >>> Op('+', arity='unary')
        Unop('+')
        >>> Op('->')
        Binop('->')
        >>> Op(['=>', '==>'])
        Binop('==>', '=>')
        >>> Op('.', arity='n-ary')
        Narop('.')
        >>> Op('< where')
        Ternop('<', 'where')

        '''
        arity = definition.get('arity', None)

        if isinstance(operator, list):
            if is_binop(operator):
                self = Binop(*operator, **definition)

        elif not operator:
            self = Nulop(**definition)

        elif is_unop(operator) and arity=='unary':
            self = Unop(operator, **definition)

        elif is_narop(operator) and arity=='n-ary':
            self = Narop(operator, **definition)

        elif is_binop(operator):
            self = Binop(operator, **definition)

        elif is_ternop(operator):
            l, r = operator.split()
            self = Ternop(l,r,**definition)

        else:
            msg = '{0} does not match any Op'
            raise PatternExhausted(msg.format(operator))

        return self

    def __init__(self, *operators, **definition):
        '''transforms definition, making the config strings into object attributes.
        keep the `definition` for repacking
        '''

        definition = dict_merge(config.default_operator, definition)
        definition.pop('arity', None)

        min_spaces, max_spaces = munge_spacing(definition['spacing'])
        self.__dict__['spacing'] = Range(min_spaces, max_spaces)

        self.__dict__['reduce'] = definition['reduce']

        self.__dict__['operands'] = definition['operands']

        self.__dict__['means'] = definition['means']

        self.__dict__['definition'] = definition

    def __repr__(self):
        args = [repr(_) for _ in self]

        definition = dict_diff(config.default_operator, self.definition)
        kwargs = ['%s=%r' % (var, val) for (var, val) in sorted(definition.items())]

        construction = ', '.join(args + kwargs)

        return '%s(%s)' % (self.__class__.__name__, construction)

    def __str__(self):
        return ' '.join(_.strip() for _ in self)

    def __getitem__(self, item):
        '''
        operator[int] => tuple index
        operator[str] => dict lookup
        '''
        if isinstance(item, int):
            return tuple.__getitem__(self, item)
        else:
            return self.definition[item]

    def __copy__(self):
        '''it's a deepcopy too:
        * unpack (i.e. * and **) makes a copy
        * everything is immutable (i.e. tuple of strings/numbers)
        '''
        return self.__class__(*self, **self.definition)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @property
    def id(self):
        '''uniquely identifies an operator (wrt parsing)
        '''
        arity = self.__class__.__name__
        symbols = tuple(self)
        spaces = self.spaces
        return (arity, symbols, spaces)

    def default(self):
        '''for cleaner doctests

        >>> Op(' + ', means='plus').default()
        Binop(' + ')

        '''
        return self.__class__(*self)

    @property
    def spaces(self):
        return min(sum(1 for _ in _ if _==' ')//2 for _ in self)

    def strip(self):
        return self.__class__(*[_.strip() for _ in self], **self.definition)


class Nulop(Op):
    '''the nullary operator.
    '''

    def __new__(cls, *args, **kwargs):
        return tuple.__new__(cls)

    def format(self, *_): return ''


class Unop(Op):
    '''a unary operator.
    '''
    def __new__(cls, symbol, **definition):
        return tuple.__new__(cls, (symbol,))

    def whiten(self, n):
        op, = self
        op = op + ' '*n
        return Unop(op, **self.definition)

    def format(self, operand, *args):
        '''

        >>> Unop('+').format('x')
        '+ x'

        '''
        operand = escape(operand)
        operator, = self
        operator = escape(operator)

        return '%s %s' % (operator, operand)

    @property
    def spaces(self):
        op, = self
        return sum(1 for _ in op if _==' ')

    def regex(self):
        '''
        '''
        op, = self
        return '(%s)' % re.escape(op)


class Binop(Op):
    '''a binary operator. each symbol shares the same precedence.

    the longer operators must come before the shorter ones,
    for regexes like "( ==> | => )" to work right.

    if at the start of a phrase, a Binop acts as a unary operator.
    e.g. "piracetam -> + ACh" may be parsed as "['piracetam', '->', ['+', 'ACh']]" which may be interpreted as "piracetam causes more acetylcholine" (i.e. unary "+" may mean "more" while binary "+" means "plus")
    '''

    def __new__(cls, *symbols, **definition):
        symbols = sorted(symbols, key=len, reverse=True)
        return tuple.__new__(cls, symbols)

    def whiten(self, n):
        """decrease precedence of operator by adding `n` spaces.

        >>> assert Binop('->').whiten(1) == Binop(' -> ')
        """
        ops = [' '*n + op + ' '*n for op in self]
        return Binop(*ops, **self.definition)

    def regex(self):
        '''binary operators are chainable (e.g. 'x => y ==> z')
        can be on same line even if different.

        >>> assert Binop(' => ').regex() == r'(\ \=\>\ )'
        >>> assert Binop('==>', '=>').regex() == r'(\=\=\>|\=\>)'

        '''
        return '(%s)' % '|'.join(map(re.escape, self))

    def format(self, *operands):
        '''

        >>> Binop('->').format('w', 'x', 'y', 'z')
        'w -> x -> y -> z'

        '''
        operator, *_ = self
        operator = ' %s ' % escape(operator)
        return operator.join(operands)


class Ternop(Op):
    '''a ternary operator.'''
    def __new__(cls, l, r, **definition):
        return tuple.__new__(cls, (l, r))

    def whiten(self, n):
        """decrease precedence of operator by adding spaces.

        >>> assert Ternop('<', 'where').whiten(1) == Ternop(' < ', ' where ')

        """
        l, r = self
        l = ' '*n + l + ' '*n
        r = ' '*n + r + ' '*n
        return Ternop(l, r, **self.definition)

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

    def format(self, *operands):
        '''

        >>> Ternop('<', 'where').format('x', 'y', 'z')
        'x < y where z'

        '''
        symbols = stagger(operands, self)
        string = ' '.join(symbols)
        return string


class Narop(Op):
    '''an n-ary operator. like binary, is chainable. unlike binary, it is not left-associated, so the 2+ operands are all passed to the verb.
    '''
    def __new__(cls, symbol, **definition):
        return tuple.__new__(cls, (symbol,))

    def __init__(self, symbol, **definition):
        super().__init__(symbol, **definition)

    def whiten(self, n):
        """decrease precedence of operator by adding `n` spaces.

        >>> assert Narop('->').whiten(1) == Narop(' -> ')
        """
        op, = self
        return Narop(' '*n + op + ' '*n, **self.definition)

    def regex(self):
        '''n-ary operators are chainable (e.g. 'x -> y -> z')

        >>> assert Narop(' -> ').regex() == r'(\ \-\>\ )'

        '''
        op, = self
        return '(%s)' % re.escape(op)

    def format(self, *operands):
        '''

        >>> Narop('.').format('w', 'x', 'y', 'z')
        'w . x . y . z'

        '''
        operator, *_ = self
        operator = ' %s ' % escape(operator)
        return operator.join(operands)


if __name__=='__main__':
    import doctest
    doctest.testmod()
