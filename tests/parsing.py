import unittest as T
from ..parsing import *


class ParsingTests(T.TestCase):

    def test_regex(self):
        verbs = '==> =>'.split()
        verbs = [whiten(verb,1) for verb in verbs]
        regex = get_regex(verbs)
        string = 'a b c => x y z ==> 1 2 3'
        actual = re.split(regex, string)
        self.assertEqual(actual,
                         ['a b c', ' => ', 'x y z', ' ==> ', '1 2 3'])

    def test_parse_head(self):
        arithmetic = parse_head('5   /   1 * 2  +  3 * 4')
        self.assertEqual(arithmetic,
                         ['5', '   /   ', [['1', ' * ', '2'], '  +  ', ['3', ' * ', '4']]])

        chaining = parse_head('x -> y -> z')
        self.assertEqual(chaining,
                         ['x', ' -> ', 'y', ' -> ', 'z'])

        ternary_operator = parse_head('x < y where z')
        self.assertEqual(ternary_operator,
                         ['x', ' < ', 'y where z'])

if __name__=='__main__':
    T.main()
