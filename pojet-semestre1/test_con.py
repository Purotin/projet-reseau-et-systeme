import sys
from backend.Game import Game
from backend.Grid import Grid
from backend.Bob import Bob
from backend.Edible import *
from multi.network import Network
import time

if __name__ == "__main__":
        
    Network.selectServer()
    game = Game(grid_size=50, screenWidth=1080, screenHeight=750, dayLimit=0, noInterface=False, spawnFoodNb=50)

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
        
    Network.disconnect()
        
    