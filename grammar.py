from collections import Hashable

from util import *
from op import Op
import config


#:: {str: [Op]}
operators = {symbol:
                 [Op(symbol, **definition) for definition in definitions]
             for (symbol, definitions) in config.operators.items()}

nulop = operators.pop('')[0]

#:: [Op]
precedence = []
for _ in config.precedence:
    if isinstance(_, Hashable):
        precedence.extend(operators[_])
for _ in complement(operators, config.precedence):
    precedence.extend(operators[_])


if __name__=='__main__':
    import doctest
    doctest.testmod()
    pp(precedence)
    print()
