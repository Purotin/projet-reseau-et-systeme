import os
import uuid
from pipe_handler import PipeHandler
from data_updater import *
from properties_manager import *
from backend.Grid import Grid

class Network:
    uuid_player = uuid.uuid4()
    pipes = PipeHandler()

    def requestConnection(IP, port):
        command = f"./tmp/network_manager {IP} {port} py_to_c c_to_py &"
        os.system(command)
        Network.pipes.send("ConnectionRequest")

    def processBuffer():
        buffer = Network.pipes.recv()

        start_index = None
        for i in range(len(buffer)):
        # Si le buffer contient un début de message
            if buffer[i] == "{":
                start_index = i
            elif buffer[i] == "}":
                if start_index is not None:
                    message = buffer[start_index+1:i]
                    start_index = None
                    Network.processMessage(message)

    def processMessage(self, message):
        # Traiter le message
        
        # Si le message est une requête propriété réseau
        header = message.split(";")[0]

        match header:
            case "ConnectionRequest":
                self.processConnectionRequest()

            case "ConnectionResponse":
                self.processConnectionResponse()

            case "NetworkPropertyRequest":
                self.processNetworkPropertyRequest()

            case "NetworkPropertyResponse":
                self.processNetworkPropertyResponse()

            case "Bob":
                self.processBob(message)

            case "Food":
                self.processFood()

            case "NewBob":
                self.processNewBob()

            case "NewFood":
                self.processNewFood()


                
        
        # À COMPLÉTER AVEC LES AUTRES EN-TÊTES

    def processConnectionRequest():
        Network.pipes.send("ConnectionResponse")

    def processConnectionResponse():
        # À COMPLÉTER
        # Envoyer tous les objets du jeu
        pass   
    
    def processNetworkPropertyRequest():
        pass

    def processNetworkPropertyResponse():
        pass

    def processBob(message):
        if Grid.updateBob(message[1:]) is None:
            #Le bob n'a pas été trouvé, on fait quoi ?
            pass

    def processFood(message):
        if Grid.updateFood(message[1:]) is None:
            #La nourriture n'a pas été trouvée, on fait quoi ?
            pass

    def processNewBob(message):
        Grid.addBobFromMessage(message[1:])
        pass

    def processNewFood(message):
        Grid.addFoodFromMessage(message[1:])
        pass

    
    
    
# EXEMPLES DE MESSAGE

# Requête prop réseau       : {NetworkProperty;player_id;obj_id}
# Déplacement bob           : {bob;id;last_X;last_Y;positionX;positionY;None;}
# bob mange bob ou food     : {bob;id;positionX;positionY;None;energy}
# nourriture eaten          : {food;id;positionX;positionY;NewValue}
# Création de bob           : {newbob;positionX;positionY;totalVelocity;mass;energy;perception;memorySize;maxAmmos;ID;Nproperty;Jproperty}
# Création de nourriture    : {newfood;positionX;positionY;value;ID;Nproperty;Jproperty}
# Réponse prop réseau       : {NetworkProperty;player_id;obj_id;networkProperty}
# Requête de connexion      : {ConnectionRequest}
# Réponse de connexion      : {ConnectionResponse}