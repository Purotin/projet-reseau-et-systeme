import sys
from backend.Game import Game
from backend.Grid import Grid
from backend.Bob import Bob
from backend.Edible import *
from multi.network import Network
from time import sleep

if __name__ == "__main__":

    net = Network()
    
    net.requestConnection("239.0.0.1", "1234")
    sleep(1) 
    buffer = net.pipes.recv()
    first_connection = True
    final_message = ""
    start_index = None
    for i in range(len(buffer)):
    # Si le buffer contient un début de message
        if buffer[i] == "{":
            start_index = i
        elif buffer[i] == "}":
            if start_index is not None:
                message = buffer[start_index+1:i].split(";")
                start_index = None
                if message[0] == "ConnectionResponse":
                    first_connection = False
                    final_message = message
                    break
    
    if not first_connection:
        print("ConnectionResponse received a game is already running, you are connected to it")
        #-------A COMPLETER-------#
        
    else:
        print("you are the first player, creating a new game")
        grid = Grid(20, 0, 0)

        game = Game(grid, screenWidth=1080, screenHeight=750, dayLimit=0, noInterface=False, network=net)

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
        
        net.disconnect()
        
    