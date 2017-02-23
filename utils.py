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


    def display(values):
        """
        Display the values as a 2-D grid.
        Input: The sudoku in dictionary form
        Output: None
        """
        add_sep = lambda idx: 0 < idx < (dim-1) and (idx % side) == (side-1)

        width = 1 + max(len(v) for v in values.values())
        line = '+'.join(['-'*(width*side)]*side)
        for r, row in enumerate(rows):
            disp = [values[row+col].center(width)+('|' if add_sep(c) else '')
                    for c, col in enumerate(cols)]
            print(''.join(disp))
            if add_sep(r): print(line)
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
            msg = 'Input grid must be a string of length %d (%dx%d)'
            raise AssertionError(msg % (length, dim, dim))
        puzzle = [symbols if c==wildcard else c for c in puzzle]
        return dict(zip(boxes, puzzle))
    grid_values.__doc__ %= locals()

    return display, parse_grid, grid_values

display, parse_grid, grid_values = init(3)
