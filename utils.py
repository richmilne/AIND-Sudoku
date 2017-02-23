import os
import re
import sys
import string

ws = '\n\r\t |+-'
re_ws = re.compile(r"""(\n|\r|\t| |\||\+|-)""")


def cross(a, b):
    return [s+t for s in a for t in b]


def init(side, wildcard='.', diagonal=False):

    if not (2 <= side <= 5):
        raise ValueError("Sorry, can't solve Sudoku puzzles of that size.")

    dim = side * side
    length = dim * dim

    rows = string.ascii_uppercase
    cols = '1234567890' + string.lowercase
    rows, cols = [seq[:dim] for seq in [rows, cols]]
    symbols = cols

    for c in ws + wildcard:
        assert c not in symbols

    sub_slices = []
    for i in xrange(side):
        base = i*side
        sub_slices.append(slice(base, base + side))

    row_blocks = [rows[s] for s in sub_slices]
    col_blocks = [cols[s] for s in sub_slices]

    boxes = cross(rows, cols)
    row_units = [cross(r, cols) for r in rows]
    col_units = [cross(rows, c) for c in cols]

    square_units = [cross(rs, cs) for rs in row_blocks
                                  for cs in col_blocks]

    unitlist = row_units + col_units + square_units

    if diagonal:
        desc_diag = [''.join(d) for d in zip(rows, cols)]
        reversed = [rows[i] for i in xrange(len(rows)-1,-1,-1)]
        asc_diag = [''.join(d) for d in zip(reversed, cols)]
        diagonals = [desc_diag, asc_diag]
        unitlist = unitlist + diagonals

    # units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    unit_tups = [(s, [u for u in unitlist if s in u]) for s in boxes]
    units = dict(unit_tups)

    flatten = lambda seq: sum(seq, [])
    # peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    peer_tups = [(s, sorted(set(flatten(units[s])) - set([s]))) for s in boxes]
    peers = dict(((s, set(peers)) for s, peers in peer_tups))

    if 0:
        val_list = [('rows', row_units),
                    ('cols', col_units),
                    ('blocks', square_units),
                    ('unit_tups', unit_tups),
                    ('peer_tups', peer_tups)]
        if diagonal:
            val_list.insert(2, ('diagonals', diagonals))
        for (name, seq) in val_list:
            print
            print name
            for line in seq:
                print line

    def values_grid(values):
        """
        Convert the dict of Sudoku values into 2-D list.

        Input: Sudoku puzzle in dictionary form
        Output:
            - The formattted separator line, to go between each row of squares.
            - The cell padding amount, based on width of longest cell.
            - A list of all the rows in the puzzle, each row being a list of
              all the cells in that row.
        """
        output = []
        width = 1 + max(len(v) for v in values.values())
        line = '+'.join(['-'*(width*side)]*side)
        for r in rows:
            output.append([values[r+c] for c in cols])
        return line, width, output

    def display(values):
        """
        Display the values as a 2-D grid.
        Input: The sudoku in dictionary form
        Output: None
        """
        add_sep = lambda idx: 0 < idx < (dim-1) and (idx % side) == (side-1)

        separator, width, padded = values_grid(values)
        for r, row in enumerate(padded):
            disp = [col.center(width) + ('|' if add_sep(c) else '')
                    for c, col in enumerate(row)]
            print ''.join(disp)
            if add_sep(r):
                print(separator)
        print

    def parse_grid(grid, wildcard=wildcard):
        """Parse the string representation of a Sudoku grid.

        The input string is split on each of the whitespace or table formatting
        chars given at the top of this module, and contents of each cell in
        the puzzle are returned in a list.
        """
        grid = re_ws.sub(' ', grid)
        puzzle = [c.strip() for c in grid.split(' ') if c.strip()]
        new = []
        for piece in puzzle:
            if wildcard in piece and len(piece) > 1:
                new.extend([c for c in piece])
            else:
                new.append(piece)
        return new

    def grid_values(grid, wildcard=wildcard):
        """
        Convert grid into a dict of {square: char} with
        '%(symbols)s' for empties (wildcard characters.)
        Input: A grid in string form.
        Output: A grid in dictionary form
                Keys: The boxes, e.g., 'A1'
                Values: The value in each box, e.g., '8'. If the box has no
                value, then the value will be '%(symbols)s'.
        """
        puzzle = parse_grid(grid, wildcard)
        if len(puzzle) != length:
            msg = 'Input grid must be a string of %d cells (%dx%d)'
            raise AssertionError(msg % (length, dim, dim))
        puzzle = [symbols if c==wildcard else c for c in puzzle]
        return dict(zip(boxes, puzzle))
    grid_values.__doc__ %= locals()

    def eliminate(values):
        """
        Go through all the boxes, and whenever there is a box with a value,
        eliminate this value from the values of all its peers.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        solved = [(s, vals) for s, vals in values.items() if len(vals) == 1]
        for box, digit in solved:
            for peer in peers[box]:
                values[peer] = values[peer].replace(digit, '')
        return values

    def only_choice(values):
        """
        Go through all the units, and whenever there is a unit with a value that
        only fits in one box, assign the value to this box.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        singles = []
        for unit in unitlist:
            all_vals = set(''.join([values[box] for box in unit]))
            for digit in all_vals:
                locations = [box for box in unit if digit in values[box]]
                if len(locations) == 1:
                    singles.append((digit, locations[0]))
        for digit, box in set(singles):
            values[box] = digit
        return values

    def reduce_puzzle(values):
        """
        Iterate eliminate() and only_choice(). If at some point, there is a box
        with no available values, return False.
        If the sudoku is solved, return the sudoku.
        If after an iteration of both functions, the sudoku remains the same,
        return the sudoku.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        solved_values = [box for box in values.keys() if len(values[box]) == 1]
        stalled = False
        while not stalled:
            solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
            values = eliminate(values)
            values = only_choice(values)
            solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
            stalled = solved_values_before == solved_values_after
            if len([box for box in values.keys() if len(values[box]) == 0]):
                return False
        return values

    return {'display': display,
            'values_grid': values_grid,
            'parse_grid': parse_grid,
            'grid_values': grid_values,
            'eliminate': eliminate,
            'only_choice': only_choice,
            'reduce_puzzle': reduce_puzzle,
    }

functions = init(3)
globals().update(functions)
__all__ = functions.keys()