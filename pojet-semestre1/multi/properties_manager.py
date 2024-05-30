from multi.network import Player

def requestNetworkProperty(object):
    id = object.id
    # Envoyer une requête au pire : je suis (id_joueur), je veux la propriété réseau de (id_objet)
    # Attendre la réponse du pair
    pass
    # Si la réponse est reçue, changer la propriété réseau de l'objet (comme ci-dessous)
    # object.networkProperty = Player.uuid_player
    pass

def processNetworkPropertyRequest(message):
    pass