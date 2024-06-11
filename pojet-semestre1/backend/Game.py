import pygame
from pygame.locals import *
from random import randint

# import json
import pickle
from datetime import datetime
from os import path, makedirs
import time

from backend.Grid import *
from backend.Settings import Settings
from multi.network import Network
from backend.Bob import Bob
from backend.Edible import Edible

from frontend.Map import Map
from frontend.Gui import Gui
from frontend.DisplayStatsChart import DisplayStatsChart

class Game:

    def __init__(self, grid_size, screenWidth=930, screenHeight=640, dayLimit = 0, noInterface=False, nbDailyFood = 50, nbBobs = 5, maxTPS = Settings.maxTps):
        
        pygame.init()

        pygame.key.set_repeat(400, 30)
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEMOTION])

        # Time related variables
        self.frameClock = pygame.time.Clock()
        self.tickClock = pygame.time.Clock()
        self.tickCount = 0
        self.dayLimit = dayLimit
        self.maxTPS = maxTPS
        
        # Pause related variables
        self.running = True
        self.render = True
        self.paused = not noInterface # Pause the game if there is an interface, else run it
        self.wasPaused = False

        # Display related variables
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.renderHeight = False
        self.renderTextures = True
        self.displayStats = True
        self.noInterface = noInterface

        # Stats related variables
        self.followBestBob = False
        self.currentBestBob = None
        self.bobCountHistory = []
        self.bestBobGenerationHistory = []


        # Editor mode related variables
        self.editorMode = False
        self.editorModeType = "bob" # "bob" or "food"
        self.editorModeCoords = None
        
        # ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️ CONNEXION AU RÉSEAU ⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️

        Network.requestConnection()
    
        first_connection = True

        # Attente de la réponse de connexion
        message = Network.timeout(1,Network.recvConnectionResponse)
        Network.connected = True
        if message is not None:
            first_connection = False

        
        # Si la réponse de connexion est reçue
        if not first_connection:
            print("ConnectionResponse received a game is already running, you are connected to it")
            networkArgs = Network.processConnectionResponse(message)

            # Création de la grille à partir des données reçues
            grid = Grid(networkArgs["gridSize"], foodCount=nbDailyFood, bobCount=nbBobs)
            for bob in networkArgs["bobs"]:
                grid.addBob(Bob(x=bob["x"], y=bob["y"], ID=bob["id"], mass=bob["mass"], energy=bob["energy"], Nproperty=bob["networkProperty"], Jproperty=bob["jobProperty"]))
        
            for food in networkArgs["foods"]:
                grid.addEdible(Food(x=food["x"], y=food["y"], ID=food["id"], energy=food["energy"], Nproperty=food["networkProperty"], Jproperty=food["jobProperty"]))

            successMessage = "ConnectionSuccess;"+str(Network.uuid_player)
            Network.sendMessage(successMessage)
            
        # Si la réponse de connexion n'est pas reçue
        else:
            print("you are the first player, creating a new game")

            # Création de la grille à partir de la taille donnée en argument du constructeur
            grid = Grid(grid_size, bobCount=nbBobs, foodCount=nbDailyFood)  

        # ⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️ FIN DE LA CONNEXION AU RÉSEAU ⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️

        # Grid related variables
        if type(grid) == Grid:
            self.grid = grid
            
            # Map size related variables
            self.mapWidth = self.grid.size
            self.mapHeight = self.grid.size
        
            if not self.noInterface:
                self.map = Map(self, screenWidth, screenHeight)
                self.gui = Gui(self, self.map, screenWidth, screenHeight)
            
            self.gridDict = self.grid.gridDict


        elif type(grid) == str:
            self.loadSaveFile(grid)

        Network.grid = self.grid
        Network.game = self
        
    # main loop
    def run(self):
        """
        Main loop of the game
        If the game is not paused, it launches a tick event every 1/maxTps seconds
        If a day has passed, it launches new day events
        """
        # Initialiser le temps du dernier tick
        last_tick_time = pygame.time.get_ticks()
        alpha = 0
        icon = pygame.image.load("assets/game-icon.png")
        pygame.display.set_icon(icon)
        
        if not self.noInterface:
            icon = pygame.image.load("assets/game-icon.png")
            pygame.display.set_icon(icon)

        if self.grid.dayCount == 0:
            # Populate the grid with random bobs and Food
            self.grid.spawnBobs()
            self.grid.spawnFood()
                                    
        if Settings.enableSpitting:
            self.grid.spawnSausages()

        # Game loop
        while self.running:
            # GESTION DES DONNÉES RÉSEAU REÇUES
            Network.sendMessagesBuffer()
            Network.processMessages()


            # handle events
            self.events()

            if not self.noInterface:            
                # display fps in title
                pygame.display.set_caption('Game of Life - FPS: ' + str(int(self.frameClock.get_fps())))

            # Refresh the frame clock
            self.frameClock.tick(Settings.maxFps)

            if not self.paused:
                # Vérifier si suffisamment de temps s'est écoulé depuis le dernier tick
                current_time = pygame.time.get_ticks()
                if current_time - last_tick_time >= 1000 / self.maxTPS:
                    # Mettre à jour le temps du dernier tick
                    last_tick_time = current_time

                    # Launch new day events
                    if self.tickCount % Settings.dayLength == 0 and (self.dayLimit == 0 or self.grid.dayCount < self.dayLimit):
                        self.grid.newDayEvents()
                    # Launch tick events
                    self.tickCount += 1
                    self.grid.newTickEvents()

                    # Compute the best bob, update the stats
                    self.currentBestBob = self.grid.getBestBob()
                    if self.currentBestBob is not None:
                        self.bobCountHistory.append(len(self.grid.getAllBobs()))
                        self.bestBobGenerationHistory.append(self.currentBestBob.generation)
                    
                # Calculate alpha, the percentage of the tick that has passed
                alpha = (pygame.time.get_ticks() - last_tick_time) / (1000 / self.maxTPS)

            if self.noInterface:
                bobCount = len(self.grid.getAllBobs())
                if bobCount == 0:
                    self.running = False
                    self.renderInTerminal()
                    # print("All bobs are dead")
                    continue
                self.renderInTerminal()
                continue

            if self.render:
                self.map.render(alpha)
                self.gui.render(self.map.screen, self.displayStats)


            pygame.display.update()
    
    def renderInTerminal(self):

        if self.tickCount == 0:
            # clear pygame init string, ect
            print('\033[2J', end='')

        gameString = self.grid.__str__()
        gameStringLinesCount = len(gameString.split('\n'))

        # clear terminal
        print(f'\033[{gameStringLinesCount + 3}A\033[2K', end='')

        # print game
        print(gameString, end='')

        # print stats
        print('\n')
        print(f'Tick: {self.tickCount} - Days: {self.grid.dayCount}')
        print(f'Bobs: {len(self.grid.getAllBobs())} - Food: {len(self.grid.getAllEdibleObjects())} ')

    # handle events
    def events(self):
        """
        Handle events
        Currently handles:
            - Quitting the game (by pressing the cross or escape)
            - Pausing the game (by pressing p)
            - Rendering the game (by pressing r)
            - Moving the map (by clicking and dragging)
            - Zooming the map (by scrolling)
        """
        for event in pygame.event.get():
            # Quitting the game (cross)
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                # Pausing the game and displaying the pause menu (escape)
                if event.key == pygame.K_ESCAPE:
                    if self.editorMode:
                        self.gui.displayPauseMenu = not self.gui.displayPauseMenu
                    else:
                        self.paused = not self.paused
                        self.wasPaused = not self.wasPaused
                        self.gui.displayPauseMenu = self.paused
                # Rendering the game (r)
                if event.key == pygame.K_r:
                    self.render = not self.render
                # Pausing the game (p)
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    self.wasPaused = not self.wasPaused
                    self.gui.displayPauseMenu = not self.paused
                # Rendering the height (h)
                if event.key == pygame.K_h:
                    self.renderHeight = not self.renderHeight
                    self.map.mustReRenderTerrain = True
                # Rendering the textures (t)
                if event.key == pygame.K_t:
                    self.renderTextures = not self.renderTextures
                    self.map.mustReRenderTerrain = True
                # Displaying stats (s)
                if event.key == pygame.K_s:
                    self.displayStats = not self.displayStats
                
                # serialize the game (o)
                if event.key == pygame.K_o:
                    # self.createSaveFile()
                    DisplayStatsChart(self.tickCount, self.bobCountHistory, self.bestBobGenerationHistory)

            # when scrolling, zoom the map
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    self.map.zoom()
                elif event.button == 5:  # Scroll down
                    self.map.unzoom()
            
            # when clicking and dragging, move the map
            if event.type == pygame.MOUSEMOTION:
                if event.buttons[0] == 1:
                    self.map.moveMap(event.rel)
            
            # if editing mode is enabled, check for clicks on the map and edit the grid accordingly
            if self.editorMode:

                if self.gui.displayPauseMenu:
                    if self.map.highlightedTile is not None:
                        self.map.highlightedTile = None
                        self.map.mustReRenderTerrain = True
                    continue

                if event.type == pygame.MOUSEMOTION: # event.type == pygame.MOUSEBUTTONDOWN:
                    self.editorModeCoords = self.map.getCoordsFromPosition(*event.pos)

                    if self.editorModeCoords is None:
                        continue

                    if event.buttons[0] == 1:
                        if self.editorModeType == "bob":
                            bob = Bob(self.editorModeCoords[0], self.editorModeCoords[1])
                            Network.sendNewBob(bob)
                            self.grid.addBob(bob)
                        elif self.editorModeType == "food":
                            food = Food(self.editorModeCoords[0], self.editorModeCoords[1])
                            Network.sendNewFood(food)
                            self.grid.addEdible(food)
                            
                            
                    if event.buttons[2] == 1:
                        if self.editorModeType == "bob":
                            self.grid.removeAllBobsAt(*self.editorModeCoords, Network.uuid_player)
                            Network.sendRemoveAllBobsAt(*self.editorModeCoords)
                        elif self.editorModeType == "food":
                            self.grid.removeFoodAt(*self.editorModeCoords, Network.uuid_player)
                            Network.sendRemoveFoodAt(*self.editorModeCoords)
                            
                            
                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.editorModeCoords is None:
                        continue

                    if event.button == 1:
                        if self.editorModeType == "bob":
                            bob = Bob(self.editorModeCoords[0], self.editorModeCoords[1])
                            Network.sendNewBob(bob)
                            self.grid.addBob(bob)
                            
                        elif self.editorModeType == "food":
                            food = Food(self.editorModeCoords[0], self.editorModeCoords[1])
                            Network.sendNewFood(food)
                            self.grid.addEdible(food)

                    if event.button == 3:

                        if self.editorModeType == "bob":
                            self.grid.removeAllBobsAt(*self.editorModeCoords, Network.uuid_player)
                            Network.sendRemoveAllBobsAt(*self.editorModeCoords)
                        elif self.editorModeType == "food":
                            self.grid.removeFoodAt(*self.editorModeCoords, Network.uuid_player)
                            Network.sendRemoveFoodAt(*self.editorModeCoords)
                            

                    
            if event.type == pygame.VIDEORESIZE:
                # There's some code to add back window content here.
                self.screenWidth = event.w
                self.screenHeight = event.h

                self.map.resize(event.w, event.h)
                self.gui.resize(event.w, event.h)

    def createSaveFile(self, pathToSaveFolder='saves', saveName=None):
        """
        Serialize the game and save it in a json file at the given path.
        Can't be used when the game is running.
        """
        if not self.paused:
            raise Exception("Can't serialize a game that is not paused")
        
        if saveName is None:
            saveName = datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".save"
        
        if not path.exists(pathToSaveFolder):
            makedirs(pathToSaveFolder)

        with open(path.join(pathToSaveFolder, saveName), 'wb') as f:
            pickle.dump({ 'grid': self.grid, 'settings': Settings.getSettings(), 'tickCount': self.tickCount }, f, pickle.HIGHEST_PROTOCOL)

        print("Game saved as " + saveName)

        return saveName

    def loadSaveFile(self, pathToSaveFile):
        with open(pathToSaveFile, 'rb') as f:
            try:
                data = pickle.load(f)
            except:
                print("Error while loading save file")
                return False

        self.grid = data['grid']

        Settings.setSettings(data['settings'])
        
        self.tickCount = data['tickCount']

        # Map size related variables
        self.mapWidth = self.grid.size
        self.mapHeight = self.grid.size
    
        if not self.noInterface:
            self.map = Map(self, self.screenWidth, self.screenHeight)
            self.gui = Gui(self, self.map, self.screenWidth, self.screenHeight)
            
        self.gridDict = self.grid.gridDict

        self.paused = True
        self.wasPaused = True
        self.gui.displayPauseMenu = True
        
        print("Game loaded from " + pathToSaveFile)

        return True
