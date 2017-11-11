"""
Created on Nov 2, 2017

Common server utilities, containing functions such as reading files or static variables such has
default addresses and ports.
"""

def read_games_from_file(filename):
    '''
    Function to read sudoku start state and final state from given file and return a list of lists [ID, final, start],
    with ID being game id, final being solved sudoku and start being initial board.
    The file has following format:

    For each game:
    1) First line - # and game id (ex. #E268)
    2) 9 rows containing 9 integers from 1 to 9, this is the final solution (ex. 1 2 3 ..)
    3) Empty line
    4) 9 rows containing mix of "-" and integers 1 to 9, with "-" denoting a missing value in start board.
    5) Empty line

    Ex:
    #E268
    7 8 1 5 4 2 6 9 3
    5 9 2 6 7 3 4 8 1
    4 6 3 8 9 1 5 2 7
    2 3 6 7 5 9 8 1 4
    8 4 9 1 3 6 7 5 2
    1 5 7 4 2 8 3 6 9
    6 2 4 9 8 7 1 3 5
    3 7 8 2 1 5 9 4 6
    9 1 5 3 6 4 2 7 8

    - - - - 4 - - - -
    5 - - - - 3 - 8 -
    - 6 - - - - 5 2 7
    - - - - - - - - -
    - - - - 3 6 - - -
    - - 7 - 2 8 - 6 9
    - 2 - 9 8 - - - -
    3 - - - 1 5 - 4 -
    - - - - - 4 - 7 8

    :param filename: database input filename
    :return hash table [ID, final, start] - game id, solved board, start board
    :raises IOError when errors on reading file
    '''

    games = []
    fd = open(filename, "r")
    lines = fd.readlines()
    fd.close()
    i = 0
    while i < len(lines):
        line = lines[i]
        # if start of new board in file
        if line[0] == "#":
            # read id
            ID = line[1:].strip()
            final = []
            start = []
            # read solved board
            for _ in range(9):
                i += 1
                final.append(lines[i].strip().split())
            # one line skip
            i += 1
            # read initial board
            for _ in range(9):
                i += 1
                start.append(lines[i].strip().split())
            # add to list of games
            games.append([ID, final, start])
        # skip one empty line.
        i += 1
    return games

