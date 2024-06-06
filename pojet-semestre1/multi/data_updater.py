from network import Network
from backend import Bob, Game

def processConnectionRequest():
    Network.pipes.send("ConnectionResponse")

def processConnectionResponse():
    # À COMPLÉTER
    # Envoyer tous les objets du jeu
    allObjects = {} # A récupérer tous les objets du jeu
    Network.pipes.send(allObjects)

def processBobMessage(message, prop):
    
    match prop:
        case 'energy':
            #Process le message pour le traiter et mettre à jour et ensuite répondre si nécessaire
            Network.pipes.send()
        case 'position':
            #Process le message pour le traiter et mettre à jour et ensuite répondre si nécessaire
            Network.pipes.send()


def processBobEatingFood(message):
    # bob mange nourriture      : {food;id;energy}
    
    message_parts = message.split(";")
    food_dict = {
        "type": message_parts[0],
        "id": message_parts[1],
        "energy": message_parts[2]
    }
    #Mettre à jour le résultat reçu dans le jeu

def processNetworkProperty(message):
    message_parts = message.split(";")
    player_id = message_parts[1]
    obj_id = message_parts[2]
    
    # Retrieve network property
    network_property = Game.get_network_property(obj_id)
    
    Network.pipes.send(f"NetworkPropertyResponse;{player_id};{obj_id};{network_property}")
    pass

def processBobCreation(message):
    
    # Création de bob           : {newbob;id;networkProperty;jobProperty;position;......}

    message_parts = message.split(";")
    new_bob = {
        "id": message_parts[1],
        "job_property": message_parts[2],
        "position" : message_parts[4]
    }
    bob = Bob(id = new_bob.id, x = new_bob["position"][0], y = new_bob["position"][1])
    Game.addBob(bob)
    pass



# def processBobCreation():
#     pass

def processFoodCreation(message):
    message_parts = message.split(";")
    new_bob = {
        "id": message_parts[1],
        "network_property": message_parts[2],
        "job_property": message_parts[3],
        "position": eval(message_parts[4])
    }
    
    bob = Bob(id=new_bob["id"], x=new_bob["position"][0], y=new_bob["position"][1])
    Game.add_bob(bob)
    Network.pipes.send(f"BobCreated;{bob.id};{bob.network_property};{bob.job_property};{bob.position}")
    pass

def processBobMovement(message):
    message_parts = message.split(";")
    bob_id = message_parts[1]
    new_position = eval(message_parts[2])
    
    bob = Game.get_bob_by_id(bob_id)
    bob.update_position(new_position)
    Network.pipes.send(f"BobMoved;{bob.id};{new_position}")
    pass

# def processBobEatingBob():
#     pass

def processBobEatingFood():
    pass