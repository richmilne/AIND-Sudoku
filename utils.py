import os
import sys
import string

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

    if 1:
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
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Input: A grid in string form.
    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))
