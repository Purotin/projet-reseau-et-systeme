import uuid
from random import choice
from backend.Effect import *
from frontend.Sprite import *
from backend.Settings import Settings
from multi.network import Network

class Bob:

    def __init__(self, x = 0, y = 0, totalVelocity = None, mass = None, energy = None, perception = None, memorySize = None, maxAmmos = None, ID = None, Nproperty = None, Jproperty = None):
        
        # Physical properties
        self.totalVelocity = totalVelocity if not totalVelocity is None else Settings.spawnVelocity
        self.velocity, self.velocityBuffer = int(self.totalVelocity // 1), self.totalVelocity % 1
        self.mass = mass if not mass is None else Settings.spawnMass
        self.perception = perception if not perception is None else Settings.spawnPerception
        self.perceptionDict = {}
        self.foodMemory = []
        self.cellMemory = []
        self.memorySize = memorySize if not memorySize is None else Settings.spawnMemory
        self.maxAmmos = maxAmmos if not maxAmmos is None else Settings.spawnMaxAmmos
        self.ammos = 0
        self.energy = (energy * self.mass if Settings.enableMassMaxEnergy else energy) if not energy is None else Settings.spawnEnergy
        self.energyMax = Settings.energyMax * self.mass if Settings.enableMassMaxEnergy else Settings.energyMax

        # Position
        self.currentX = x
        self.currentY = y
        self.lastX = x
        self.lastY = y
        # Action performed
        self.action = "idle"
        self.effects = []
        self.mutationFactor = 1
        self.consumptionFactor = 1
        self.target = None
        # Unique id
        self.id = ID if not ID is None else uuid.uuid4()
        # Sprite
        self.sprite = BobSprite(self)
        self.generation = 0

        self.age = 0

        #network properties
        self.networkProperty = Nproperty if not Nproperty is None else Network.uuid_player
        self.jobProperty = Jproperty if not Jproperty is None else Network.uuid_player
    
    def __str__(self):
        return "B"

    def __getstate__(self):
        state = self.__dict__.copy()

        del state['sprite']
        
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.sprite = BobSprite(self)


    # Bob data retrieval methods
    # Round the velocity of the bob to the nearest integer
    def getPerceptionRange(self):
        return round(self.perception)

    # Round the velocity of the bob to the nearest integer
    def getMemorySize(self):
        return round(self.memorySize)


    # Bob data modification methods


    # Increment the energy of the bob by the given amount
    def incrementEnergy(self, energyIncrement):
        """
        This method increments the energy of the bob by the given amount.
        It sets the energy to 0 if the resulting energy is negative.
        It sets the energy to the maximum energy if the resulting energy is greater than the maximum energy.

        Args:
            energyIncrement (float): The amount of energy to be added to the bob.
        """

        if Settings.enableIsotonicDrinks and energyIncrement < 0:
            energyIncrement *= self.consumptionFactor
        self.energy = min(Settings.energyMax, max(0,self.energy + energyIncrement))

    # Add a food to the memory of the bob, forgetting the oldest one if the memory is full
    def putInFoodMemory(self, element):
        if self.foodMemory and len(self.foodMemory) >= self.memorySize:
            self.foodMemory.pop(0)
        self.foodMemory.append(element)

    # Add a cell to the memory of the bob, forgetting the oldest one if the memory is full
    def putInCellMemory(self, element):
        if self.cellMemory and len(self.cellMemory) >= 2 * self.memorySize:
            self.cellMemory.pop(0)
        self.cellMemory.append(element)

    # Sets the memory size to the new size. If the new size is smaller than the old one, the oldest memories are forgotten
    def setMemorySize(self, newSize):
        diff = newSize - self.memorySize
        # Forget the oldest memories if the new size is smaller than the old one
        if diff < 0:
            for i in range(diff):
                self.removeFromMemory(self.foodMemory[0])
        self.memorySize = newSize
        
    # Updates the effects of the bob
    def updateEffects(self):
        for effect in self.effects:
            effect.applyEffect(self)

     # Create a child from one parent       
    
    # Create a child from one parent
    def createMonoparentalChild(self):
        """
        Create a new bob with the same properties as the parent.
        Makes the bob mutate if the mutation mechanism is enabled.

        Returns:
            Bob: The new bob.
        """
        # Create the new bob with the same properties as the parent
        bornBob = Bob(
                    x = self.currentX,
                    y = self.currentY,
                    totalVelocity=self.velocity + self.velocityBuffer,
                    mass = self.mass,
                    perception = self.perception,
                    memorySize = self.memorySize,
                    energy = Settings.pBirthEnergy
        )
        # Make the bob mutate
        if Settings.enableMutation:
            bornBob.totalVelocity = max(0, bornBob.totalVelocity + choice((-Settings.velocityMutation, Settings.velocityMutation)) * self.mutationFactor)
            bornBob.velocity, bornBob.velocityBuffer = int(bornBob.totalVelocity // 1), bornBob.totalVelocity % 1
            bornBob.mass = max(Settings.minMass, bornBob.mass + choice((-Settings.massMutation, Settings.massMutation)) * self.mutationFactor)
            bornBob.perception = max(0, bornBob.perception + choice((-Settings.perceptionMutation, Settings.perceptionMutation)) * self.mutationFactor)
            bornBob.memorySize = max(0, bornBob.memorySize + choice((-Settings.memoryMutation, Settings.memoryMutation)) * self.mutationFactor)
        
        # Set the generation of the new bob
        bornBob.generation = self.generation + 1

        # Set the action of the enw bob to birth
        bornBob.action = "birth"

        # Return the new bob
        return bornBob

    # Create a child from two parents
    @staticmethod
    def createBiParentalChild(b1, b2):
        """
        Create a new bob with the average properties of the two parents.
        Makes the bob mutate if the mutation mechanism is enabled.

        Args:
            b1 (Bob): The first parent.
            b2 (Bob): The second parent.

        Returns:
            Bob: The new bob.
        """
        # Create the new bob with the average properties of the two parents
        bornBob = Bob(
                    x = b1.currentX,
                    y = b1.currentY,
                    totalVelocity = (b1.velocity + b2.velocity + b1.velocityBuffer + b2.velocityBuffer) / 2,
                    mass = max(Settings.minMass, (b1.mass + b2.mass) / 2),
                    perception = (b1.perception + b2.perception) / 2,
                    memorySize = (b1.memorySize + b2.memorySize) / 2,
                    energy = Settings.sBirthEnergy
        )
        # Make the bob mutate
        if Settings.enableMutation:
            bornBob.totalVelocity = max(0, bornBob.totalVelocity + choice((-Settings.velocityMutation, Settings.velocityMutation)) * (b1.mutationFactor + b2.mutationFactor - 1))
            bornBob.velocity, bornBob.velocityBuffer = int(bornBob.totalVelocity // 1), bornBob.totalVelocity % 1
            bornBob.mass = max(Settings.minMass, bornBob.mass + choice((-Settings.massMutation, Settings.massMutation)) * (b1.mutationFactor + b2.mutationFactor - 1))
            bornBob.perception = max(0, bornBob.perception + choice((-Settings.perceptionMutation, Settings.perceptionMutation)) * (b1.mutationFactor + b2.mutationFactor - 1))
            bornBob.memorySize = max(0, bornBob.memorySize + choice((-Settings.memoryMutation, Settings.memoryMutation)) * (b1.mutationFactor + b2.mutationFactor - 1))

        # Set the generation of the new bob
        bornBob.generation = (b1.generation + b2.generation) / 2 + 1

        # Set the action of the enw bob to birth
        bornBob.action = "birth"

        # Return the new bob
        return bornBob