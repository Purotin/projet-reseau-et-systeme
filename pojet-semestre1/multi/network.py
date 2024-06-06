import os
import uuid
from multi.data_updater import *
from multi.properties_manager import *
from multi.pipe_handler import PipeHandler


class Network:
    
    #uuid_player = uuid.uuid4()
    #pipes = PipeHandler()
    
    def __init__(self):
        self.uuid_player = uuid.uuid4()
        self.grid = None
        
    def disconnect(self):
        self.pipes.send("{Disconnect;"+str(self.uuid_player)+"}")
        self.pipes.close()

    
    def processBuffer(self):
        #buffer = Network.pipes.recv()
        buffer = self.pipes.recv()

        start_index = None
        for i in range(len(buffer)):
        # Si le buffer contient un début de message
            if buffer[i] == "{":
                start_index = i
            elif buffer[i] == "}":
                if start_index is not None:
                    message = buffer[start_index+1:i]
                    start_index = None
                    #Network.processMessage(message)
                    self.processMessage(message)

    def processMessage(self, message):
        # Traiter le message
        
        # Si le message est une requête propriété réseau
        message = message.split(";")
        header = message[0]

        match header:
            case "ConnectionRequest":
                self.processConnectionRequest(message)

            case "ConnectionResponse":
                self.processConnectionResponse(message)

            case "NetworkPropertyRequest":
                self.processNetworkPropertyRequest(message)

            case "NetworkPropertyResponse":
                self.processNetworkPropertyResponse(message)

            case "Bob":
                self.processBob(message)

            case "Food":
                self.processFood(message)

            case "NewBob":
                self.processNewBob(message)

            case "NewFood":
                self.processNewFood(message)

    def requestConnection(self, IP, port):
        command = f"./multi/network_manager {IP} {port} py_to_c c_to_py {self.uuid_player}&"
        os.system(command)
        #Network.pipes.send("ConnectionRequest")
        strUuid = str(self.uuid_player)
        self.pipes = PipeHandler()
        self.pipes.send("{ConnectionRequest;"+strUuid+"}")
        

                
    def processConnectionRequest(self, message):
        # À COMPLÉTER
        # Envoyer tous les objets du jeu
        #Message = {ConnectionResponse; message[1]; info du jeu dont j'ai la np}
        game_info = self.grid.getGameInfo()
        reponse = "{ConnectionResponse;"+message[1]+";"+game_info+"}"
        self.pipes.send(reponse)

    def processConnectionResponse(self, message):
        # À COMPLÉTER
        # Récupérer tous les objets du jeu
        if message[1] != self.uuid_player:
            return
        
        game_info = message[3].split("$")
        for info in game_info:
            if info == "":
                continue
            entity = info.split("-")
            if entity[0] == "bob":
                self.grid.addBobFromMessage(entity[1:])
            elif entity[0] == "food":
                self.grid.addFoodFromMessage(entity[1:])
        pass
    
    def sendNetworkPropertyRequest(self, entityId):
        # Broadcast for Nproperty
        message = "{NetworkPropertyRequest;"+self.uuid_player + ";" + entityId + "}"
        self.pipes.send(message)

    def processNetworkPropertyResponse(self, message):
        # À COMPLÉTER
        # Mettre à jour la propriété réseau de l'objet
        if message[1] == self.uuid_player:
            return
        entity = self.grid.findEntityById(message[2])
        self.grid.addEntityToNPorperty(entity)

    def processNetworkPropertyRequest(self, message):
        # Do I have the Nproperty ?
             # If yes, give it
             # If not, don't answer
        if self.grid.checkEntityInNProperty(message[2]):
            response = "{NetworkPropertyResponse;"+ message[1] + ";" + message[2] + "}"
            self.pipes.send(response)
            self.grid.delEntityFromNProperty(message[2])

    def processBob(self, message):
        if self.grid.updateBob(message[1:]) is None:
            #Le bob n'a pas été trouvé, on fait quoi ?
            pass

    def processFood(self, message):
        if self.grid.updateFood(message[1:]) is None:
            #La nourriture n'a pas été trouvée, on fait quoi ?
            pass

    def processNewBob(self, message):
        self.grid.addBobFromMessage(message[1:])
        
    def processNewFood(self, message):
        self.grid.addFoodFromMessage(message[1:])
    
    def sendMessage(self, message):
        mess = "{"+message+"}"
        self.pipes.send(mess)
    
    
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