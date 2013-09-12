from util import *
import config


class Op: pass

class Nulop(tuple, Op):
    syms = ['']

class Binop(list, Op):
    """a list of binary operators that share the same precedence.

    if at the start of a phrase, a Binop acts as a unary operator.
    e.g. "piracetam -> + ACh" may be parsed as "['piracetam', '->', ['+', 'ACh']]" which may be interpreted as "piracetam causes more acetylcholine" (i.e. unary "+" may mean "more" while binary "+" means "plus")


    assert isinstance(Binop(':='), Binop)
    assert isinstance(Binop(['->','<-']), Binop)
    assert Binop('==') == ['==']

    """

    def __init__(self, symbols, min_spaces=None):
        assert is_binop(symbols)

        if isinstance(symbols, str):
            self.ops = [symbols]
        if isinstance(symbols, list):
            self.ops = sorted(symbols, key=len, reverse=True)

        if min_spaces is not None:
            self.min_spaces = min_spaces
        else:
            self.min_spaces = min(config.min_spaces[op] for op in self.syms)

        super().__init__(self.ops)

    def __hash__(self):
        return hash(' '.join(self))

    @property
    def syms(self) -> list:
        """the symbol(s) of the config representation

        >>> assert Binop([' -> ', ' <- ']).syms == ['->', '<-']

        """
        return [sym.strip() for sym in self.ops]

    def whiten(self, n):
        """decrease precedence of operator by adding spaces.

        >>> assert whiten(Binop('->'), 1) == [' -> ']
        >>> assert whiten(Binop(['->', '<-']), 1) == [' -> ', ' <- ']

        """
        op = [' '*n + sym + ' '*n for sym in self.ops]
        return Binop(op, min_spaces=self.min_spaces)

class Ternop(tuple, Op):
    """a ternary operator.

    assert isinstance(Ternop('<', 'where'), Ternop)
    assert Ternop('~', 'but') == ('~', 'but')

    """
    def __new__(cls, l, r, **kwargs):
        assert is_ternop(l + ' ' + r)
        return super().__new__(cls, (l, r))

    def __init__(self, l, r, min_spaces=None):
        if min_spaces is not None:
            self.min_spaces = min_spaces
        else:
            self.min_spaces=config.min_spaces[self.syms[0]]

    @property
    def syms(self) -> list:
        """the config representation

        >>> assert Ternop(' < ', ' where ').syms == ['< where']

        """
        return [' '.join(sym.strip() for sym in self)]

    def whiten(self, n):
        """decrease precedence of operator by adding spaces.

        >>> assert Ternop('<', 'where').whiten(1) == Ternop(' < ', ' where ')

        """
        l, r = self
        l = ' '*n + l + ' '*n
        r = ' '*n + r + ' '*n
        return Ternop(l, r, min_spaces=self.min_spaces)


def is_binop(op):
    """

    >>> assert is_binop('->')
    >>> assert is_binop(['->', '<-'])

    """
    if isinstance(op, str):
        return len(op.split())==1
    if isinstance(op, list):
        return all(map(is_binop, op))

def is_ternop(op):
    return len(op.split())==2

@as_list
def munge_syntax(syntax):
    """groups operators by precedence.
    the longer operators must come before the shorter ones,
    for regexes like "( ==> | => )" to work right.
    """

    for symbols in syntax['operators']:

        if is_binop(symbols):
            yield Binop(symbols)

        elif is_ternop(symbols):
            l, r = symbols.split()
            yield Ternop(l,r)

CHARS = '123456789' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 'abcdefghijklmnopqrstuvwxyz' + '-/._' + '#$%^'

PREPOSITIONS = 'of in to with as at for on by from'.split()
VERBS = 'is was has had want should can could will would do'.split()
CONNECTIVES = 'and or not but while'.split()
INTERROGATIVES = 'who what where when why how'.split()

#: [Op]
OPERATORS = munge_syntax(config.syntax)
assert has_no_duplicates(OPERATORS)

if __name__=='__main__':
    for operator in OPERATORS: print(operator)
