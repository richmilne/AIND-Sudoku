# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

# Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?  
A: I think the question is the wrong way around! We look for naked twins to reduce the total number of possible options for the remaining values in the same unit. By reducing the number of options, we **constrain** the set of potential Sudoku grids (which we have to enumerate and evaluate) to be only those where the naked twins' digits have been removed.

This may help us immediately, in that using the naked twins strategy immediately results in a solution to the puzzle. If not, it helps us solve the problem quicker, as there are fewer grids we have to evaluate. Each of these grids would still be subject to the same naked twins constraint, and each of them will be constrained further when other reductive functions eliminate more potential values.

# Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?  
A: The diagonal constraint states that each digit can appear only once in the diagonals of a Sudoku puzzle. Similarly to what was discussed above, by reducing the potential digits that can appear in a diagonal, we reduce the number of grids that have to be enumerated and evaluated. Fewer grids allow us to search through the solution space quicker and therefore solve a puzzle (or determine it's insoluble) faster.

### Install

This project requires **Python 3**.

We recommend students install [Anaconda](https://www.continuum.io/downloads), a pre-packaged Python distribution that contains all of the necessary libraries and software for this project. 
Please try using the environment we provided in the Anaconda lesson of the Nanodegree.

##### Optional: Pygame

Optionally, you can also install pygame if you want to see your visualization. If you've followed our instructions for setting up our conda environment, you should be all set.

If not, please see how to download pygame [here](http://www.pygame.org/download.shtml).

### Code

* `solutions.py` - You'll fill this in as part of your solution.
* `solution_test.py` - Do not modify this. You can test your solution by running `python solution_test.py`.
* `PySudoku.py` - Do not modify this. This is code for visualizing your solution.
* `visualize.py` - Do not modify this. This is code for visualizing your solution.

### Visualizing

To visualize your solution, please only assign values to the values_dict using the ```assign_values``` function provided in solution.py

### Data

The data consists of a text file of diagonal sudokus for you to solve.