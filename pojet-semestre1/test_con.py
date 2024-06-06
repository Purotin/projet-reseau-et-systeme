import sys
from backend.Game import Game
from backend.Grid import Grid
from backend.Bob import Bob
from backend.Edible import *
from multi.network import Network
import time

if __name__ == "__main__":
    
    Network.requestConnection("239.0.0.1", "1234")
    
    first_connection = True
    
    start_time = time.time()
    timoutB = True
    while timoutB:
        message = Network.waitResponseConnection()
        if message != None:
            timoutB = False
            first_connection = False
        if time.time() - start_time > 5:
            timoutB = False
    
    if not first_connection:
        print("ConnectionResponse received a game is already running, you are connected to it")
        print(Network.processConnectionResponse(message))

    else:
        print("you are the first player, creating a new game")
        grid = Grid(20, 0, 0)

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
        
    Network.disconnect()
        
    