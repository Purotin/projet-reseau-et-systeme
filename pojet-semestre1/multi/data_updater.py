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

def processFoodCreation():
    pass

def processBobMovement():
    pass

# def processBobEatingBob():
#     pass

def processBobEatingFood():
    pass