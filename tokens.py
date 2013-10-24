import re

from util import *
import config


class Words(tuple):
    '''
    : (Word,)
    '''
    def __new__(cls, *words):
        return super().__new__(cls, words)
    def __str__(self):
        return ' '.join(string for (string,_,_) in self)
    def __repr__(self):
        return 'Words%r' % (tuple(self),)

class Word(tuple):
    def __new__(cls, string, token='', match=None):
        if match is None: match = {}
        return super().__new__(cls, (string, token, match))
    def __str__(self):
        string, token, match = self
        return string
    def __repr__(self):
        string, token, match = self
        if not token:
            return 'Word(%r)' % (string,)
        elif not match:
            return 'Word(%r, %r)' % (string, token)
        else:
            return 'Word(%r, %r, %r)' % (string, token, match)

def match_token(word, regexes):
    '''tries to match word to any regex, in order.

    on an inclusive match, returns the named group.
    on an exclusive match, returns None (short-circuiting).
    on neither, returns None.

    >>> yes_word = r'\w+'
    >>> not_number = {'not': r'[0-9]+'}
    >>> assert not match_token('A1', [not_number, yes_word])
    >>> assert match_token('A1', [yes_word, not_number])

    '''
    for regex in regexes:

        if isinstance(regex, dict):
            regex = regex['not']
            match = re.search(regex, word, re.UNICODE|re.VERBOSE)
            if match:
                return

        else:
            match = re.search(regex, word, re.UNICODE|re.VERBOSE)
            if match:
                return match

def match_word(word):
    '''
    >>> match_word('looks/sounds/feels')
    Word('looks/sounds/feels', 'word')

    >>> match_word('5-HT')
    Word('5-HT', 'word')

    >>> match_word('Na+')
    Word('Na+', 'word')

    >>> match_word('1..10')
    Word('1..10', 'word')

    >>> match_word('__str__')
    Word('__str__', 'word')

    >>> string, token, match = match_word('http://host.com/page.html?param=value')
    >>> string
    'http://host.com/page.html?param=value'
    >>> token
    'url'

    >>> match_word('1+2')
    Word('1+2')
    '''

    for token, regexes in config.tokens:
        match = match_token(word, regexes)
        if match:
            word = Word(word, token, match.groupdict())
            return word
    return Word(word)

@typecheck
def tokenize(line: str) -> Words:
    '''
    if no token matches the word, return just the word.
    if the word matches some token, return a Word, with the first token that matches.
    '''
    words = [match_word(word) for word in line.split()]
    return Words(*words)

@typecheck
def has_tokens(line: str) -> bool:
    '''

    >>> has_tokens(line)
    True
    >>> has_tokens('this line has no tokens')
    False

    '''
    words = tokenize(line)
    return any(token for (_,token,_) in words)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    words = tokenize('azarask.in/ 50% α-lipoic acid')

    line = str(words)
    assert line == 'azarask.in/ 50% α-lipoic acid'

    tokens = [word for (word,_,_) in words]
    assert tokens == ['azarask.in/', '50%', 'α-lipoic', 'acid']

    url, percent, word, string = words
    assert url == ('azarask.in/', 'url', {'username': None, 'port': None, 'fragment': None, 'path': '/', 'password': None, 'filename': None, 'hostname': 'azarask.in', 'query': None, 'scheme': None})
    assert percent == ('50%', 'percent', {'n': '50'})
    assert word == ('α-lipoic', 'word', {})
    assert string == ('acid', '', {})
