import os
import re
import sys
import string

ws = '\n\r\t |+-'
re_ws = re.compile(r"""(\n|\r|\t| |\||\+|-)""")

fn_type = type(lambda x:0)

def cross(a, b):
    return [s+t for s in a for t in b]


def init(side, wildcard='.', diagonal=False, assign_fn=None):
    """
    Creates functions used to solve Sudoku puzzles of varying sizes.

    A Sudoku puzzle is a 2-D square grid. We refer to the number of rows/cols
    as the puzzle's dimension, or *dim*. The Sudoku puzzle is then made up of
    various units. Each row, and each column, is a unit. So is each of the
    sub-squares, tiled from the top left corner of the grid to the bottom
    right. The side length, or *side*, of a sub-square is the square root of
    the puzzle's dim.

    Each unit consists of a 'dim' number of cells. In some puzzle variations,
    the 2 main diagonals across the grid are also considered units.

    Input:
        - side:
            Size of the sub-square units, which determines the puzzle's
            `dim`ensions. Currently this function only accepts sides from
            2 to 5.
        - wildcard:
            The character which stands for the unknown contents of a cell in
            the string representation of a Sudoku puzzle
        - diagonal:
            Whether you'd like to include the main diagonals of the puzzle with
            the other units - leading to the further constraint that each of
            the puzzle's symbols can only appear once along each diagonal.
        - assign_fn:
            Function with signature (dictionary, key, value) used to assign
            the given value to the dictionary under the specified key. Used by
            the visualisation module.
    Output:
        A dictionary of all the function closures produced by this function.
    """

    if not (2 <= side <= 5):
        raise ValueError("Sorry, can't solve Sudoku puzzles of that size.")

    dim = side * side
    length = dim * dim

    rows = string.ascii_uppercase
    cols = '1234567890' + string.ascii_lowercase
    rows, cols = [seq[:dim] for seq in [rows, cols]]
    symbols = cols

    for c in ws + wildcard:
        assert c not in symbols

    sub_slices = []
    for i in range(side):
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
        reversed = [rows[i] for i in range(len(rows)-1,-1,-1)]
        asc_diag = [''.join(d) for d in zip(reversed, cols)]
        diagonals = [desc_diag, asc_diag]
        unitlist = unitlist + diagonals

    # units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    unit_tups = [(s, [u for u in unitlist if s in u]) for s in boxes]
    units = dict(unit_tups)

    _flatten = lambda seq: sum(seq, [])
    # peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    peer_tups = [(s, sorted(set(_flatten(units[s])) - set([s]))) for s in boxes]
    peers = dict(((s, set(peers)) for s, peers in peer_tups))

    symbols = ''.join(sorted(set(symbols)))

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
            print(name)
            for line in seq:
                print(line)

    if assign_fn is None:
        def assign_fn(values, box, value):
            values[box] = value
    else:
        assert isinstance(assign_fn, fn_type)


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
            print(''.join(disp))
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
            length = len(piece)
            if wildcard in piece and length > 1:
                new.extend([c for c in piece])
            else:
                if length > 1:
                    piece = ''.join(sorted(set(piece)))
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

    def _boxes_with_val_len(values, length):
        boxes = [(box, val) for box, val in values.items()
                 if len(val) == length]
        return boxes

    def eliminate(values):
        """
        Go through all the boxes, and whenever there is a box with a value,
        eliminate this value from the values of all its peers.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        solved = _boxes_with_val_len(values, 1)
        for box, digit in solved:
            for peer in peers[box]:
                assign_fn(values, peer, values[peer].replace(digit, ''))
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
            assign_fn(values, box, digit)
        return values

    def naked_siblings(values, num_siblings=None):
        """Generalisation of the naked twins strategy.

        If a unit contains n identical cells, with each containing n options,
        eliminate those options from all the other cells in that unit."""
        if num_siblings is not None:
            assert 2 <= num_siblings <= (dim-1)

        for unit in unitlist:
            unit_values = [(box, tuple(sorted(values[box]))) for box in unit]
            unit_values = sorted(unit_values, key = lambda v: len(v[1]))

            siblings = {}
            for box, digits in unit_values:
                num_digits = len(digits)
                if num_siblings is not None:
                    if num_digits  > num_siblings: break
                    if num_digits != num_siblings: continue
                if digits not in siblings:
                    siblings[digits] = set([])
                siblings[digits].add(box)

            for digits, boxes in siblings.items():
                if len(digits) > 1 and len(digits) == len(boxes):
                    # We've found our n identical cells!
                    digits = set(digits)
                    for box, old_value in unit_values:
                        if box in boxes: continue
                        value = ''.join(sorted(set(old_value) - digits))
                        assign_fn(values, box, ''.join(sorted(value)))

        return values

    def naked_twins(values):
        """Eliminate values using the naked twins strategy.

        'Naked twins' are two cells in a unit which both contain the same two
        values. These two values can't appear in any other cells, so remove
        them from all other cells.

        Here's an example: If two cells each contain the two options 2 and 3 -
        one of those cells must contain the 2, and the other the 3; no other
        cell in that unit can. Therefore we can eliminate those values from the
        other cells!

        Args:
            values:
                The dictionary representation of a Sudoku puzzle
                ({'box-co-ords': symbol-string, ...}

        Returns:
            the values dictionary with the naked twins eliminated from peers.
        """

        # Find all instances of naked twins
        # Eliminate the naked twins as possibilities for their peers
        return naked_siblings(values, 2)

    def reduce(values):
        """One round of each of the reduction functions."""
        values = naked_siblings(values)
        values = only_choice(values)
        values = eliminate(values)
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
        # The original definition of 'remains the same' doesn't quite work.
        # It was just a count of how many cells had been reduced to 1 char.
        # But what about reductions that reduce the possibilities in other
        # cells, such that the next iteration would reduce them? And whether
        # this happens or not also depends on the order the reductions are
        # performed; if you do only_choice, then eliminate, you might be able
        # to have another round, whereas if you do eliminate first, then
        # only_choice, this won't happen.

        # To make the order of reductions irrelevant, we'll expand the original
        # definition of 'remains the same'. If the reductions seem to have
        # stalled (no more cells reduced to one) do one more set of reductions,
        # and only exit if that results in no change.

        stalled = False
        stalled_flag = False
        while True:
            solved_before = len(_boxes_with_val_len(values, 1))
            values = reduce(values)
            if len(_boxes_with_val_len(values, 0)):
                return False
            solved_after = len(_boxes_with_val_len(values, 1))

            stalled = solved_before == solved_after
            # print 'Stalled flags:', (stalled, stalled_flag)
            # print 'Values before/after: %d/%d' % (solved_before, solved_after)
            if stalled:
                if stalled_flag:
                    break
                else:
                    stalled_flag = True
            else:
                stalled_flag = False

        return values

    def search(values):
        """Solve a Sudoku puzzle by using depth-first search and propogation."""

        # First, reduce the puzzle using the previous function
        values = reduce_puzzle(values)
        if not isinstance(values, dict):
            return

        count = [(len(vals), box, vals) for box, vals in values.items()]
        count = sorted(count)
        count = [tup for tup in count if tup[0] > 1]
        if not count:
            # Problem must already be solved
            return values

        # Choose one of the unfilled squares with the fewest possibilities
        _, box, vals = count.pop(0)
        for digit in vals:
            # Now use recursion to solve each one of the resulting sudokus,
            # and if one returns a value (not False), return that answer!
            new_values = values.copy()
            new_values[box] = digit
            answer = search(new_values)
            if isinstance(answer, dict):
                return answer

    functions = {}
    for name, obj in locals().items():
        if isinstance(obj, fn_type) and not name.startswith('_'):
            functions[name] = obj
    return functions

functions = init(3, diagonal=True)
globals().update(functions)
__all__ = list(functions.keys())