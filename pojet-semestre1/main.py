import sys
from backend.Game import Game
from backend.Grid import Grid
from backend.Bob import Bob
from backend.Edible import *

if __name__ == "__main__":

    if len(sys.argv) > 1:
        grid = sys.argv[1]
    else:
        grid = Grid(10, 1, 0)

    game = Game(grid, screenWidth=1080, screenHeight=750, dayLimit=0, noInterface=False)

    print("Shortcuts: \n")
    print("Press 'escape' to display the pause menu")
    print("Press 'p' to pause/unpause the game")
    print("Press 'r' to toggle rendering")
    print("Press 'h' to toggle the height")
    print("Press 't' to toggle textures")
    print("Press 's' to toggle the overlay")
    print("Press 'o' to display charts about the current population")
    print("Scroll to zoom in/out")
    print("Click and drag to move the camera")
    print("")


    game.run()