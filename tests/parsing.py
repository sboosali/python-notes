#!/usr/bin/python3
import unittest as T

from parsing import *


class ParsingTests(T.TestCase):
    def test_parse(self):
        verbs = '==> =>'.split()
        verbs = [whiten(verb,1) for verb in verbs]
        regex = get_regex(verbs)
        string = 'a b c => x y z ==> 1 2 3'
        actual = re.split(regex, string)
        expect = ['a b c', ' => ', 'x y z', ' ==> ', '1 2 3']
        self.assertEqual(actual, expect)

if __name__=='__main__':
    T.main()
