from util import *
import config
from op import Op


CHARS = '123456789' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 'abcdefghijklmnopqrstuvwxyz' + '-/._' + '#$%^'

PREPOSITIONS = 'of in to with as at for on by from'.split()
VERBS = 'is was has had want should can could will would do'.split()
CONNECTIVES = 'and or not but while'.split()
INTERROGATIVES = 'who what where when why how'.split()

#: [Op]
OPERATORS = [Op(op) for op in config.operators]
assert has_no_duplicates(OPERATORS)


if __name__=='__main__':
    import doctest
    doctest.testmod()
    pp(OPERATORS)
