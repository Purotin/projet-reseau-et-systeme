import os
import uuid
# from multi.data_updater import *
from multi.properties_manager import *
from multi.pipe_handler import PipeHandler
import time


class Network:

    uuid_player = uuid.uuid4()
    grid = None
    messageBuffer = ""

    def __init__(self):
        print("Network initialized")

    #  ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ GESTION DE LA CONNEXION ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️

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
        Network.sendMessage("ConnectionRequest;"+strUuid)
   
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
        reponse = "ConnectionResponse;"+message[1]+";"+strUuid+";"+game_info
        Network.sendMessage(reponse)
      
    def recvConnectionResponse():
        """
            Attendre la réponse de la connexion et retourne la réponse sinon None
        """
        messageList = Network.processBuffer()   
        
        for message in messageList:
            length = len(message)
            message = message.split(";")
            if message[0] == "ConnectionResponse" and message[1] == str(Network.uuid_player):
                return message
            else:
                Network.messageBuffer += "{"+str(length)+";"+message+"}"
        return None
     
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
                obj["energy"] = int(float(data[6]))
                
                if data[0] == "bob":
                    obj["mass"] = int(data[7])
                    dataDictionnary["bobs"].append(obj)
                elif data[0] == "food":
                    dataDictionnary["foods"].append(obj)
                
        return dataDictionnary

    def disconnect():
        Network.sendMessage("Disconnect;"+str(Network.uuid_player))
        Network.pipes.close()

    def timeout(timeout,function,*args):
        """
            Attendre la réponse de la connexion et retourne la réponse sinon None
            
            args : les arguments de la fonction
                timeout : le temps d'attente
                function : la fonction à exécuter
                *args : les arguments de la fonction
        """
    
        startTime = time.time()
        timeoutBool = False
        
        while(not timeoutBool):
            ret = function(*args)
            if ret is not None:
                return ret
            if time.time() - startTime > timeout:
                timeoutBool = True
        return None
    


    # ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ GESTION DES PROPRIÉTÉS RÉSEAU ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️



    def requestNetworkProperty(entityId):
        # Broadcast for Nproperty
        message = "NetworkPropertyRequest;"+Network.uuid_player + ";" + entityId
        Network.sendMessage(message)
   
    def processNetworkPropertyRequest(message):
        """ Traite la requête de propriété réseau

        Args:
            message (str) : contient le header NetworkPropertyRequest et l'UID de l'objet

        Explications :
            
        """
        
        # message[1] : player_id
        # message[2] : obj_id
    
        entity = Network.grid.findEntityById(message[2])

        if entity is None:
            response = "NetworkPropertyResponse;"+ message[1] + ";None"
            Network.sendMessage(response)

        if entity.networkProperty == Network.uuid_player:
            response = "NetworkPropertyResponse;"+ message[1] + ";" + message[2]
            Network.sendMessage(response)
            entity.networkProperty = message[1]

    def recvNetworkProperty(obj_id):
        """ Attendre la réponse de la connexion et mettre à jour la propriété réseau de l'objet

        Args:
            obj_id (str) : l'UID de l'objet
        
        Explications :
            Cette fonction est appelée par la fonction timeout pour attendre la réponse de la connexion
            - Elle parcourt les messages reçus
            - Si le message est une réponse de connexion et que la réponse est pour moi, on met à jour la propriété réseau de l'objet
            - On place les autres messages dans messageBuffer
        """     
        messageList = Network.processBuffer()
        

        # On cherche un message de type {NetworkPropertyResponse;player_id;obj_id}
        for message in messageList:
            length = len(message)
            string_message = message
            message = message.split(";")
            # Si le message est une réponse de connexion et que la réponse est pour moi
            if message[0] == "NetworkPropertyResponse" and message[1] == str(Network.uuid_player):

                # Si l'entité n'existe pas chez l'autre joueur, on retourne -1
                if message[2] == "None":
                    return -1

                # On met à jour la propriété réseau de l'objet
                entity = Network.grid.findEntityById(message[2])
                entity.networkProperty = Network.uuid_player
            
            # On ignore les messages qui concernent l'objet pour lequel on a la propriété réseau
            # ex : ignorer Déplacement bob : {bob;id;last_X;last_Y;positionX;positionY;None;}
            elif (message[1] !=str(obj_id)):
                Network.messageBuffer += "{"+str(length)+";"+string_message+"}"
                
     

    # ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ GESTION DES MESSAGES ENTRANTS ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️



    def processBuffer():
        """ Traiter les messages reçus

        Explications :
            Cette fonction parcourt les messages reçus et ceux qui sont dans le messageBuffer
    
        """
        buffer = Network.messageBuffer
        messageList = []
        for i in range(20):
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
                    messageLength = int(message.split(";")[0])
                    finalMessage = message.split(";")[1:]
                    finalMessage = ";".join(finalMessage)
                    print("Received message : ", finalMessage)
                    if len(finalMessage) == messageLength:
                        messageList.append(finalMessage)
        return messageList

    def processMessages():
        # Traiter les message
        
        messageList = Network.processBuffer()
        
        for message in messageList:
        
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
                
                case "Disconnect":
                    Network.grid.removeAllEdibles(uuid.UUID(message[1]))
                    Network.grid.removeAllBobs(uuid.UUID(message[1]))
                
                case "RemoveFood":
                    Network.grid.removeFoodAt(int(message[1]), int(message[2]), uuid.UUID(message[3]))
                    
                case "RemoveBob":
                    Network.grid.removeAllBobsAt(int(message[1]), int(message[2]), uuid.UUID(message[3]))
                    
                case "RemoveAllFoods":
                    Network.grid.removeAllEdibles(uuid.UUID(message[1]))
                
                case "RemoveAllBobs":
                    Network.grid.removeAllBobs(uuid.UUID(message[1]))
        
    
    
    # ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ GESTION DES MESSAGES SORTANTS ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️


    
    def sendMessage(message):
        """
            Envoie un message à la connexion
            ajoute la taille du message au début du message
            message : le message à envoyer
        
        """
        length = str(len(message))
        mess = "{"+length+";"+message+"}"
        print("Sent message : ", mess)
        Network.pipes.send(mess)
        
    def sendNewBob(bob):        # {NewBob;X;Y;totalVelocity;mass;energy;perception;memorySize;maxAmmos;ID;Nproperty;Jproperty}

        message = "NewBob" + ";" + str(bob.id) + ";" + str(bob.currentX) + ";" + str(bob.currentY) + ";" + str(bob.mass) + ";" + str(bob.energy) + ";" + str(bob.networkProperty) + ";" + str(bob.jobProperty)
        Network.sendMessage(message)

    def sendNewFood(food):      # {NewFood;X;Y;value;ID;Nproperty;Jproperty}
        
        message = "NewFood" + ";" + str(food.id) + ";" + str(food.x) + ";" + str(food.y) + ";" + str(food.value) + ";" + str(food.networkProperty) + ";" + str(food.jobProperty)
        Network.sendMessage(message)

    def sendBobUpdate(bob):     # {Bob;id;positionX;positionY;energy}
        
        if bob.action == "move":
            # Envoie la nouvelle position du bob
            message = f"Bob;{bob.id};{bob.currentX};{bob.currentY};{bob.energy}"

        elif bob.action in ["eat", "parthenogenesis", "love", "idle"]:
            # Envoie la nouvelle énergie du bob
            message = f"Bob;{bob.id};None;None;{bob.energy}"

        elif bob.action == "eaten":
            # Met l'énergie du bob à 0
            message = f"Bob;{bob.id};None;None;0"

        else:
            print(bob.action)

        Network.sendMessage(message)
    
    def sendFoodCreation(food): # {NewFood;positionX;positionY;value;ID;Nproperty;Jproperty}
        
        # Envoie la position et la valeur de la nourriture
        message = f"NewFood;{food.x};{food.y};{food.value};{food.id};{food.networkProperty};{food.jobProperty}"
        Network.sendMessage(message)

    def sendFoodUpdate(food):   # {Food;id;positionX;positionY;NewValue}
        
        # Envoie la nouvelle valeur de la nourriture
        message = f"Food;{food.id};None;None;{food.value}"
        Network.sendMessage(message)
        
    def sendRemoveFoodAt(x,y):   #  {RemoveFood;X;Y;ID}
        message = f"RemoveFood;{x};{y};{Network.uuid_player}"
        Network.sendMessage(message)
        
    def sendRemoveAllBobsAt(x,y):     # {RemoveBob;X;Y;ID}    
        message = f"RemoveBob;{x};{y};{Network.uuid_player}"
        Network.sendMessage(message)
        
    def sendRemoveAllFoods():    # {RemoveFood, ID}
        message = f"RemoveAllFoods;{Network.uuid_player}"
        Network.sendMessage(message)
        
    def sendRemoveAllBobs():
        message = f"RemoveAllBobs;{Network.uuid_player}"
        Network.sendMessage(message)



    # ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ GESTION DE LA REPRODUCTION ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️



    def sendMateRequest(bob):       # {MateRequest;bob.id}
        # Envoie une demande de reproduction
        message = f"MateRequest;{bob.id}"
        Network.sendMessage(message)

    def sendMateResponse(bob):      # {MateResponse;player_id;bob_id;energy;velocity;velocityBuffer;mass;perception;memorySize}

        # Envoie une réponse à une demande de reproduction
        message = f"MateResponse;{bob.id};{bob.energy};{bob.velocity};{bob.velocityBuffer};{bob.mass};{bob.perception};{bob.memorySize}"
        Network.sendMessage(message)

    def recvMateResponse(bob_id):
        # Attend une réponse à une demande de reproduction
        messageList = Network.processBuffer()

        for message in messageList:
            message = message.split(";")
            if message[0] == "MateResponse" and message[1] == str(Network.uuid_player) and message[2] == str(bob_id):
                return message
            
        # Si on n'a pas reçu de réponse, on retourne -1
        return -1


    
# EXEMPLES DE MESSAGE

# Requête prop réseau       : {NetworkProperty;player_id;obj_id}
# Déplacement bob           : {bob;id;last_X;last_Y;positionX;positionY;None;}
# bob mange bob ou food     : {bob;id;positionX;positionY;None;energy}
# nourriture eaten          : {food;id;positionX;positionY;NewValue}

# Création de bob           : {newbob;positionX;positionY;totalVelocity;mass;energy;perception;memorySize;maxAmmos;ID;Nproperty;Jproperty}
# Création de nourriture    : {newfood;positionX;positionY;value;ID;Nproperty;Jproperty}

# Réponse prop réseau       : {NetworkProperty;player_id;obj_id}
# Requête de connexion      : {ConnectionRequest}
# Réponse de connexion      : {ConnectionResponse;receiverJobProperty;senderJobProperty;gridSize;..........}