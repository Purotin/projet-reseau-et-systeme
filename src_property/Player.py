
class Player:

    def __init__(self, ID):
        
        self.ID = ID

    def get_property(self, entityID):
        """ returns true if player got property"""
        response = self.method_to_send_message(entityID)
        if (response == self.ID): #Supposing method_to_send_message returns the ID of entity's owner
            return True
        return False

