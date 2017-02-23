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
        puzzle = '1 2 3 4 3 4 . 234 . 3 . . . 1 . .'.split()

        check = self.parse_grid(input)
        self.assertEqual(puzzle, check)

    def test_wildcard_subs(self):
        self.utils_init(2)

        input = r"""
        1 2 3 4
        3 4 _ 432
        _ 3 ___
         1 _ _"""
        check = ['1 2 3 4', '3 4 1234 234',
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


class TestOnlyChoice(unittest.TestCase, AttachUtils):

    grid = '23 234 .. 34 13 .. .. 123 . ....'

    check = ['  23  234 1234 1234 ',
             '  34    1 1234 1234 ',
             '1234 1234  123 1234',
             '1234 1234 1234 1234',]
    check = [c.split() for c in check]
    check_diag = [c[:] for c in check]
    check_diag[-1][-1] = '4'

    def test_only_choice(self):
        self.utils_init(2, diagonal=False)

        values = self.grid_values(self.grid)
        values = self.only_choice(values)
        separator, width, output = self.values_grid(values)

        self.assertEqual(output, self.check)

    def test_only_choice_diagonal(self):
        self.utils_init(2, diagonal=True)

        values = self.grid_values(self.grid)
        values = self.only_choice(values)
        separator, width, output = self.values_grid(values)

        self.assertEqual(output, self.check_diag)

    def test_only_choice_hexa(self):
        side = 4
        dim = side * side
        self.utils_init(side, diagonal=False)

        grid = '.'*(dim**2)
        values = self.grid_values(grid)
        _, _, puzzle = self.values_grid(values)
        symbols = puzzle[0][0]
        cut, last = symbols[:-1], symbols[-1]
        puzzle[0]  = ([cut] * (dim-1)) + [symbols]

        grid = ' '.join(sum(puzzle, []))

        values = self.only_choice(self.grid_values(grid))
        _, _, puzzle = self.values_grid(values)

        self.assertEqual(puzzle[0][-1], last)

class TestReduce(unittest.TestCase, AttachUtils):

    grid = '23 234 .. 34 13 .. .. 123 . ....'

    def test_reduce(self):
        self.utils_init(2, diagonal=False)

        check = ['  23 234 1234 1234 ',
                 '  34   1  234  234 ',
                 '1234 234  123 1234',
                 '1234 234 1234 1234',]
        check = [c.split() for c in check]

        values = self.grid_values(self.grid)
        values = self.reduce(values)
        separator, width, output = self.values_grid(values)

        self.assertEqual(output, check)

    def test_reduce_diagonal(self):
        self.utils_init(2, diagonal=True)

        check = ['  23 234 1234 123',
                 '  34   1  234  23',
                 '1234 234   23 123',
                 ' 123  23 123    4',]
        check = [c.split() for c in check]

        values = self.grid_values(self.grid)
        values = self.reduce(values)
        separator, width, output = self.values_grid(values)

        self.assertEqual(output, check)

    def test_reduce_puzzle(self):
        self.utils_init(2, diagonal=True)

        grid = r""" 1234 1234| 1234 1234
                    1234  1  | 1234 1234
                   ----------+----------
                    1234 1234| 1234 234
                    1234 1234| 1234  4"""

        # Note that one iteration of the reduction function does eliminate
        # some possibilities - but does not chenge the number of cells which
        # only contain one character.
        one_reduce = self.grid_values(r"""  23  234 | 1234 123
                                           234   1  | 234   23
                                          ----------+----------
                                           1234 234 |  23   23
                                           123   23 | 123   4""")
        values = self.grid_values(grid)
        values = self.reduce(values)
        self.assertEqual(values, one_reduce)

        # The full reduction function, however, will iterate through reductions
        # until it's not capable of doing any more
        full_reduce = self.grid_values(r""" 23 23| 4  1
                                            4  1 | 23 23
                                           ------+------
                                            1  4 | 23 23
                                            23 23| 1  4""")
        values = self.grid_values(grid)
        values = self.reduce_puzzle(values)
        self.assertEqual(values, full_reduce)

    def test_reductio_ad_absurdum(self):
        self.utils_init(2, diagonal=False)

        input = (r""". . |  .   .
                     . . |  .   .
                     ----+-------
                     . . |234 234
                     1 . |123 234""")

        check = ['234 1234 234 1234',
                 '234 1234 234 1234',
                 '234  234 234  234',
                 '  #  234   #  234',]
        check = [[c.strip('#') for c in row.split()] for row in check]

        values = self.reduce(self.grid_values(input))
        _, _, output = self.values_grid(values)
        self.assertEqual(output, check)

        values = self.reduce_puzzle(self.grid_values(input))
        self.assertFalse(values)


class TestSearch(unittest.TestCase, AttachUtils):

    # Test is identical to the diagonal test in solution_test; here it's just
    # formatted to be more readable and understandable!
    input = r"""2 . . |. . . |. . .
                . . . |. . 6 |2 . .
                . . 1 |. . . |. 7 .
                ------+------+------
                . . 6 |. . 8 |. . .
                3 . . |. 9 . |. . 7
                . . . |6 . . |4 . .
                ------+------+------
                . 4 . |. . . |8 . .
                . . 5 |2 . . |. . .
                . . . |. . . |. . 3"""

    def test_search(self):
        self.utils_init(3, diagonal=False)

        # Example taken from course notes/coding example.
        input = self.grid_values(self.input)

        answer = self.grid_values(r"""2 3 9 |8 7 4 |1 5 6
                                      7 5 4 |3 1 6 |2 9 8
                                      6 8 1 |9 5 2 |3 7 4
                                      ------+------+------
                                      4 7 6 |1 2 8 |5 3 9
                                      3 1 2 |4 9 5 |6 8 7
                                      5 9 8 |6 3 7 |4 1 2
                                      ------+------+------
                                      1 4 3 |7 6 9 |8 2 5
                                      9 6 5 |2 8 3 |7 4 1
                                      8 2 7 |5 4 1 |9 6 3""")

        values = self.search(input)
        self.assertEqual(answer, values)

    def test_search_diagonal(self):
        self.utils_init(3, diagonal=True)

        input = self.grid_values(self.input)

        answer = self.grid_values(r"""2 6 7 |9 4 5 |3 8 1
                                      8 5 3 |7 1 6 |2 4 9
                                      4 9 1 |8 2 3 |5 7 6
                                      ------+------+------
                                      5 7 6 |4 3 8 |1 9 2
                                      3 8 4 |1 9 2 |6 5 7
                                      1 2 9 |6 5 7 |4 3 8
                                      ------+------+------
                                      6 4 2 |3 7 9 |8 1 5
                                      9 3 5 |2 8 1 |7 6 4
                                      7 1 8 |5 6 4 |9 2 3""")
        values = self.search(input)
        self.assertEqual(answer, values)


class TestNakedSiblings(unittest.TestCase, AttachUtils):

    input = r"""134 34 |123 .
                143  . |132 .
                -------+------
                  .  . |231 .
                431 43 |  . ."""

    def test_naked_siblings(self):
        self.utils_init(2)

        check = r"""134 34 |123 1234
                    134 12 |123 1234
                    -------+---------
                      2 12 |123 1234
                    134 34 |  4 1234"""

        input = self.grid_values(self.input)
        values = self.naked_siblings(input)
        self.assertEqual(values, self.grid_values(check))

    def test_naked_twins(self):
        self.utils_init(2)

        check = r"""134 34 | 123 1234
                    134 12 | 123 1234
                   --------+----------
                   1234 12 | 123 1234
                    134 34 |1234 1234"""
        check = self.grid_values(check)

        input = self.grid_values(self.input)
        values = self.naked_siblings(input, 2)
        self.assertEqual(values, check)

        input = self.grid_values(self.input)
        values = self.naked_twins(input)
        self.assertEqual(values, check)

if __name__ == '__main__':
    unittest.main(verbosity=2)