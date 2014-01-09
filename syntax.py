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
for _ in config.operator_precedence:
    if isinstance(_, Hashable):
        precedence.extend(operators[_])
for _ in complement(operators, config.operator_precedence):
    precedence.extend(operators[_])

#:: {str: str}
symbol = {operator.means: operator for operator in precedence}
# maps verbs (e.g. 'causes') back to symbols (e.g. '->')
# verbs should be unique to operators


if __name__=='__main__':
    import doctest
    doctest.testmod()
    pp(meanings)
    print()
