import pygame

from frontend.frontendConstantes import *
from backend.Settings import *
from frontend.settingsWindow import SettingsWindow
from backend.Multi import *

import time

class Gui:

    def __init__(self, game, map, screenWidth, screenHeight):
        
        self.game = game
        self.map = map

        self.displayPauseMenu = True
    
        self.pauseButtonCooldown = 0.2  # Cooldown time in seconds
        self.lastPauseButtonClick = 0

        self.followBestBobButtonCooldown = 0.2  # Cooldown time in seconds
        self.lastFollowBestBobButtonClick = 0

        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.guiSurface = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)

    def resize(self, screenWidth, screenHeight):
        self.guiSurface = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)

    def render(self, screen, displayStats):

        self.guiSurface.fill((0,0,0,0))
        
        self.renderTogglePauseMenuButton()

        if self.game.paused:
            if self.displayPauseMenu:
                self.renderPauseMenu()
            else:
                self.renderTooltips()

        if self.game.editorMode:
            self.renderEditorButtons()
        
        if displayStats:
            self.stats()

        if self.game.followBestBob and self.game.currentBestBob is not None:
            self.renderTooltip(self.game.currentBestBob, 10, self.screenHeight - 200, self.game.currentBestBob.currentX - self.map.worldXoffset, self.game.currentBestBob.currentY - self.map.worldYoffset)

        screen.blit(self.guiSurface, (0,0))

    def stats(self):

        bobImg = pygame.image.load("assets/main-bob.png")
        bobImg = pygame.transform.scale(bobImg, (30, 30))  # Increase image size
        bobCount = len(self.game.grid.getAllBobs())
        
        # draw a bob count indicator in the top left corner
        self.guiSurface.blit(bobImg, (10, 10))
        font = pygame.font.SysFont('Arial', 25)  # Increase font size
        text = font.render(f"{bobCount}", True, (255,255,255))
        self.guiSurface.blit(text, (10 + bobImg.get_width() + 10, 10 + bobImg.get_height() / 2 - text.get_height() / 2))

        # draw uuid of the player
        text = font.render(f"Player uuid: {Network.uuid_player}", True, (255,255,255))
        self.guiSurface.blit(text, (10, 10 + bobImg.get_height() + 10))


        # draw a day count indicator in the top right corner
        text = font.render(f"Day {self.game.grid.dayCount}", True, (255,255,255))
        self.guiSurface.blit(text, (self.guiSurface.get_width() - text.get_width() - 10, 10 + bobImg.get_height() / 2 - text.get_height() / 2))

        # ticks
        text = font.render(f"{self.game.tickCount} ticks", True, (255,255,255))
        self.guiSurface.blit(text, (self.guiSurface.get_width() - text.get_width() - 10, 10 + bobImg.get_height() / 2 - text.get_height() / 2 + text.get_height()))

    def renderEditorButtons(self):
        # draw three buttons in the bottom right corner
        # First one is "add bob" and second is "add food"

        buttonWidth = 110
        buttonHeight = 30
        buttonX = self.guiSurface.get_width() - buttonWidth - 20
        buttonY = self.guiSurface.get_height() - buttonHeight - 20

        # Bob brush button
        self.smallButton(buttonX, buttonY, buttonWidth, buttonHeight, "Add / remove bob", self.guiSurface, lambda : setattr(self.game, "editorModeType", "bob"), self.game.editorModeType == "bob")

        # add food button
        self.smallButton(buttonX, buttonY - (buttonHeight + 10), buttonWidth, buttonHeight, "Add / remove food", self.guiSurface, lambda : setattr(self.game, "editorModeType", "food"), self.game.editorModeType == "food")

        # Clear bobs button
        self.smallButton(buttonX - (buttonWidth + 10), buttonY, buttonWidth, buttonHeight, "Clear bobs", self.guiSurface, lambda : self.game.grid.removeAllBobs(), len(self.game.grid.getAllBobs()) == 0)

        # Clear food button
        self.smallButton(buttonX - (buttonWidth + 10), buttonY - (buttonHeight + 10), buttonWidth, buttonHeight, "Clear food", self.guiSurface, lambda : self.game.grid.removeAllEdibles(), len(self.game.grid.getAllEdibleObjects()) == 0)

    def smallButton(self, x, y, width, height, text, surface, action, selected=False):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        # Set button color based on selected parameter
        buttonColor = (100, 100, 100) if selected else (255, 255, 255)

        # draw the button
        pygame.draw.rect(surface, buttonColor, (x, y, width, height), border_radius=10)

        # draw the text
        font = pygame.font.SysFont('Arial', 15)
        text = font.render(text, True, (0, 0, 0))
        surface.blit(text, (x + width / 2 - text.get_width() / 2, y + height / 2 - text.get_height() / 2))

        # check if the mouse is inside the hitbox
        if mouse[0] >= x and mouse[0] <= x + width and mouse[1] >= y and mouse[1] <= y + height:

            hoveredButtonColor = (50, 50, 50) if selected else (200, 200, 200)

            pygame.draw.rect(surface, hoveredButtonColor, (x, y, width, height), border_radius=10, width=2)

            # check if the button is clicked
            if click[0] == 1:
                action()  # call the function passed as a parameter

    def renderTooltips(self):
    
        # iterate over all bobs, if the bob is under the mouse, display its tooltip
        mouseX, mouseY = pygame.mouse.get_pos()

        for bob in self.game.grid.getAllBobs():
            
            # The tile the bob is supposed to be on
            xTile = bob.currentX - self.map.worldXoffset
            yTile = bob.currentY - self.map.worldYoffset

            # The tile the bob is actually on (can be between two real tiles)
            animatedXTile = bob.sprite.displayX - self.map.worldXoffset
            animatedYTile = bob.sprite.displayY - self.map.worldYoffset

            # don't display entities outside the screen
            if xTile < 0 or xTile > self.map.width or yTile < 0 or yTile > self.map.height:
                continue
            
            height = self.map.getHeightAt(bob.currentX, bob.currentY) * ((tileTotalHeightOriginal * self.map.scaleMultiplier) / 2 - 2) # 2 = height of the "hole" in the tile

            xScreen = (self.map.terrainSurface.get_width() - self.map.width*self.map.scaleMultiplier*tileTotalWidthOriginal)/2 + self.map.terrainSurface.get_width() / 2 + (animatedXTile-2) * (tileTotalWidthOriginal * self.map.scaleMultiplier) / 2 -  + animatedYTile * (tileTotalWidthOriginal * self.map.scaleMultiplier) / 2
            yScreen = animatedYTile * (tileVisibleHeightOriginal * self.map.scaleMultiplier) / 2 + animatedXTile * (tileVisibleHeightOriginal * self.map.scaleMultiplier) / 2 - height

            # # draw the hitbox
            # pygame.draw.rect(self.guiSurface, (255,255,255), (xScreen + self.map.xScreenOffset, yScreen + self.map.yScreenOffset - (tileTotalHeightOriginal * self.map.scaleMultiplier) / 2, tileTotalWidthOriginal * self.map.scaleMultiplier, tileTotalHeightOriginal * self.map.scaleMultiplier), width=2)

            # check if the mouse is inside the hitbox
            if mouseX >= xScreen + self.map.xScreenOffset and mouseX <= xScreen + self.map.xScreenOffset + tileTotalWidthOriginal * self.map.scaleMultiplier and mouseY >= yScreen + self.map.yScreenOffset - (tileTotalHeightOriginal * self.map.scaleMultiplier) / 2 and mouseY <= yScreen + self.map.yScreenOffset + (tileTotalHeightOriginal * self.map.scaleMultiplier) / 2:
                self.renderTooltip(bob, mouseX, mouseY, xTile - 1, yTile - 1)
                break
            
    def renderTooltip(self, bob, x, y, xTile, yTile):
        tooltipWidth = 250
        tooltipHeight = 260

        tooltip = pygame.Surface((tooltipWidth, tooltipHeight), pygame.SRCALPHA)
        pygame.draw.rect(tooltip, (0,0,0,200), (0, 0, tooltipWidth, tooltipHeight), border_radius=10)

        font = pygame.font.SysFont('Arial', 15)

        # energy
        self.progressBar(10, 10, 230, 15, bob.energy / bob.energyMax, f"Energy: {int(bob.energy)} / {Settings.energyMax}", (194, 14, 14), tooltip)

        # age
        text = font.render(f"Age: {bob.age} ticks", True, (255,255,255))
        tooltip.blit(text, (10, 30))

        # mass -> no maximum so no progress bar just text
        text = font.render(f"Mass: {bob.mass:.1f}", True, (255,255,255))
        tooltip.blit(text, (10, 50))
        
        # velocity -> no maximum so no progress bar just text
        text = font.render(f"Velocity: {bob.velocity:.1f} tile/tick", True, (255,255,255))
        tooltip.blit(text, (10, 70))

        # perception -> no maximum so no progress bar just text
        text = font.render(f"Vision range: {bob.getPerceptionRange()} tiles", True, (255,255,255))
        tooltip.blit(text, (10, 90))

        #bob id
        text = font.render(f"Bob uuid:", True, (255,255,255))
        tooltip.blit(text, (10, 110))
        text = font.render(f"{bob.id}", True, (255,255,255))
        tooltip.blit(text, (10, 130))

        #bob network properties
        text = font.render(f"Bob network properties uuid:", True, (255,255,255))
        tooltip.blit(text, (10, 150))
        text = font.render(f"{bob.network_properties}", True, (255,255,255))
        tooltip.blit(text, (10, 170))

        #bob job properties
        text = font.render(f"Bob job properties uuid:", True, (255,255,255))
        tooltip.blit(text, (10, 190))
        text = font.render(f"{bob.job_properties}", True, (255,255,255))
        tooltip.blit(text, (10, 210))

        # draw the outline of the vision area

        # get the center of the tile
        
        tileCenterX = (self.map.terrainSurface.get_width() - self.map.width*self.map.scaleMultiplier*tileTotalWidthOriginal)/2 + self.map.terrainSurface.get_width() / 2 + (xTile-1) * (tileTotalWidthOriginal * self.map.scaleMultiplier) / 2 - (yTile) * (tileTotalWidthOriginal * self.map.scaleMultiplier) / 2 + self.map.xScreenOffset
        tileCenterY = (yTile + 2) * (tileVisibleHeightOriginal * self.map.scaleMultiplier) / 2 + (xTile-1) * (tileVisibleHeightOriginal * self.map.scaleMultiplier) / 2 + self.map.yScreenOffset

        self.drawManhattanCircle(tileCenterX, tileCenterY, bob.getPerceptionRange(), self.guiSurface, xTile, yTile)

        # memory -> no maximum so no progress bar just text
        memory = bob.foodMemory
        text = font.render(f"Memory: {len(memory)} out of {bob.getMemorySize()} objects", True, (255,255,255))
        tooltip.blit(text, (10, 230))

        # draw a rectangle around the memorized objects
        for obj in memory:
            objX = obj[0] - self.map.worldXoffset
            objY = obj[1] - self.map.worldYoffset

            # don't display entities outside the screen
            if objX < 0 or objX > self.map.width or objY < 0 or objY > self.map.height:
                continue

            objHeight = self.map.getHeightAt(objX, objY) * ((tileTotalHeightOriginal * self.map.scaleMultiplier) / 2 - 2)

            objXScreen = (self.map.terrainSurface.get_width() - self.map.width*self.map.scaleMultiplier*tileTotalWidthOriginal)/2 + self.map.terrainSurface.get_width() / 2 + (objX-2) * (tileTotalWidthOriginal * self.map.scaleMultiplier) / 2 -  + objY * (tileTotalWidthOriginal * self.map.scaleMultiplier) / 2
            objYScreen = objY * (tileVisibleHeightOriginal * self.map.scaleMultiplier) / 2 + objX * (tileVisibleHeightOriginal * self.map.scaleMultiplier) / 2 - objHeight

            pygame.draw.rect(self.guiSurface, (255,255,255), (objXScreen + self.map.xScreenOffset, objYScreen + self.map.yScreenOffset - (tileTotalHeightOriginal * self.map.scaleMultiplier) / 2, tileTotalWidthOriginal * self.map.scaleMultiplier, tileTotalHeightOriginal * self.map.scaleMultiplier), width=2)

        self.guiSurface.blit(tooltip, (x, y))

    def progressBar(self, x, y, width, height, progress, text, color, surface):
        # draw the progress bar (rounded rectangle). Make the rest of the bar darker
        pygame.draw.rect(surface, (0,0,0,150), (x, y, width, height), border_radius=height//2)
        pygame.draw.rect(surface, color, (x, y, width * progress, height), border_radius=height//2)
        pygame.draw.rect(surface, (0,0,0,150), (x + width * progress, y, width * (1 - progress), height), border_radius=height//2)

        # draw the text
        font = pygame.font.SysFont('Arial', 15)
        text = font.render(text, True, (255,255,255))
        surface.blit(text, (x + width / 2 - text.get_width() / 2, y + height / 2 - text.get_height() / 2))

    # draw a circle using manhattan distance on the map
    def drawManhattanCircle(self, x, y, radius, surface, xTile, yTile):

        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):

                currentTileX = xTile + (i+j)//2 + self.map.worldXoffset
                currentTileY = yTile + (j-i)//2 + self.map.worldYoffset

                if currentTileX < 0 or currentTileX >= self.game.mapWidth or currentTileY  < 0 or currentTileY >= self.game.mapHeight:
                    continue

                if i == -radius or i == radius or j == -radius or j == radius:    
                    xDot = x + i * tileTotalWidthOriginal * self.map.scaleMultiplier / 2
                    yDot = y + j * tileVisibleHeightOriginal * self.map.scaleMultiplier / 2

                    pygame.draw.circle(surface, (255,255,255), (xDot, yDot), 2)

    def renderTogglePauseMenuButton(self):
        # draw the pause button
        pauseButtonWidth = 30
        pauseButtonHeight = 30

        pauseButton = pygame.Surface((pauseButtonWidth, pauseButtonHeight), pygame.SRCALPHA)
        btnColor = (200, 200, 200)
        btnColorClicked = (100, 100, 100)

        # draw the burger menu icon
        iconPadding = 6
        iconSize = min(pauseButtonWidth, pauseButtonHeight) - 2 * iconPadding
        iconX = pauseButtonWidth / 2 - iconSize / 2
        iconY = pauseButtonHeight / 2 - iconSize / 2

        pygame.draw.rect(pauseButton, btnColor, (iconX, iconY, iconSize, 4))
        pygame.draw.rect(pauseButton, btnColor, (iconX, iconY + iconPadding, iconSize, 4))
        pygame.draw.rect(pauseButton, btnColor, (iconX, iconY + 2 * iconPadding, iconSize, 4))

        # check if the mouse is inside the hitbox
        mouseX, mouseY = pygame.mouse.get_pos()
        if mouseX >= 20 and mouseX <= 20 + pauseButtonWidth and mouseY >= self.guiSurface.get_height() - pauseButtonHeight - 20 and mouseY <= self.guiSurface.get_height() - 20:

            pygame.draw.rect(pauseButton, btnColorClicked, (iconX, iconY, iconSize, 4))
            pygame.draw.rect(pauseButton, btnColorClicked, (iconX, iconY + iconPadding, iconSize, 4))
            pygame.draw.rect(pauseButton, btnColorClicked, (iconX, iconY + 2 * iconPadding, iconSize, 4))


            # check if the button is clicked
            if pygame.mouse.get_pressed()[0] == 1 and time.time() - self.lastPauseButtonClick > self.pauseButtonCooldown:
                self.lastPauseButtonClick = time.time()
                
                
                if not self.game.paused:
                    self.game.paused = True
                    self.displayPauseMenu = True
                else:
                    self.displayPauseMenu = not self.displayPauseMenu

        self.guiSurface.blit(pauseButton, (20, self.guiSurface.get_height() - pauseButtonHeight - 20))

    def renderPauseMenu(self):
            
            # draw the pause menu
            pauseMenuWidth = 300
            pauseMenuHeight = 500
    
            pauseMenu = pygame.Surface((pauseMenuWidth, pauseMenuHeight), pygame.SRCALPHA)
            pygame.draw.rect(pauseMenu, (0,0,0,200), (0, 0, pauseMenuWidth, pauseMenuHeight), border_radius=10)
    
            font = pygame.font.SysFont('Arial', 30)
    
            # draw the title
            text = font.render("Paused", True, (255,255,255))
            pauseMenu.blit(text, (pauseMenuWidth / 2 - text.get_width() / 2, 10))
    
            # draw the buttons
            buttonWidth = 200
            buttonHeight = 50
            buttonX = pauseMenuWidth / 2 - buttonWidth / 2
            buttonY = 100
    

            pauseMenuOffset = self.guiSurface.get_width() / 2 - pauseMenuWidth / 2, self.guiSurface.get_height() / 2 - pauseMenuHeight / 2

            # resume button
            self.button(buttonX, buttonY, pauseMenuOffset, buttonWidth, buttonHeight, "Resume", pauseMenu, lambda: setattr(self.game, "paused", False))
            
            # options button
            self.button(buttonX, buttonY + buttonHeight + 10, pauseMenuOffset, buttonWidth, buttonHeight, "Options", pauseMenu, lambda : SettingsWindow(self.game.createSaveFile, self.game.loadSaveFile))
    
            #multiplayer button
            self.button(buttonX, buttonY + 2 * (buttonHeight + 10), pauseMenuOffset, buttonWidth, buttonHeight, "Multiplayer", pauseMenu, lambda : self.game.net.toggleMultiplayer())

            # editor mode button
            self.button(buttonX, buttonY + 3 * (buttonHeight + 10), pauseMenuOffset, buttonWidth, buttonHeight, "Editor mode", pauseMenu, lambda : [setattr(self.game, "editorMode", not self.game.editorMode), setattr(self, "displayPauseMenu", not getattr(self, "displayPauseMenu")), setattr(self.game, "renderHeight", False)],)

            # Follow best bob button
            self.button(buttonX, buttonY + 4 * (buttonHeight + 10), pauseMenuOffset, buttonWidth, buttonHeight, "Follow best bob", pauseMenu, self.followBestBobButtonWithCooldown)
            
            # quit button
            self.button(buttonX, buttonY + 5 * (buttonHeight + 10), pauseMenuOffset, buttonWidth, buttonHeight, "Quit", pauseMenu, lambda : setattr(self.game, "running", False))
    

            self.guiSurface.blit(pauseMenu, (self.guiSurface.get_width() / 2 - pauseMenuWidth / 2, self.guiSurface.get_height() / 2 - pauseMenuHeight / 2))


    def followBestBobButtonWithCooldown(self):
        if time.time() - self.lastFollowBestBobButtonClick > self.followBestBobButtonCooldown:
            self.lastFollowBestBobButtonClick = time.time()
            self.game.followBestBob = not self.game.followBestBob

    def button(self, x, y, pauseMenuOffset, width, height, text, surface, action):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
    
        # draw the button
        pygame.draw.rect(surface, (255,255,255), (x, y, width, height), border_radius=10)
    
        # draw the text
        font = pygame.font.SysFont('Arial', 30)
        text = font.render(text, True, (0,0,0))
        surface.blit(text, (x + width / 2 - text.get_width() / 2, y + height / 2 - text.get_height() / 2))
    
        # check if the mouse is inside the hitbox
        if mouse[0] >= x + pauseMenuOffset[0] and mouse[0] <= x + pauseMenuOffset[0] + width and mouse[1] >= y + pauseMenuOffset[1] and mouse[1] <= y + pauseMenuOffset[1] + height:

            pygame.draw.rect(surface, (200,200,200), (x, y, width, height), border_radius=10, width=2)
    
            # check if the button is clicked
            if click[0] == 1:
                action() # call the function passed as a parameter