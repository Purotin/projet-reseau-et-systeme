import os
import uuid
# from multi.data_updater import *
from multi.properties_manager import *
from multi.pipe_handler import PipeHandler


class Network:

    uuid_player = uuid.uuid4()
    
    grid = None

    def __init__(self):
        print("Network initialized")
        
    def disconnect():
        Network.pipes.send("{Disconnect;"+str(Network.uuid_player)+"}")
        Network.pipes.close()

    def processBuffer():
        buffer = ""
        for i in range(10):
            buffer += Network.pipes.recv()


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
                    print(message)
                    Network.processMessage(message)

    def processMessage(message):
        # Traiter le message
        
        # Si le message est une requête propriété réseau
        message = message.split(";")
        header = message[0]

        match header:
            case "ConnectionRequest":
                Network.processConnectionRequest(message)

            case "ConnectionResponse":
                Network.processConnectionResponse(message)

            case "NetworkPropertyRequest":
                Network.processNetworkPropertyRequest(message)

            case "NetworkPropertyResponse":
                Network.processNetworkPropertyResponse(message)

            case "Bob":
                Network.grid.updateBob(message[1:])

            case "Food":
                Network.grid.updateFood(message[1:])

            case "NewBob":
                Network.grid.addBobFromMessage(message[1:])

            case "NewFood":
                Network.grid.addFoodFromMessage(message[1:])

    # FONCTION OK
    def requestConnection(IP, port):
        """Demande de connexion à la partie en cours

        Args:
            IP (str): Adresse IP du serveur
            port (str): Port du serveur

        Explications:
            Cette fonction permet de demander une connexion à une partie en cours. 
            Si aucune partie n'est en cours, une nouvelle partie sera créée.
        """
        # Lancer le network_manager
        command = f"./../src/tmp/network_manager {IP} {port} py_to_c c_to_py {Network.uuid_player}&"
        os.system(command)

        # Envoyer la requête de connexion
        strUuid = str(Network.uuid_player)
        Network.pipes = PipeHandler()
        Network.pipes.send("{ConnectionRequest;"+strUuid+"}")

    # FONCTION OK       
    def processConnectionRequest(message):
        """ Traite la requête de connexion à la partie en cours

        Args:
            message (str) : contient le header ConnectionRequest et l'UUID du joueur entrant

        Explications :
            Cette fonction envoie toutes les informations de la partie en cours au joueur entrant.
        """
        # Envoyer tous les objets du jeu
        # Message = {ConnectionResponse; message[1]; info du jeu dont j'ai la np}
        
        strUuid = str(Network.uuid_player)
        # game_info doit contenir tous les objets du jeu
        game_info = Network.grid.getGameInfo()
        reponse = "{ConnectionResponse;"+message[1]+";"+strUuid+";"+game_info+"}"
        print(reponse)
        Network.pipes.send(reponse)

    # FONCTION OK
    def processConnectionResponse(message):
        """ Traite la réponse à la requête de connexion

        Args : message (str) : contient le header, la taille de la grille et tous les bobs et nourritures de la partie en cours

        Return (dict) : le dictionnaire contenant la taille de la grille, la liste de tous les bobs et la liste de toutes les nourritures
        """      
        dataDictionnary = dict()

        # argList : [ConnectionResponse, liste des bobs, liste des food]
        argList = message[3].split("$")
        dataDictionnary["gridSize"] = int(argList[0])
        dataDictionnary["bobs"] = []
        dataDictionnary["foods"] = []

        for i in range(1, len(argList)):
            # data : [bob, id, jobProperty, networkProperty, x, y, energy, mass] ou [food, id, jobProperty, networkProperty, x, y, energy] 
            data = argList[i].split(",")
            if len(data) >= 7:
                obj = {}
                obj["id"] = uuid.UUID(data[1])
                obj["jobProperty"] = uuid.UUID(data[2])
                obj["networkProperty"] = uuid.UUID(data[3])
                obj["x"] = float(data[4])
                obj["y"] = float(data[5])
                obj["energy"] = int(data[6])
                
                if data[0] == "bob":
                    obj["mass"] = int(data[7])
                    dataDictionnary["bobs"].append(obj)
                elif data[0] == "food":
                    dataDictionnary["foods"].append(obj)
                
        return dataDictionnary

    def sendNetworkPropertyRequest(entityId):
        # Broadcast for Nproperty
        message = "{NetworkPropertyRequest;"+Network.uuid_player + ";" + entityId + "}"
        Network.pipes.send(message)

    def processNetworkPropertyRequest(message):
        # Do I have the Nproperty ?
             # If yes, give it
             # If not, don't answer
        
        entity = Network.grid.findEntityById(message[2])

        if entity.networkProperty == Network.uuid_player:
            response = "{NetworkPropertyResponse;"+ message[1] + ";" + message[2] + "}"
            Network.pipes.send(response)
            entity.networkProperty = message[1]

    def sendMessage(message):
        mess = "{"+message+"}"
        Network.pipes.send(mess)
        
    def waitResponseConnection():
        """
            Attendre la réponse de la connexion et retourne la réponse sinon None
        """
        buffer = Network.pipes.recv()
        message = ""
        start_index = None
        for i in range(len(buffer)):
        # Si le buffer contient un début de message
            if buffer[i] == "{":
                start_index = i
            elif buffer[i] == "}":
                if start_index is not None:
                    message = buffer[start_index+1:i].split(";")
                    start_index = None
                    # Si le message est une réponse de connexion et que la réponse est pour moi
                    if message[0] == "ConnectionResponse" and message[1] == str(Network.uuid_player):
                        return message
        return None
                        
    
# EXEMPLES DE MESSAGE

# Requête prop réseau       : {NetworkProperty;player_id;obj_id}
# Déplacement bob           : {bob;id;last_X;last_Y;positionX;positionY;None;}
# bob mange bob ou food     : {bob;id;positionX;positionY;None;energy}
# nourriture eaten          : {food;id;positionX;positionY;NewValue}

# Création de bob           : {newbob;ID;positionX;positionY;mass;energy;Nproperty;Jproperty}
# Création de nourriture    : {newfood;positionX;positionY;value;ID;Nproperty;Jproperty}
# Réponse prop réseau       : {NetworkProperty;player_id;obj_id;networkProperty}
# Requête de connexion      : {ConnectionRequest}
# Réponse de connexion      : {ConnectionResponse;receiverJobProperty;senderJobProperty;gridSize;..........}