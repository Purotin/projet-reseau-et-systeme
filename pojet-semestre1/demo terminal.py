import sys
from backend.Game import Game
from backend.Grid import Grid
from backend.Bob import Bob
from backend.Edible import *

if __name__ == "__main__":

    if len(sys.argv) > 1:
        grid = sys.argv[1]
    else:
        grid = Grid(20, 10, 10)

    game = Game(grid, screenWidth=1080, screenHeight=750, dayLimit=0, noInterface=True)

    game.run()