'''e.g. `context.head()`
'''
from util import *
import re
import config


_contexts = {}
@decorator
def context(f):
    '''decorated by 'context' means:

    * it's name is in the config
    * it merges a head and a body
    '''
    _contexts[f.__name__] = f
    assert f.__name__ in config.parsers
    f.__annotations__ = {'head': str,
                         'body': str,
                         'return': 'format'}
    f = typecheck(f)
    return f

def get(parser, head, body):
    '''
    >>> get('default', '', 'body')
    '%s'

    >>> get('ellipsis', '... -> ... -> ...', '')
    '%s -> %s -> %s'

    '''
    poke = _contexts[parser]
    holes = poke(head, body)
    return holes

def starts_with_op(line):
    '''
    >>> assert starts_with_op('= line')
    >>> assert not starts_with_op('line')
    '''
    tokens = line.split()
    return tokens[0] in config.operators

@context
def default(head, body):
    '''(default context)

        x
        = y
        : z

    >>> default('head', 'body')
    '%s'

    >>> default('head', '=  body')
    'head  %s'
    '''
    if starts_with_op(body):
        tokens = re.split(r'(\s+)', body)
        spaces = tokens[1] if len(tokens)>1 else ' '

        holes = {'head': head, 'spaces': spaces}
        holes = '{head}{spaces}%s'.format(**holes)

    else:
        holes = '%s'

    return holes

@context
def ellipsis(head, _):
    '''

       ... -> + ACh
       vitamin E
       choline

    >>> ellipsis('... -> ... -> ...', None)
    '%s -> %s -> %s'
    '''
    definition = config.parsers['ellipsis']
    regex = definition['regex']
    return re.sub(regex, ' %s ', head).strip()

@context
def comment(head, _):
    return '%s'


if __name__ == "__main__":
    import doctest
    doctest.testmod()
