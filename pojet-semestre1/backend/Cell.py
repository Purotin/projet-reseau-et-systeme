from backend.Settings import Settings
from backend.Edible import *
from backend.Bob import *
from backend.Effect import *
from backend.Grid import *
from random import *
from multi.network import Network
import uuid

class Cell:
    def __init__(self, x, y):
        self.bobs = []
        self.edibleObject = None

        self.id = uuid.uuid4()
        self.networkProperty = Network.uuid_player

    # Compare two cells
    def __eq__(self, other):
        if self is other or other is None:
            return False
        if not isinstance(other, Cell):
            return False
        return self.x == other.x and self.y == other.y

    # Hash the cell
    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + self.coordY
        result = prime * result + self.coordX
        return result

    # Convert the cell to a string
    def __str__(self):
        return f"({self.getX()},{self.getY()})"
    

    # Cell data retrieval methods


    # Check if the cell is empty
    def isEmpty(self):
        return len(self.bobs) == 0 and self.edibleObject is None


    # Cell data manipulation methods


    # Add a Bob object to the cell
    def addBob(self, bob):
        """
        Add a Bob object to the list of bobs.

        Args:
            bob (Bob): The Bob object to be added.
        """
        self.bobs.append(bob)

    # Remove a Bob object from the cell of bobs by its ID
    def removeBob(self, bobID=None, noMessage = False):
        if bobID is None:
            self.bobs = []

        if not noMessage:
            Network.sendForceRemoveEntity(bobID)
            print("nvvuievbzeunj")

        self.bobs = list(filter(lambda x: x.id != bobID, self.bobs))

    # Add an Edible object to the cell
    def addEdible(self, edibleObject):
        """
        Add an edible object to the cell.

        Args:
            edibleObject (Edible): The edible object to be added.
        """
        # If the cell is empty, add the edible object to the cell
        if self.edibleObject is None:
            self.edibleObject = edibleObject
        # Else, add the value of the edible object to the value of the edible object in the cell
        else:
            self.edibleObject.value += edibleObject.value



    # Cell events methods
        

    # Feed all bobs in the cell
    def eat(self, b, edibleObject):
        """
        This method makes a Bob eat an edible object.

        Args:
            b (Bob): The Bob object that eats the edible object.
            edibleObject (Edible): The edible object that is eaten.
        """
        # If the edible object is a food
        if isinstance(edibleObject, Food):
            bobEnergy = b.energy
            if isinstance(edibleObject, EffectFood):
                b.effects.append(edibleObject.effect)
            # The Bob object consumes the food energy
            b.energy = min(b.energyMax, bobEnergy + edibleObject.value)
            edibleObject.value -= b.energy - bobEnergy
            if edibleObject.value <= 1e-5:
                Network.sendForceRemoveEntity(self.edibleObject.id)
                self.edibleObject = None
            # Set the action of the Bob object to "eat"
            b.action = "eat"

        # If the edible object is a sausage
        elif isinstance(edibleObject, Sausage):
            # The Bob object consumes the sausage
            b.ammos = min(b.maxAmmos, b.ammos + edibleObject.value)
            Network.sendForceRemoveEntity(self.edibleObject.id)
            self.edibleObject = None
            # Set the action of the Bob object to "eat"
            b.action = "eat"


        Network.sendFoodUpdate(edibleObject)

    # Make all bobs in the cell eat food or a prey if they are able to
    def feedCellBobs(self):
        """
        This method feeds the Bob objects in the cell. 
        It first gets the food energy available in the cell and the list of Bob objects. 
        Each Bob object then consumes the energy of another Bob object if the mass ratio is less than a certain threshold. 
        If a Bob object's energy reaches zero, it is removed from the cell. 
        After consuming the energy of another Bob object, the Bob object stops eating. 
        If there is food energy available and the Bob object's energy is less than a maximum energy threshold, 
        the Bob object consumes the food energy.
        """
        # Shuffle the list of Bob objects in the cell
        shuffle(self.bobs)

        # Make each bob that has not performed any action yet eat
        for bob in [b for b in self.bobs if b.jobProperty == Network.uuid_player]:
            if bob.action == "idle":
                
                # Get the list all other Bobs in the cell 
                otherBobs = [otherBob for otherBob in self.bobs if otherBob != bob]

                # If the mass mechanism is enabled, make the Bob eats its prey if there is one in the cell
                if Settings.enableMass:
                    for otherBob in otherBobs:
                        massRatio = otherBob.mass / bob.mass
                        otherBobEnergy = otherBob.energy

                        # If the mass ratio is less than the threshold
                        if massRatio < Settings.massRatioThreshold:
                            # Request otherBob network property
                            if otherBob.networkProperty != Network.uuid_player:
                                Network.requestNetworkProperty(otherBob.id)

                                # On supprime le bob s'il n'a pas été trouvé par le détenteur de la propriété réseau
                                networkProperty = Network.timeout(5, Network.recvNetworkProperty, otherBob.id)
                                if networkProperty == -1 or networkProperty == None:
                                    self.removeBob(otherBob.id)
                                    continue
 
                            # The Bob consumes the energy of the other Bob object
                            bob.energy = min(bob.energyMax, otherBobEnergy * .5 * (1 - massRatio))

                            # The other Bob is removed
                            Network.sendForceRemoveEntity(otherBob.id)
                            otherBob.action = "eaten"
                            # Set the actions of the two Bob objects
                            bob.action = "eat"
                            # The Bob can only eat once per tick so we break the loop
                            break  
                
                # If the Bob has not eaten yet, make it eat the edible object if there is one in the cell
                if self.edibleObject is not None and bob.action == "idle":
                    
                    # On demande la propriété réseau de l'objet comestible
                    if self.edibleObject.networkProperty != Network.uuid_player:
                        Network.requestNetworkProperty(self.edibleObject.id)

                        # On supprime l'objet comestible s'il n'a pas été trouvé par le détenteur de la propriété réseau
                        networkProperty = Network.timeout(5, Network.recvNetworkProperty, self.edibleObject.id)
                        if networkProperty == -1 or networkProperty == None:
                            self.edibleObject = None
                            continue
                    self.eat(bob, self.edibleObject)

    # Split a bob into two bobs, (reproduction by parthenogenesis)
    def split(self, b):
        """
        This method makes a Bob split into two Bobs.

        Args:
            b (Bob): The Bob object to be split.
        """
        # Create a new bob
        bornBob = b.createMonoparentalChild()

        # Add the new bob to the cell
        Network.sendNewBob(bornBob)
        self.addBob(bornBob)

        # Set the action of the parent to "parthenogenesis"
        b.action = "parthenogenesis"

        # Remove SuperMutation effects
        b.effects = [effect for effect in b.effects if not isinstance(effect, SuperMutation)]
        b.mutationFactor = 1

        # Reduce the energy of the parent
        b.incrementEnergy(-Settings.motherEnergy)

        # Send the update to the grid
        Network.sendBobUpdate(b)

    # Make two bobs reproduce (sexual reproduction)
    def mate(self, b1, b2):
        """
        This method makes two Bob mate and creates a new Bob.

        Args:
            b1 (Bob): The first Bob.
            b2 (Bob): The second Bob.
        """

        # Si l'autre bob appartient à un autre joueur
        if b2.networkProperty != Network.uuid_player:

            # On demande sa propriété réseau
            Network.requestNetworkProperty(b2.id)

            # On supprime le bob s'il n'a pas été trouvé par le détenteur de la propriété réseau
            networkProperty = Network.timeout(5,Network.recvNetworkProperty,b2.id)
            if networkProperty == -1:
                self.removeBob(b2.id)
                return
            elif networkProperty == None:
                return

            # On demande ses statistiques
            Network.sendMateRequest(b2)

            # On met à jour ses statistiques
            b2_attributes = Network.timeout(5,Network.recvMateResponse,b2.id)

            print("\n\n\n",b2_attributes,"\n\n\n")

            # On supprime le bob s'il n'a pas été trouvé par le détenteur de la propriété réseau
            if b2_attributes == -1 or b2_attributes == None:
                self.removeBob(b2.id)
                return
            elif b2_attributes == 0:
                return
            
            b2.energy = float(b2_attributes[2])
            b2.velocity = int(b2_attributes[3])
            b2.velocityBuffer = float(b2_attributes[4])
            b2.mass = float(b2_attributes[5])
            b2.perception = float(b2_attributes[6])
            b2.memorySize = float(b2_attributes[7])

        # Create a new bob
        bornBob = Bob.createBiParentalChild(b1, b2)

        # Add the new bob to the cell
        Network.sendNewBob(bornBob)
        self.addBob(bornBob)

        # Set the action of the two parents to "mate"
        b1.action = "love"
        if b2.networkProperty == Network.uuid_player:
            b2.action = "love"

        # Remove SuperMutation effects
        b1.effects = [effect for effect in b1.effects if not isinstance(effect, SuperMutation)]
        b2.effects = [effect for effect in b2.effects if not isinstance(effect, SuperMutation)]
        b1.mutationFactor = 1
        b2.mutationFactor = 1

        # Reduce the energy of the bobs
        b1.incrementEnergy(-Settings.matingEnergyConsumption)
        b2.incrementEnergy(-Settings.matingEnergyConsumption)

        # Send the update to the grid
        Network.sendBobUpdate(b1)
        Network.sendBobUpdate(b2)
        
    # Make all bobs in the cell reproduce (parthenogenesis or sexual reproduction)
    def reproduceCellBobs(self):
        """
        This method makes the Bobs in the cell reproduce.
        """
        # If both parthenogenesis and sexual reproduction are disabled, exit the method
        if not(Settings.enableParthenogenesis or Settings.enableSexualReproduction):
            return
        
        for bob in [b for b in self.bobs if b.jobProperty == Network.uuid_player]:
            # If the Bob has not performed any action yet
            if bob.action == "idle":
                # Make the Bob reproduce by parthenogenesis if it has enough energy
                if Settings.enableParthenogenesis and bob.energy >= bob.energyMax:
                    self.split(bob)
                elif Settings.enableSexualReproduction and bob.energy >= Settings.matingEnergyRequirement:
                    # Get the list of Bob objects in the cell
                    otherBobs = [otherBob for otherBob in self.bobs if otherBob != bob]

                    for _ in range(len(otherBobs)):
                        # Select a random Bob object from the list of Bob objects in the cell
                        otherBob = choice(otherBobs)

                        # If the other Bob object has enough energy to reproduce by parthenogenesis
                        if otherBob.energy >= Settings.matingEnergyRequirement:
                            # The two Bobs mate
                            self.mate(bob, otherBob)

    # Delete all dead bobs in the cell
    def cleanCellDeadBobs(self):
        """
        This method decays the Bob objects in the cell. 
        It first gets the list of Bob objects. 
        Each Bob object then loses a certain amount of energy. 
        If a Bob object's energy reaches zero, it is removed from the cell.
        """

        for bob in self.bobs:
            # If a Bob object's energy reaches zero, it is removed from the cell
            if bob.action == "decay" or bob.action == "eaten":
                if bob.jobProperty == Network.uuid_player:
                    self.removeBob(bob.id)
                else:
                    self.removeBob(bob.id, True)

