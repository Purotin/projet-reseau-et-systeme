import os
import uuid
from pipe_handler import PipeHandler
from data_updater import *
from properties_manager import *

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

    def processMessage(message):
        # Traiter le message
        
        # Si le message est une requête propriété réseau
        header = message.split(";")[0]
        if header == "NetworkProperty":
            pass
        elif header == "ConnectionRequest":
            pass
        # À COMPLÉTER AVEC LES AUTRES EN-TÊTES

    def processConnectionRequest():
        Network.pipes.send("ConnectionResponse")

    def processConnectionResponse():
        # À COMPLÉTER
        # Envoyer tous les objets du jeu
        pass   
    
    
    
# EXEMPLES DE MESSAGE

# Requête prop réseau       : {NetworkProperty;player_id;obj_id}
# Déplacement bob           : {bob;id;position;None;}
# bob mange bob             : {bob;id;None;energy}
# bob mange nourriture      : {food;id;energy}
# Création de bob           : {newbob;id;networkProperty;jobProperty;position;......}
# Création de nourriture    : {
# Réponse prop réseau       : {NetworkProperty;player_id;obj_id;networkProperty}
# Requête de connexion      : {ConnectionRequest}
# Réponse de connexion      : {ConnectionResponse}