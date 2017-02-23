import utils
import unittest

class AttachUtils(object):
    @classmethod
    def utils_init(cls, side, wildcard='.', diagonal=False):
        functions = utils.init(side, wildcard, diagonal)
        for name, fn in functions.items():
            setattr(cls, name, staticmethod(fn))

class TestGridParsing(unittest.TestCase, AttachUtils):

    def test_grid_parsing(self):
        self.utils_init(3)

        input = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        puzzle = [c for c in input]

        check = self.parse_grid(input)
        self.assertEqual(puzzle, check)

        input = '4 8 3 | 9 2 1 | 6 5 7 9 6 7 | 3 4 5 | 8 2 1 2 5 1 | 8 7 6 | 4 9 3 ------------------+------------------+------------------ 5 345 8 | 1 3456 2 | 9 7 6 7 2 9 | 5 34569 4 | 1 13456 8 1 13459 6 | 7 3459 8 | 2 1345 5 ------------------+------------------+------------------ 3 7 2 | 6 8 9 | 5 1 4 8 1 4 | 2 5 3 | 7 6 9 6 9 5 | 4 1 7 | 3 8 2 '
        puzzle = '4 8 3 9 2 1 6 5 7 9 6 7 3 4 5 8 2 1 2 5 1 8 7 6 4 9 3 5 345 8  1 3456 2 9 7 6 7 2 9 5 34569 4 1 13456 8 1 13459 6 7 3459 8 2 1345 5 3 7 2 6 8 9 5 1 4 8 1 4 2 5 3 7 6 9 6 9 5 4 1 7 3 8 2'.split()

        check = self.parse_grid(input)
        self.assertEqual(puzzle, check)

        input = r"""
        1 2 3 4
        3 4 . 432
        . 3 ...
         1 . ."""
        puzzle = '1 2 3 4 3 4 . 432 . 3 . . . 1 . .'.split()

        check = self.parse_grid(input)
        self.assertEqual(puzzle, check)

    def test_wildcard_subs(self):
        self.utils_init(2)

        input = r"""
        1 2 3 4
        3 4 _ 432
        _ 3 ___
         1 _ _"""
        check = ['1 2 3 4', '3 4 1234 432',
                 '1234 3 1234 1234', '1234 1 1234 1234']
        check = [c.split() for c in check]

        values = self.grid_values(input, wildcard='_')
        separator, width, output = self.values_grid(values)
        self.assertEqual(check, output)
        self.assertEqual(separator, '----------+----------')

class TestElimination(unittest.TestCase, AttachUtils):

    grid = '2.............1.'


    def test_elimination(self):
        self.utils_init(2, diagonal=False)

        check = ['  2  134  34  134',
                 '134  134 234 1234',
                 '134 1234 234  234',
                 ' 34  234   1  234']
        check = [c.split() for c in check]

        values = self.grid_values(self.grid)
        values = self.eliminate(values)
        separator, width, output = self.values_grid(values)

        self.assertEqual(output, check)

    def test_elimination_diagonal(self):
        self.utils_init(2, diagonal=True)

        check = ['  2  134  34  134',
                 '134  134 234 1234',
                 '134 1234  34  234',
                 ' 34  234   1   34']
        check = [c.split() for c in check]

        values = self.grid_values(self.grid)
        values = self.eliminate(values)
        separator, width, output = self.values_grid(values)

        self.assertEqual(output, check)


if __name__ == '__main__':
    unittest.main(verbosity=2)