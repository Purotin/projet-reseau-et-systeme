class Settings:

    version = "0.1.5"

    #----------------------------------------------enable FEATURES--------------------------------------------

    enableFeed = True  # Enables the feeding mechanism for Bob objects. Bobs can eat food and other bobs.

    enablePerception = True  # Enables the perception mechanism for Bob objects. Bobs can see food and other bobs in a certain radius around them.

    enableMovement = True  # Enables the movement mechanism for Bob objects. If set to False, all bobs will be static.

    enableEnergyConsumption = True  # Enables the energy consumption mechanism for Bob objects. Faster bobs consume more energy, etc

    enableMemory = True  # Enables the memory mechanism for Bob objects. Bobs can remember the location of food they have seen.

    enableMass = True  # Enables the mass mechanism for Bob objects.

    enableVelocity = True  # Enables the velocity mechanism for Bob objects. 

    enableSmoothMovement = True # Enables the smooth movement mechanism for Bob objects. Bobs move smoothly instead of jumping from cell to cell.

    donut = False  # Enables the donut grid mode. Instead of having a border, the grid is a donut. Bobs can go through the edges and appear on the opposite side.

    enableAnimation = True # Enables the animation mechanism for Bob objects. Bobs have an animation when they move, eat, etc.

    computeColorSprite = False  # Enables the color mechanism for Bob objects. Faster bobs are redder, etc

    enableEffects = True # Enables the effects mechanism for Bob objects. Bobs can be affected by effects such as being spit at.

    enableSpitting = True # Enables the spitting mechanism for Bob objects. Bobs can spit ammos to hinder other bobs.

    enableSexualReproduction = True # Enables the sexual reproduction mechanism for Bob objects. Bobs can reproduce with other bobs.

    enableParthenogenesis = True # Enables the parthenogenesis mechanism for Bob objects. Bobs can reproduce without other bobs.

    enableMutation = True # Enables the mutation mechanism for Bob objects. Bobs can mutate when they reproduce.

    enableMutantFood = False # Enables the apparition of mutantFood

    enableIsotonicDrinks = False # Enables the apparition of isotonic drinks, food that reduces the energy consumption of a bob when eaten

    enableMassMaxEnergy = False # Enables the massMaxEnergy mechanism for Bob objects. Bobs can have a maximum energy depending on their mass.

    enableNoise = True # Enables the perlin noise used to randomize the map textures and height

    #----------------------------------------------GAME SETTINS--------------------------------------------
    
    dayLength = 100 # the number of ticks in a day

    maxTps = 10 # the maximum number of ticks per second

    maxFps = 60 # the maximum number of frames per second

    #----------------------------------------------ENERGY--------------------------------------------


    spawnEnergy = 151 # the energy level a bob starts at when spawned by the game

    energyMax = 200 # the maximum amount of energy a bob can have

    motherEnergy = 150 # the required amount of energy for a bob do give birth

    matingEnergyConsumption = 100 # the amount of energy a bob loses when mating

    matingEnergyRequirement = 150 # the amount of energy a bob needs to mate

    tickMinEnergyConsumption = .5 # the minimal amount of energy a bob consumes per tick

    spawnedFoodEnergy = 100 # the amount of energy a food gives when spawned

    #--------------------------------------------VELOCITY--------------------------------------------

    spawnVelocity = 2 # the velocity a bob starts at it spawns in the game

    minVelocity = 0 # the minimal velocity for any bob

    #----------------------------------------------MASS----------------------------------------------

    spawnMass = 2 # the mass a bob starts at when spawner by the game

    minMass = 1 # the minimal mass for any bob

    massRatioThreshold = 2/3 # the maximal mass ration between a smaller bob and a bigger bob necessary for the bigger bob to eat the smaller one

    #----------------------------------------------VISION----------------------------------------------

    spawnPerception = 5 # the default radius of perception of a bob spawner by the game

    preyFactor = 1 # The factor by which the food value of a cell seen by a bob is multiplied by during the cost calculation during the pathfinding

    predatorFactor = 5 # The value that works the opposite of foodFactor when a bob sees a predator

    foodFactor = 1 # The factor by which the food value of a cell seen by a bob is multiplied by during the cost calculation during the pathfinding (float)

    #----------------------------------------------MEMORY----------------------------------------------

    spawnMemory = 3 # the default number of food location a bob has in memory when spawned by the game

    #----------------------------------------------MUTATION----------------------------------------------
    velocityMutation = .1 # the mutation rate for velocity (float)

    massMutation = .1 # the mutation rate for mass (float)

    perceptionMutation = 1 # the mutation rate for mass (int)

    memoryMutation = 1 # the mutation rate for memory (int)

    pBirthEnergy = 50 # the energy level a newborn bob by parthenogenesis is given (float)

    sBirthEnergy = 100 # the energy level a newborn bob by sexual reproduction is given (float)

    #----------------------------------------------SPITTING----------------------------------------------
    
    spawnAmmos = 3 # the default number of ammos a bob has when spawned by the game
    
    spawnMaxAmmos = 10 # the default number of ammos a bob has when spawned by the game

    spawnSausagesAmmos = 3 # the default number of ammos a sausage has when spawned by the game

    #-----------------------------------------------COLORS-----------------------------------------------

    velocityFactor = 10 # the factor by which the velocity of a bob is multiplied by to get the blue value of its color

    perceptionFactor = 10 # the factor by which the perception of a bob is multiplied by to get the green value of its color

    memoryFactor = 10 # the factor by which the memory of a bob is multiplied by to get the red value of its color

    def getSettings():
        return { k: v for k, v in Settings.__dict__.items() if not k.startswith('__') and not callable(v) }
    
    def getSetting(key):
        return getattr(Settings, key)

    def setSetting(key, value):
        setattr(Settings, key, value)
    
    def setSettings(settings):
        for key, value in settings.items():
            setattr(Settings, key, value)