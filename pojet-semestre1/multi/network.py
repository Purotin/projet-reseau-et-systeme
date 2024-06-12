import os
import uuid
# from multi.data_updater import *
from multi.properties_manager import *
from multi.pipe_handler import PipeHandler
import time


class Network:

    uuid_player = uuid.uuid4()
    grid = None
    requestsBuffer = ""
    recvMessageBuffer = ""
    messagesBuffer = ""
    ActionRequestBuffer = ""
    actionsInProgress = {"Mate":[], "EatBob":[], "EatFood":[]}
    connected = False
    ip_game = ""
        
    def selectServer():
        
        print("Select the Game you want to connect to: ")
        print("1 : Game 1")
        print("2 : Game 2")
        print("3 : Game 3")
        print("4 : Game 4")
        
        game = input()
        ip_game = None
        if game == "1":
            ip_game = "239.0.0.1"
        elif game == "2":
            ip_game = "239.0.0.2"
        elif game == "3":
            ip_game = "239.0.0.3"
        elif game == "4":
            ip_game = "239.0.0.4"
        else:
            Network.selectServer()
            
        Network.ip_game = ip_game

    #  ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ GESTION DE LA CONNEXION ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️

    def requestConnection():
        """Demande de connexion à la partie en cours

        Args:
            IP (str): Adresse IP du serveur
            port (str): Port du serveur

        Explications:
            Cette fonction permet de demander une connexion à une partie en cours. 
            Si aucune partie n'est en cours, une nouvelle partie sera créée.
        """
        process_name = "network_manager"
        try:
        # Utilise os.system pour exécuter la commande pkill
            result = os.system(f'pkill {process_name}')
            if result == 0:
                print(f"Processus '{process_name}' a été tué avec succès.")
            else:
                print(f"Erreur lors de la tentative de tuer le processus '{process_name}'. Code de retour: {result}")
        except Exception as e:
            print(f"Une erreur inattendue est survenue: {e}")
        # Lancer le network_manager
        command = f"./../src/tmp/network_manager {Network.ip_game} 9999 py_to_c c_to_py &"
        os.system(command)

        # Envoyer la requête de connexion
        strUuid = str(Network.uuid_player)
        Network.pipes = PipeHandler()
        Network.sendDirectMessage("ConnectionRequest;"+strUuid)
   
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
        if Network.game.paused == True:
            Network.game.wasPaused = False
        Network.game.paused = True
      
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
                obj["energy"] = float(data[6])
                
                if data[0] == "bob":
                    obj["mass"] = float(data[7])
                    dataDictionnary["bobs"].append(obj)
                elif data[0] == "food":
                    dataDictionnary["foods"].append(obj)

        successMessage = "ConnectionSuccess;"+str(Network.uuid_player)
        Network.sendMessage(successMessage)
        return dataDictionnary

    def disconnect():
        Network.sendDirectMessage("Disconnect;"+str(Network.uuid_player))
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



    def requestEatFood(food, bob):
        message = "EatFood" + ";" + str(food.id) + ";" + str(food.networkProperty)
        Network.actionsInProgress["EatFood"].append([food, bob])
        Network.storeActionRequest(message)

    def requestEatBob(prey, predator):
        message = "EatBob" + ";" + str(prey.id) +  ";"  + str(prey.networkProperty)
        Network.actionsInProgress["EatBob"].append([prey, predator])
        Network.storeActionRequest(message)

    def sendMateRequest(b1, b2):       # {MateRequest;bob.id;bob.currentX;bob.currentY}
        # Envoie une demande de reproduction
        message = f"MateRequest;{b2.id};{b2.currentX};{b2.currentY}"
        Network.actionsInProgress["Mate"].append([b2, b1])
        Network.storeActionRequest(message)

    def processMateRequest(message):
        """ Traite une demande de reproduction

        Args:
            message (str) : contient le header MateRequest et les informations du bob

        Explications :
            Cette fonction traite une demande de reproduction
            - Si l'entité n'existe pas chez nous, on la retire chez l'autre joueur
            - Si le bob est à une position différente de celle demandée, on le déplace
            - On envoie une réponse à la demande de reproduction
        """
        # Traite une demande de reproduction
        bob = Network.grid.findEntityById(uuid.UUID(message[0]))

        # Si l'entité n'existe pas chez nous, on la retire chez l'autre joueur
        if bob is None:
            Network.sendForceRemoveEntity(uuid.UUID(message[0]))
            message = f"MateResponse;{message[0]};{None};{None};{None};{None};{None};{None};{Network.uuid_player}"
            Network.sendDirectMessage(message)
            
        if bob.networkProperty == Network.uuid_player:
            x = float(message[1])
            y = float(message[2])

            # Si le bob est à une position différente de celle demandée, on le déplace
            if bob.currentX != x or bob.currentY != y:
                Network.grid.moveBobTo(bob, x, y, True)

            # On met à jour le bob pour changer sa propriété réseau
            Network.sendBobUpdate(bob)

            # On envoie les informations du bob
            message = f"MateResponse;{bob.id};{bob.energy};{bob.velocity};{bob.velocityBuffer};{bob.mass};{bob.perception};{bob.memorySize};{Network.uuid_player}"
            Network.sendDirectMessage(message)

    def recvGameActionsResponse():
        """
            Attendre la réponse de tout les actions du jeu et process les messages reçus
        """

        
        allMessages = Network.processBuffer()
        gameActionsHeaders = ["MateResponse", "EatBobResponse", "EatFoodResponse"]
        all_id = [id[0] for id in Network.actionsInProgress["Mate"]]
        all_id += [id[0] for id in Network.actionsInProgress["EatBob"]]
        all_id += [id[0] for id in Network.actionsInProgress["EatFood"]]
        
        for message in allMessages:
            string_message = message
            length = len(string_message)
            message = message.split(";")
            print(Network.actionsInProgress)
            
            
            if message[0] in gameActionsHeaders:
                match message[0]:
                    case "MateResponse":
                        
                        for couple in Network.actionsInProgress["Mate"]:
                            if message[8] == Network.uuid_player and couple[0].id == message[1]:
                                Network.actionsInProgress["Mate"].remove(couple)
                                Network.grid.processMateResponse(message[1:])
                        
                    case "EatBobResponse":
                        for couple in Network.actionsInProgress["EatBob"]:
                            if message[2] == Network.uuid_player and couple[0].id == message[1]:
                                Network.actionsInProgress["EatBob"].remove(couple)
                                Network.grid.processEatBobResponse(message[1:])
                            
                    case "EatFoodResponse":
                        for couple in Network.actionsInProgress["EatFood"]:
                            if message[2] == Network.uuid_player and couple[0].id == message[1]:
                                Network.actionsInProgress["EatFood"].remove(couple)
                                print("\n\n\nCON QUI PUE\n\n\n")
                                Network.grid.processEatFoodResponse(message[1:])
            
            else:
                if message[1] not in all_id:
                    Network.recvMessageBuffer += "{"+str(length)+";"+string_message+"}"
        
        if all([not Network.actionsInProgress[key] for key in Network.actionsInProgress]):
            return True
            

    # ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ GESTION DES MESSAGES ENTRANTS ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️



    def processBuffer():
        """ Traiter les messages reçus

        Explications :
            Cette fonction parcourt les messages reçus et ceux qui sont dans le recvMessageBuffer
    
        """
        buffer = Network.recvMessageBuffer
        messageList = []
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
                    try:
                        messageLength = int(message.split(";")[0])
                    except:
                        continue
                    finalMessage = message.split(";")[1:]
                    finalMessage = ";".join(finalMessage)
                    print("Received message : ", finalMessage)
                    if len(finalMessage) == messageLength:
                        messageList.append(finalMessage)
                        
        Network.recvMessageBuffer = ""
        return messageList

    def processMessages():
        # Traiter les message
        
        messageList = Network.processBuffer()
        
        for message in messageList:
        
            # Si le message est une requête propriété réseau
            message = message.split(";")
            header = message[0]

            if Network.connected == False and header == "ConnectionResponse":
                Network.processConnectionResponse(message)

            else :
                match header:

                    case "ConnectionRequest":
                        Network.processConnectionRequest(message)

                    case "MateRequest":
                        Network.processMateRequest(message[1:])
                        
                    case "EatFood":
                        Network.grid.processNetworkPropertyRequest(message)
                        
                    case "EatBob":
                        Network.grid.processNetworkPropertyRequest(message)

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
                        Network.grid.removeFoodAt(float(message[1]), float(message[2]), uuid.UUID(message[3]))
                        
                    case "RemoveBob":
                        Network.grid.removeAllBobsAt(float(message[1]), float(message[2]), uuid.UUID(message[3]))
                        
                    case "RemoveAllFoods":
                        Network.grid.removeAllEdibles(uuid.UUID(message[1]))
                    
                    case "RemoveAllBobs":
                        Network.grid.removeAllBobs(uuid.UUID(message[1]))

                    case "ConnectionSuccess":
                        if Network.game.wasPaused == True:
                            Network.game.paused = False
                    
                    case "ForceRemoveEntity":
                        Network.grid.forceRemoveEntity(uuid.UUID(message[1]))
            
    
    
    # ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ GESTION DES MESSAGES SORTANTS ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️


    
    def sendMessage(message):
        """
            Ajoute le message au buffer de messages à envoyer
            ajoute la taille du message au début du message
            message : le message à envoyer
        
        """
        length = str(len(message))
        mess = "{"+length+";"+message+"}"
        # print("Sent message : ", mess)
        Network.messagesBuffer += mess
        # Network.pipes.send(mess)
    
    def storeActionRequest(message):
        """
            Ajoute le message au buffer de messages à envoyer
            ajoute la taille du message au début du message
            message : le message à envoyer
        """
               
        length = str(len(message))
        mess = "{"+length+";"+message+"}"
        # print("Sent high priority message : ", mess)
        Network.ActionRequestBuffer += mess
        
    def sendActionRequestBuffer():
        """
            Envoie tous les messages dans le buffer de haute priorité si le buffer n'est pas vide
        """
        if Network.ActionRequestBuffer != "":
            Network.pipes.send(Network.ActionRequestBuffer)
            print("Sent high priority messages : ", Network.ActionRequestBuffer)
            Network.ActionRequestBuffer = ""
            
            
    def removeAllEntityActionBuffer():
        ids = [couple[0].id for couple in Network.actionsInProgress["Mate"]]
        ids += [couple[0].id for couple in Network.actionsInProgress["EatBob"]]
        ids += [couple[0].id for couple in Network.actionsInProgress["EatFood"]]
        for id in ids:
            Network.grid.forceRemoveEntity(id)
            Network.sendForceRemoveEntity(id)
            
        Network.actionsInProgress = {"Mate":[], "EatBob":[], "EatFood":[]}
        
        
    def sendDirectMessage(message):
        """
            Envoie un message directement
            message : le message à envoyer
        """
        length = str(len(message))
        mess = "{"+length+";"+message+"}"
        print("Sent direct message : ", mess)
        Network.pipes.send(mess)
        
    def sendMessagesBuffer():
        """
            Envoie tous les messages dans le buffer si le buffer n'est pas vide
        """
        if Network.messagesBuffer != "":    
            Network.pipes.send(Network.messagesBuffer)
            print("Sent messages : ", Network.messagesBuffer)
            Network.messagesBuffer = ""
        
    def sendNewBob(bob):        # {NewBob;X;Y;totalVelocity;mass;energy;perception;memorySize;maxAmmos;ID;Nproperty;Jproperty}

        message = "NewBob" + ";" + str(bob.id) + ";" + str(bob.currentX) + ";" + str(bob.currentY) + ";" + str(bob.mass) + ";" + str(bob.energy) + ";" + str(bob.networkProperty) + ";" + str(bob.jobProperty)
        Network.sendMessage(message)

    def sendNewFood(food):      # {NewFood;X;Y;value;ID;Nproperty;Jproperty}
        
        message = "NewFood" + ";" + str(food.id) + ";" + str(food.x) + ";" + str(food.y) + ";" + str(food.value) + ";" + str(food.networkProperty) + ";" + str(food.jobProperty)
        Network.sendMessage(message)

    def sendBobUpdate(bob):     # {Bob;id;positionX;positionY;energy}
        
        if bob.action == "move":
            # Envoie la nouvelle position du bob
            message = f"Bob;{bob.id};{bob.currentX};{bob.currentY};{bob.energy};{bob.networkProperty}"

        elif bob.action in ["eat", "parthenogenesis", "love", "idle"]:
            # Envoie la nouvelle énergie du bob
            message = f"Bob;{bob.id};None;None;{bob.energy};{bob.networkProperty}"

        elif bob.action == "eaten" or bob.action == "decay":
            # Met l'énergie du bob à 0
            message = f"Bob;{bob.id};None;None;0;{bob.networkProperty}"

        else:
            print(bob.action)

        Network.sendMessage(message)
    
    def sendFoodCreation(food): # {NewFood;positionX;positionY;value;ID;Nproperty;Jproperty}
        
        # Envoie la position et la valeur de la nourriture
        message = f"NewFood;{food.x};{food.y};{food.value};{food.id};{food.networkProperty};{food.jobProperty}"
        Network.sendMessage(message)

    def sendFoodUpdate(food):   # {Food;id;positionX;positionY;NewValue}
        # Envoie la nouvelle valeur de la nourriture
        message = f"Food;{food.x};{food.y};{food.value}{food.networkProperty}"
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
        
    def sendForceRemoveEntity(id):
        message = f"ForceRemoveEntity;{id}"
        Network.sendMessage(message)



    # ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ GESTION DE LA REPRODUCTION ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️

