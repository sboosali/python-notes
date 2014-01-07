'''
'''

class Line(str):
    def __new__(cls, line: str = '', file: str = '', lineno: int = 0):
        self = super().__new__(cls, line)
        self.line = line
        self.file = file
        self.lineno = lineno
        return self

    def __repr__(self):
        string = super().__str__()
        if not self.file:
            return 'Line(%r, lineno=%r)' % (string, self.lineno)
        else:
            return 'Line(%r, file=%r, lineno=%r)' % (string, self.file, self.lineno)

    def __getattribute__(self, attr):
        '''transparently return a Line for any str method call that returns a str.

        >>> Line('Line', 'file.txt', 0).strip()
        Line('Line', file='file.txt', lineno=0)
        >>> isinstance(Line('Line').split(), list)
        True
        '''

        attr = super().__getattribute__(attr)
        if hasattr(attr, '__call__') and not str(attr).startswith('__'):

            def unstring(*args, **kwargs):
                ret = attr(*args, **kwargs)
                if isinstance(ret, str):
                    return Line(ret, lineno=self.lineno, file=self.file)
                else:
                    return ret
            return unstring

        else:
            return attr

    @property
    def json(self):
        return {'line': self.line,
                'file': self.file,
                'lineno': self.lineno}


if __name__ == "__main__":
    import doctest
    doctest.testmod()
