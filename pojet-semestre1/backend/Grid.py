from backend.Settings import *
from backend.Cell import Cell
from backend.Bob import Bob
from backend.Edible import *
from backend.Effect import SpittedAt
from multi.network import Network

from random import randint, choice
from math import sqrt

class Grid:
    def __init__(self, size, bobCount, foodCount, sausageCount = 0):
        self.size = size
        self.gridDict = {} # {(x,y):Cell}
        self.bobCount = bobCount
        self.foodCount = foodCount
        if Settings.enableSpitting:
            self.sausageCount = sausageCount
        self.dayCount = 0
         
    # Check that the grid is made of cells and that the values are Bob or Food objects
    def verifyGrid(self):
        for key,value in self.gridDict.items():
            assert isinstance(key, Cell)
            assert (any(isinstance(value,i) for i in [Bob,Food]))  # je veux dire que la valeur est soit un objet Food soit un objet Bob ou les deux

    # Convert the grid to a string
    def __str__(self):
        string = ""
        for x in range(self.size):
            for y in range(self.size):
                if (x, y) in self.gridDict.keys():
                    # If the list of bobs is not empty in the cell, display as many "B" as there are bobs
                    if any(self.gridDict[(x, y)].bobs):
                        char = "\033[91m" + "B" + "\033[0m"  # Red
                    elif (isinstance(self.gridDict[(x, y)].edibleObject, Food)):
                        if isinstance(self.gridDict[(x, y)].edibleObject, EffectFood):
                            if self.gridDict[(x, y)].edibleObject.effect.name == "superMutation":
                                char = "\033[92m" + "M" + "\033[0m"
                            elif self.gridDict[(x, y)].edibleObject.effect.name == "powerCharged":
                                char = "\033[95m" + "P" + "\033[0m"
                        else:
                            char = "\033[94m" + "F" + "\033[0m"  # Blue
                    elif (isinstance(self.gridDict[(x, y)].edibleObject, Sausage)):
                        char = "\033[93m" + "S" + "\033[0m" # Yellow
                    else:
                        char = " "
                else:
                    char = " "

                string += f"│ {char} "
            string += "│\n"
            if x < self.size - 1:
                string += "├─" + "──┼─" * (self.size - 1) + "──┤\n"

        string = "╭─" + "──┬─" * (self.size - 1) + "──╮\n" + string + "╰─" + "──┴─" * (self.size - 1) + "──╯\n"
        return string
    
        # ╭ ╮ ╯ ╰ ┼ ├ ┤ ┴ ┬ ─


    # Grid data retrieval methods
    
    # Retrieve a cell at the position (x,y) in the grid
    def getCellAt(self, x, y):
        return self.gridDict.get((x, y))
    
    # Retrieve a list of all the cells in the grid
    def getAllCells(self):
        """Return a list of all cells in the grid"""
        return self.gridDict.values()

    # Retrieve a bob at the position (x,y) in the grid
    def getBobsAt(self, x, y):
        cell = self.gridDict.get((x, y))
        if cell:
            return cell.bobs
        else:
            return []

    # Retrieve a list of all the bobs in the grid
    def getAllBobs(self):
        """Return a list of all bobs in the grid"""
        return [b for cell in self.gridDict.copy().values() for b in cell.bobs]

    # Retrieve the food value at the position (x,y) in the grid
    def getFoodValueAt(self, x, y):
        cell = self.gridDict.get((x, y))
        if cell is not None and isinstance(cell.edibleObject, Food):
            return cell.edibleObject.value
        return 0

    # Retrieve a list of all the coordinates where there is food in the grid
    def getAllEdibleObjects(self):
        """Return a list of all coordinates where there is food in the grid"""
        return [cell.edibleObject for cell in self.gridDict.copy().values() if cell.edibleObject is not None]

    # Calculate the Manhattan distance between two positions
    def getManhattanDistance(self, position1, position2):
        """
        This method calculates the Manhattan distance between two positions.

        Parameters:
        position1 (tuple): The first position.
        position2 (tuple): The second position.

        Returns:
        int: The Manhattan distance between the two positions.
        """

        # Unpack the positions into coordinates
        x1, y1 = position1
        x2, y2 = position2

        # Calculate the Manhattan distance between the two positions
        distanceX = abs(x1 - x2)
        distanceY = abs(y1 - y2)

        if Settings.donut:
            # Wrap the distance around the grid if the grid is a donut
            distanceX = min(distanceX, self.size - distanceX)
            distanceY = min(distanceY, self.size - distanceY)

        distance = distanceX + distanceY

        # Return the Manhattan distance
        return distance



    # Grid data manipulation methods


    # Place a bob at the position (x,y) in the grid
    def addBob(self, b = Bob()):
        """
        This method places a Bob object at it's currrent position in the grid. 
        If the cell at that position does not yet exist, it is created. 
        Then, Bob is added to this cell and its coordinates are updated to match the cell's position.

        Parameters:
        bob (Bob): The Bob object to be placed. Defaults to a new Bob object.
        """


        # If the current cell does not exist, create a new cell at coordinates (x, y)
        if not self.getCellAt(b.currentX, b.currentY):
            self.gridDict[(b.currentX, b.currentY)] = Cell(b.currentX, b.currentY)
        
        # Add Bob to the cell
        self.gridDict[(b.currentX, b.currentY)].addBob(b)
 
    # Remove a bob at the position (x,y) in the grid
    def removeBob(self, bobID, x, y):
        """
        This method removes a Bob object from the grid.
        If the cell at that position does not exist, nothing happens.
        If the cell at that position exists, Bob is removed from this cell.
        If the cell is now empty, it is removed from the grid dictionary.

        Parameters:
        bobID (int): The id of the Bob object to be removed. Defaults to None.
        x (int): The x coordinate of the position to remove Bob from.
        y (int): The y coordinate of the position to remove Bob from.
        """

        # If the bob is not at the specified position, do nothing
        cell = self.getCellAt(x, y)
        if not cell:
            return
        
        # Else, remove it from the grid
        cell.removeBob(bobID)

        # Remove the cell from the dictionnary if it is now empty
        if cell.isEmpty():
            del self.gridDict[(x, y)]
    
    def removeAllBobsAt(self, x, y, jobProperty):
        """
        This method removes a Bob object from the grid.
        
        Parameters:
        x (int): The x coordinate of the position to remove Bob from.
        y (int): The y coordinate of the position to remove Bob from.
        jobProperty (int): The jobProperty of the Bob object to be removed.
        """
        cell = self.getCellAt(x, y)
        if not cell:
            return
        
        # Else, remove it from the grid
        cell.bobs = [b for b in cell.bobs if b.jobProperty != jobProperty]

        # Remove the cell from the dictionnary if it is now empty
        if cell.isEmpty():
            del self.gridDict[(x, y)]
    
    # Move a bob from the position to the position (x,y) in the grid
    def moveBobTo(self, b, x, y, noMessage = False):
        """
        This method moves a Bob object from its current position to a new position in the grid.
        If the cell at the new position does not yet exist, it is created.
        Then, Bob is removed from its current cell and added to the new cell.
        Finally, Bob's coordinates are updated to match the new cell's position.

        Parameters:
        bob (Bob): The Bob object to be moved.
        x (int): The x coordinate of the position to move Bob to.
        y (int): The y coordinate of the position to move Bob to.
        noMessage (bool): A boolean indicating whether to send a message to the network. Defaults to False.
        """
        # If the position is the same as the bob's current position, set its action to idle
        if (b.currentX, b.currentY) == (x, y):
            b.action = "idle"
        # Else, set its action to move
        else:
            b.action = "move"
        
        # Remove the bob from its current position
        self.removeBob(b.id, b.currentX, b.currentY)

        # Update the bob's position
        b.lastX, b.lastY = b.currentX, b.currentY
        b.currentX, b.currentY = x, y
        
        # Add the bob to its new position
        self.addBob(b)

        # Send the new position to the network
        if not noMessage and b.action == "move":
            Network.sendBobUpdate(b)

    # Add food at the position (x,y) in the grid
    def addEdible(self, edible, noMessage = False):
        """
        This method adds an Edible object to the grid.
        If the cell at that position does not yet exist, it is created.

        Parameters:
        food (Food): The Food object to be added.
        """
        # if np is None:
        #     self.addEntityToNProperty(edible)
        # If the current cell does not exist, create a new one
        if not self.getCellAt(edible.x, edible.y):
            self.gridDict[(edible.x, edible.y)] = Cell(edible.x, edible.y)
        
        # Add the edible object to the cell
        self.gridDict[(edible.x, edible.y)].addEdible(edible)
    
    # Remove food at the position (x,y) in the grid
    def removeFoodAt(self,x,y, jobProperty):
        """
        This method removes a Food object from the grid.

        Parameters:
        x (int): The x coordinate of the position to remove Food from.
        y (int): The y coordinate of the position to remove Food from.
        """
        
        # If the cell at the specified position does not exist, do nothing
        cell = self.getCellAt(x, y)
        if not cell:
            return
        
        # Remove the food from the cell
        if cell.edibleObject is not None and cell.edibleObject.jobProperty == jobProperty:
            cell.edibleObject = None


    # Tick events


    # Update the perception of a bob if it has enough energy
    def updatePerception(self, b):
        """
        This method retrieves a dictionary representing Bob's perception of his environment.
        It iterates over all keys in the grid dictionary.
        For each key, it calculates the Manhattan distance from Bob to the key.
        If the distance is within Bob's perception range and there is food at the key's location, it adds the key to the dictionary with a value of foodFactor.
        If the distance is within Bob's perception range and there is another Bob at the key's location, it calculates the mass ratio of Bob to the other Bob.
        If the mass ratio is greater than the threshold, it adds the key to the dictionary with a value of -predatorFactor.
        If the mass ratio is less than the inverse of the threshold, it adds the key to the dictionary with a value of preyFactor.
        If the mass ratio is between the threshold and the inverse of the threshold, it does not add the key to the dictionary.

        Parameters:
        b (Bob): The Bob object whose perception is being calculated.

        Returns:
        dict: A dictionary representing Bob's perception of his environment.
        """
        # Calculate the perception range of the bob
        if Settings.enableEnergyConsumption:
            perceptionRange =  min(b.perception, int(5 * b.energy))
            if b.action == "idle":
                b.incrementEnergy(- int(perceptionRange / 5))
        else:
            perceptionRange = b.perception

        # Initialize an empty dictionary
        perceptionDict = {}

        mass = b.mass
        bobX = b.currentX
        bobY = b.currentY

        # If Bob's perception is 0, return the empty dictionary
        if perceptionRange == 0:
            return

        # Initialize an empty list to store keys in range
        keysInRange = []

        # Iterate over all keys in the grid dictionary
        for key in self.gridDict.keys():
            # Unpack the key into coordinates
            keyX, keyY = key

            # Calculate the Manhattan distance from Bob to the current key
            distance = self.getManhattanDistance((bobX, bobY), (keyX, keyY))

            # If the distance is within Bob's perception range and not 0, add the key to the list
            if distance < perceptionRange and distance != 0:
                keysInRange.append(key)

        # Iterate over all keys in range
        for key in keysInRange:
            # If there is food at the current key's location, add the key to the dictionary with a value of 1
            if Settings.enableSpitting and isinstance(self.gridDict[key].edibleObject, Sausage) and b.ammos < b.maxAmmos:
                perceptionDict[key] = Settings.foodFactor
            elif isinstance(self.gridDict[key].edibleObject, Food):
                perceptionDict[key] = Settings.foodFactor

            # Iterate over all other Bobs at the current key's location
            for otherBob in self.getBobsAt(key[0], key[1]):
                # Calculate the mass ratio of Bob to the other Bob
                massRatio = mass / otherBob.mass

                # If the mass ratio is greater than the threshold, add the key to the dictionary with a value of -1 and break the loop
                if massRatio < Settings.massRatioThreshold:
                    perceptionDict[key] = -Settings.predatorFactor
                    break

                # If the mass ratio is less than the inverse of the threshold, add the key to the dictionary with a value of 1 and break the loop
                if massRatio >= 1 / Settings.massRatioThreshold:
                    perceptionDict[key] = Settings.preyFactor
                    break

        b.perceptionDict = perceptionDict
    
    # Search for a target for the bob to spit at
    def acquireSpitTarget(self, b):
        if b.ammos <= 0:
            b.target = None
            return

        # Calculate the perception range of the bob
        if Settings.enableEnergyConsumption:
            perceptionRange =  min(b.perception, int(5 * b.energy))
            b.incrementEnergy(- int(perceptionRange / 5))
        else:
            perceptionRange = b.perception

        closestPredatorDistance = perceptionRange + 1
        closestPredator = None
        closestPreyDistance = perceptionRange + 1
        closestPrey = None

        # Calculate the inverse of the mass ratio threshold
        inverseMassRatioThreshold = 1 / Settings.massRatioThreshold

        # Iterate over all other Bobs in the grid
        for otherBob in [bob for bob in self.getAllBobs() if bob.id != b.id]:
            # Calculate the Manhattan distance between the two bobs
            distance = self.getManhattanDistance((b.currentX, b.currentY), (otherBob.currentX, otherBob.currentY))

            # If the other bob is within the perception range, check if he is the closest predator or prey
            if not any(isinstance(effect, SpittedAt) for effect in otherBob.effects):
                if distance < closestPredatorDistance:
                    massRatio = b.mass / otherBob.mass
                    if massRatio < Settings.massRatioThreshold:
                        closestPredatorDistance = distance
                        closestPredator = otherBob
                    elif distance < closestPreyDistance and massRatio >= inverseMassRatioThreshold:
                        closestPreyDistance = distance
                        closestPrey = otherBob

        # If there is a closest predator, return the closest predator, else return the closest prey
        if closestPredator:
            b.target = closestPredator
        elif closestPrey:
            b.target = closestPrey
        else:
            b.target = None

    # Make a bob spit at the closest predator or prey if there is no predator in range
    def spit(self, b):
        """
        This method makes a Bob object spit at the closest predator or prey.
        If there is a predator in range, the bob spits at the predator.

        Parameters:
        b (Bob): The Bob object to spit.
        """
        # Acquire a target for the bob to spit at
        self.acquireSpitTarget(b)
        # If there is a target, spit at the target
        if b.target is not None:
            b.action = "spit"
            b.target.effects.append(SpittedAt())
            b.ammos -= 1

            # print("spit")
        else:
            return
          
    # Update the memory of a bob if it has enough energy
    def updateMemory(self, b):
        """
        This method updates the memory of a Bob object based on its perception.
        It first calculates the maximum possible memory size based on the bob's energy.
        It then updates the bob's memory based on its perception.
        If the bob's memory is larger than the maximum possible memory size, it removes the oldest food location from the bob's memory until the memory size is equal to the maximum possible memory size.
        If the bob's memory is smaller than the maximum possible memory size, it adds all the food locations in the bob's perception to the bob's memory if they are not already in it.
        If the bob's memory is equal to the maximum possible memory size, it forgets all the food locations in the bob's memory that are not in the bob's perception.
        
        Parameters:
        b (Bob): The Bob object whose memory is being updated.
        """

        if Settings.enableEnergyConsumption:
            memorySize =  min(b.memorySize, int(5 * b.energy))
            b.incrementEnergy(- int(memorySize / 5))
        else:
            memorySize = b.memorySize

        # Update the bob's memory based on its perception
        if Settings.enableMemory and Settings.enablePerception:
            
            # Forget all the food locations in the bob's memory until the memory size is equal to the maximum possible memory size
            while len(b.foodMemory) > memorySize:
                b.foodMemory.pop(0)

            # Forget all the food locations in the bob's memory that are not in the bob's perception
            for foodCoordinates in b.foodMemory:
                if foodCoordinates not in b.perceptionDict.keys():
                    distance = self.getManhattanDistance((b.currentX, b.currentY), foodCoordinates)
                    if distance < b.perception:
                        b.foodMemory.remove(foodCoordinates)
            
            # Add all the food locations in the bob's perception to the bob's memory if they are not already in it
            for foodCoordinates in b.perceptionDict.keys():
                if foodCoordinates not in b.foodMemory:
                    b.putInFoodMemory(foodCoordinates)

            # Add the foods in the bob's memory to the perception dictionary if it si not already in it
            for foodCoordinates in b.foodMemory:
                if foodCoordinates not in b.perceptionDict.keys():
                    b.perceptionDict[foodCoordinates] = Settings.foodFactor

    # Make a bob move
    def moveBob(self, b):
        """
        This method moves a Bob object based on its vision and energy. 
        If Bob's energy is sufficient, it calculates a score for each possible move, 
        chooses the move with the highest score, and moves Bob to the new position. 
        If Bob's energy is not sufficient, Bob stays in the same position. 
        The energy cost of the move is then calculated and subtracted from Bob's energy.

        Parameters:
        b (Bob): The Bob object to be moved.
        """
        velocity = b.velocity if Settings.enableVelocity else 1

        # Update the bob's velocity based on the velocity buffer
        if Settings.enableVelocity:
            b.totalVelocity += b.velocityBuffer + b.velocity
            velocity, b.totalVelocity = int(b.totalVelocity // 1), b.totalVelocity % 1
            
        if velocity == 0:
            return

        # Determine the maximum possible velocity, perception, and memory based on energy and mass
        if Settings.enableEnergyConsumption:
            energy = b.energy if Settings.enableEnergyConsumption else b.energyMax
            mass = b.mass if Settings.enableMass else 1
            # Calculate the maximum possible velocity based on the bob's energy and mass;
            velocity = min(velocity, int(sqrt(energy / mass)))
            # Exit if the bob cannot move due to insufficient energy

        # If the bob's perceptionDict and it's memory are empty, move randomly
        if not bool(b.perceptionDict):
            dx = self.size
            dy = self.size

            # While the bob coordinates + dx and + dy are out of bounds or the cell has already been visited
            while not ((0 <= b.currentX + dx < self.size and 0 <= b.currentY + dy < self.size) or (Settings.enableMemory and (b.currentX + dx, b.currentY + dy) in b.cellMemory)):
                dx = randint(-velocity, velocity)
                remaining = velocity - abs(dx)
                dy = remaining if choice([True, False]) else -remaining
                
                # If the grid is a donut, wrap the bob around the grid

                if Settings.donut:
                    dx = (b.currentX + dx) % self.size - b.currentX
                    dy = (b.currentY + dy) % self.size - b.currentY

            newX = b.currentX + dx
            newY = b.currentY + dy

        # Else, the bob's perception is not 0 and the perception mechanism is enabled
        else:

            # Find the best move based on the bob's perception
            bestMove = None
            bestScore = float('-inf')  # Initialize with negative infinity

            for dx in range(-velocity, velocity + 1):
                for dy in range(-velocity + abs(dx), velocity - abs(dx) + 1):
                    newX = b.currentX + dx
                    newY = b.currentY + dy

                    # If the grid is a donut, wrap the new coordinates around the grid
                    if Settings.donut:
                        newX %= self.size
                        newY %= self.size

                    # Check if the new coordinates are within bounds
                    if 0 <= newX < self.size and 0 <= newY < self.size:
                        # Calculate the score based on perceptionDict and distance
                        score = 0

                        # Iterate over each key in perceptionDict
                        for key, value in b.perceptionDict.items():
                            # If the grid is a donut, wrap the perception coordinates around the grid
                            distance = self.getManhattanDistance((newX, newY), key)
                            weight = 1 / (distance + 1)
                                
                            score += weight * value  # Add the weighted benefit or danger score

                        # Update bestMove and bestScore if the current move has a higher score
                        if score > bestScore:
                            bestMove = (newX, newY)
                            bestScore = score

            # Use bestMove to determine the new coordinates
            newX, newY = bestMove

        if Settings.enableEnergyConsumption:
            # Calculate the manhattan distance moved
            distance = self.getManhattanDistance((b.currentX, b.currentY), (newX, newY))
            # Calculate the energy cost of the move
            movementCost = distance**2 * mass
            # Subtract the energy cost from Bob's energy
            b.incrementEnergy(-movementCost)
        
        # Move Bob to the best position
        self.moveBobTo(b, newX, newY)
  
    # Launches all the events of the grid in a game's tick
    def newTickEvents(self):
        """
        This method updates the state of the grid. 
        It moves all Bob objects in the grid using the moveBobs method,
        feeds all Bob objects in the grid using the feedAllBobs method,
        reproduces all Bob objects that are able to reproduce using parthenogenesis or sexual reproduction,
        and deletes all dead Bob objects in the grid using the cleanDeadBobs method.
        """
        # Get a list of all bobs in the grid
        bobsList = self.getAllBobs()
        bobsList = [b for b in self.getAllBobs() if b.jobProperty == Network.uuid_player]
   
        for b in bobsList:
            # Set the bob's action to idle if it is not dying
            if b.action != "decay":
                b.action = "idle"

            b.age += 1
        
        for cell in self.getAllCells():
            if cell.bobs:
                # Make all bobs in the cell reproduce (parthenogenesis or sexual reproduction)
                cell.reproduceCellBobs()
                
                # Feed all bobs in the cell if they are able to
                if Settings.enableFeed:
                    cell.feedCellBobs()

        for b in bobsList:
            # Update the perception of the bob
            if Settings.enablePerception and b.action == "idle":
                self.updatePerception(b)
            # Make the bob spit if it is able to
            if Settings.enableSpitting and b.action == "idle":
                self.spit(b)
            # Apply the effects of the bob
            if Settings.enableEffects:
                b.updateEffects()
            # Update the memory of the bob
            if Settings.enableMemory and b.action == "idle":
                self.updateMemory(b)
            # Move the bob if it is able to
            if Settings.enableMovement and b.action == "idle":
                self.moveBob(b)


        # Delete all dead Bob objects in the grid
        self.cleanDeadBobs()
        
        for b in bobsList:
            # If the Bob is immobile, set its last position to its current position
            if b.action != "move":
                b.lastX, b.lastY = b.currentX, b.currentY
                b.displayX, b.displayY = b.currentX, b.currentY

            if b.action != "move" and not(Settings.enableParthenogenesis and b.energy >= b.energyMax):
                b.incrementEnergy(-Settings.tickMinEnergyConsumption)

            if b.energy <= 0 and b.action != "eaten":
                b.action = "decay"

        # Update the action of all foreign bobs
        foreignBobs = [b for b in self.getAllBobs() if b.jobProperty != Network.uuid_player]
        for b in foreignBobs:
            if b.action == "move":
                b.lastX, b.lastY = b.currentX, b.currentY
                b.action = "idle"



    # Day events


    # Delete all food in the grid
    def removeAllEdibles(self, jobProperty ):
        """
        This method removes all Food objects from the grid.
        It iterates over the grid dictionary and removes all Food objects from each cell.
        If a cell is now empty, it is removed from the grid dictionary.
        
        Parameters:
        jobProperty (int): The jobProperty of the Food objects to be removed.
        """
        # Store the keys to remove in a list to avoid modifying the dictionary during iteration
        keysToRemove = []
        
        # Iterate over the grid dictionary
        for key, cell in self.gridDict.items():
            if (cell.edibleObject):
                if cell.edibleObject.jobProperty == jobProperty:
                    cell.edibleObject = None
            # If the cell is empty, add its key to the list
            if cell.isEmpty():
                keysToRemove.append(key)

        # Remove all empty cells from the grid dictionary in a seeparate loop
        for key in keysToRemove:
            del self.gridDict[key]

    # Delete all bobs in the grid
    def removeAllBobs(self, jobProperty):
        """
        This method removes all Bob objects from the grid.
        It iterates over the grid dictionary and removes all Bob objects from each cell.
        If a cell is now empty, it is removed from the grid dictionary.
        
        Parameters:
        jobProperty (int): The jobProperty of the Bob objects to be removed.
        
        """
        keysToRemove = []
        for key, cell in self.gridDict.items():
            cell.bobs = [b for b in cell.bobs if b.jobProperty != jobProperty]
            if cell.isEmpty():
                keysToRemove.append(key)
        for key in keysToRemove:
            del self.gridDict[key]
        
    # Populates the grid with bobs at the start of a new day
    def spawnBobs(self):
        """
        This method populates the grid with Bob objects at the start of a new day.
        """
        for _ in range(self.bobCount):
            x = randint(0, self.size - 1)
            y = randint(0, self.size - 1)
            bob = Bob(x, y)
            if bob.jobProperty != Network.uuid_player:
                Network.sendNewBob(bob)
            self.addBob(bob)

    # Populates the grid with food at the start of a new day
    def spawnFood(self):
        """
        This method populates the grid with Food objects at the start of a new day.
        The food objetcs aer assigned a random energy value between 25 and 100.
        """
        for i in range (self.foodCount):
            x = randint(0,self.size - 1)
            y = randint(0,self.size - 1)

            if Settings.enableMutantFood and randint(1, 100) <= 2:
                self.addEdible(EffectFood(x, y, effect=SuperMutation()))
            elif Settings.enableIsotonicDrinks and randint(1, 100) <= 2:
                self.addEdible(EffectFood(x, y, energy=10, effect=PowerCharged()))
            else:
                self.addEdible(Food(x,y))
        
    # Populates the grid with sausages at the start of a new day
    def spawnSausages(self):
        """
        This method populates the grid with Sausage objects at the start of a new day.
        The sausage objetcs aer assigned a random ammos value between 25 and 100.
        """
        for i in range (self.sausageCount):
            while True:
                x = randint(0,self.size - 1)
                y = randint(0,self.size - 1)
                
                if (x, y) not in self.gridDict:
                    self.gridDict[(x, y)] = Cell(x, y)

                if self.gridDict[x,y].edibleObject is None or isinstance(self.gridDict[x,y].edibleObject, Sausage):
                    break

            self.addEdible(Sausage(x, y))

    # Delete all dead bobs
    def cleanDeadBobs(self):
        """
        This method decays all Bob objects in the grid. 
        It creates a copy of the grid dictionary and iterates over each cell. 
        If the cell contains any Bobs, it decays them using the decayCellBobs method of the cell.

        Note: A copy of the grid dictionary is used to avoid issues with changing the dictionary size during iteration.
        """
        # Iterate over each cell in the grid dictionary
        for cell in self.getAllCells():
            # If the cell contains any Bobs
            cell.cleanCellDeadBobs()
    
    # Launches all the events of the grid in a game's day
    def newDayEvents(self):
        """
        This method updates the state of the grid at the end of a day. 
        It spawns food using the spawnFood method and spawns Bob objects using the spawnBobs method.
        """
        # Don't do anything on day 0 -> initial bobs and food are already spawned
        if(self.dayCount == 0):
            self.dayCount += 1
            return

        # Remove all food from the grid
        self.removeAllEdibles(Network.uuid_player)
        Network.sendRemoveAllFoods()

        # Spawn food
        self.spawnFood()

        if Settings.enableSpitting:
            self.spawnSausages()

        # Increment the day count
        self.dayCount += 1

    # Get the oldest Bob in the grid
    def getBestBob(self):
        bestBob = None
        for bob in self.getAllBobs():
            if bestBob is None or bob.age > bestBob.age:
                bestBob = bob
            elif bob.age == bestBob.age and bob.energy > bestBob.energy:
                bestBob = bob
            elif bob.age == bestBob.age and bob.energy == bestBob.energy and bob.mass > bestBob.mass:
                bestBob = bob
            elif bob.age == bestBob.age and bob.energy == bestBob.energy and bob.mass == bestBob.mass and bob.velocity > bestBob.velocity:
                bestBob = bob
        return bestBob
    
    def updateBob(self, message):
        """
        This method updates a Bob object based on a message received from the network.
        It retrieves the Bob object from the grid based on the message's ID.
        If the Bob object is found, it updates the Bob object based on the message's data.

        Parameters:
        message (list): A list containing the message data.

        Explainations:
        The received message lookes like {Bob;bob_id;X;Y;energy}
        """

        print(message)

        # On rècupère le bob à partir de son ID
        bob = self.findEntityById(uuid.UUID(message[0]))

        if bob is not None:
            print("bob trouvé")
            # On met à jour l'énergie du bob
            bob.energy = int(float(message[3]))

            # Si le bob s'est déplacé, on met à jour sa position
            if message[1] is not None:
                self.moveBobTo(bob, int(float(message[1])), int(float(message[2])), noMessage=True)
        else:
            print("bob non trouvé")


    
    def updateFood(self, message):
        """
        This method updates a Food object based on a message received from the network.
        It retrieves the Food object from the grid based on the message's ID.
        If the Food object is found, it updates the Food object based on the message's data.

        Parameters:
        message (list): A list containing the message data.
        """
        message[1] = float(message[2])
        message[2] = float(message[2])
        message[3] = float(message[2])

        if not self.getCellAt(message[1], message[2]):
            self.gridDict[message[1], message[2]] = Cell(message[1], message[2])

        # Retrieve the Food object from the grid based on the message
        food = self.getCellAt(message[1], message[2]).edibleObject
        if food.id != message[0]:
            return None
        
        # Update the food object
        food.value = message[3]
        return 0

    def addBobFromMessage(self, message):
        """
        This method adds a Bob object to the grid based on a message received from the network.
        It creates a new Bob object based on the message's data and adds it to the grid.

        Parameters:
        message (list): A list containing the message data.
        """
        # Create a new Bob object based on the message
        newBob = Bob(ID = uuid.UUID(message[0]),x = float(message[1]), y = float(message[2]), mass = int(message[3]), energy = int(float(message[4])), Nproperty = uuid.UUID(message[5]), Jproperty = uuid.UUID(message[6]))
        self.addBob(newBob)

    def addFoodFromMessage(self, message):
        """
        This method adds a Food object to the grid based on a message received from the network.
        It creates a new Food object based on the message's data and adds it to the grid.

        Parameters:
        message (list): A list containing the message data.
        """
        # Create a new Food object based on the message
        newFood = Food(ID = uuid.UUID(message[0]), x=float(message[1]), y=float(message[2]), energy = int(message[3]), Nproperty = uuid.UUID(message[4]), Jproperty = uuid.UUID(message[5]))
        self.addEdible(newFood, True)
    
    def getGameInfo(self):
        mess = ""
        mess += f"{self.size}$"
        for b in self.getAllBobs():
                mess += f"bob,{b.id},{b.jobProperty},{b.networkProperty},{b.currentX},{b.currentY},{b.energy},{b.mass}$"
        for f in self.getAllEdibleObjects():
                mess += f"food,{f.id},{f.jobProperty},{f.networkProperty},{f.x},{f.y},{f.value}$"
        return mess
    
    def findEntityById(self, ID):
        for cell in self.gridDict.values():
            if cell.edibleObject and cell.edibleObject.id == ID:
                return cell.edibleObject
            for bob in cell.bobs:
                if bob.id == ID:
                    return bob
        return None
    
    