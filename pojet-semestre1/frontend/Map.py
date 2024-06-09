from pygame.locals import *
import pygame

from random import randint
import pygame

import functools
import noise

from backend.Settings import *
from backend.Edible import *
from backend.Effect import *
from multi.network import Network
from frontend.frontendConstantes import *
from frontend.Projectiles import Spittle

class Map:

    def __init__(self, Game, screenWidth=930, screenHeight=640):
        
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.worldSeed = randint(0, 10000)

        self.highlightedTile = None

        self.width = Game.mapWidth + 2
        self.height = Game.mapHeight + 2
        
        self.scaleMultiplier = self.screenWidth / ((self.width + 1) * tileTotalWidthOriginal)
        
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), RESIZABLE, DOUBLEBUF)
        pygame.display.set_caption('Game of Life')

        self.bobSurface = pygame.Surface((self.screenWidth, self.screenHeight), pygame.SRCALPHA)
        self.terrainSurface = pygame.Surface((self.screenWidth, self.screenHeight), pygame.SRCALPHA)

        # set initial position for display on screen
        self.xScreenOffset = 0
        self.yScreenOffset = abs((self.screenHeight - (tileVisibleHeightOriginal * self.scaleMultiplier) * self.height) // 2 - ((tileTotalHeightOriginal - tileVisibleHeightOriginal) * self.scaleMultiplier) // 2)

        self.tilesAssets = []

        self.worldXoffset = -1
        self.worldYoffset = -1

        self.zoomCenter = pygame.Vector2(self.screenWidth // 2, self.screenHeight // 2)

        self.mustReRenderTerrain = True

        self.Game = Game

        self.loadAllImages()
    
    def resize(self, screenWidth, screenHeight):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.scaleMultiplier = self.screenWidth / ((self.width + 1) * tileTotalWidthOriginal)

        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), RESIZABLE, DOUBLEBUF)
        self.bobSurface = pygame.Surface((self.screenWidth, self.screenHeight), pygame.SRCALPHA)
        self.terrainSurface = pygame.Surface((self.screenWidth, self.screenHeight), pygame.SRCALPHA)

        self.xScreenOffset = 0
        self.yScreenOffset = abs((self.screenHeight - (tileVisibleHeightOriginal * self.scaleMultiplier) * self.height) // 2 - ((tileTotalHeightOriginal - tileVisibleHeightOriginal) * self.scaleMultiplier) // 2)

        self.loadAllImages()

        self.mustReRenderTerrain = True
    
    def loadImage(self, filename):
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (int(tileTotalWidthOriginal * self.scaleMultiplier), int(tileTotalHeightOriginal * self.scaleMultiplier)))
        return image

    def loadAllImages(self):

        # TODO: test if loading different textures based on the zoom level can improve performance

        # Tiles assets - index is the height of the tile
        self.tilesAssets = [
            self.loadImage('assets/ext/isometric-blocks/PNG/Platformer tiles/platformerTile_48.png'), # water
            self.loadImage('assets/ext/isometric-blocks/PNG/Platformer tiles/platformerTile_48.png'), # sand
            self.loadImage('assets/ext/isometric-blocks/PNG/Platformer tiles/platformerTile_48.png'), # grass
            self.loadImage('assets/ext/isometric-blocks/PNG/Platformer tiles/platformerTile_48.png'), # box
        ]

        # Default tile asset - used when the height is not enabled
        self.defaultTileAsset = self.loadImage('assets/ext/isometric-blocks/PNG/Platformer tiles/platformerTile_44.png')
        
        # Border tile asset - used when the tile is outside the map
        self.borderTile = self.loadImage('assets/ext/isometric-blocks/PNG/Abstract tiles/abstractTile_20.png')

        self.edibleAssets = {
            "pizza": self.loadImage('assets/pizza.png'),
            "croissant": self.loadImage('assets/croissant.png'),
            "sausage": self.loadImage('assets/hot-dog.png'),
            "mutant-pizza": self.loadImage('assets/mutant-pizza.png'),
            "mutant-croissant": self.loadImage('assets/mutant-croissant.png'),
            "powerade": self.loadImage('assets/powerade.png'),
        }

        self.bobsAssets = {
            "idle": self.loadSpriteSheet("assets/sprite-sheets/idle-sheet.png"),
            "parthenogenesis": self.loadSpriteSheet("assets/sprite-sheets/parthenogenesis-sheet.png"),
            "eat": self.loadSpriteSheet("assets/sprite-sheets/eat-sheet.png"),
            "eaten": self.loadSpriteSheet("assets/sprite-sheets/eaten-sheet.png"),
            "move": self.loadSpriteSheet("assets/sprite-sheets/movement-sheet.png"),
            "decay": self.loadSpriteSheet("assets/sprite-sheets/decay-sheet.png"),
            "spit": self.loadSpriteSheet("assets/sprite-sheets/spit-sheet.png"),
            "love": self.loadSpriteSheet("assets/sprite-sheets/love-sheet.png"),
        }
        
        self.effectsAssets = {
            "spittedAt": self.loadSpriteSheet("assets/sprite-sheets/spit-effect-sheet.png"),
            "superMutation": self.loadImage("assets/radioactive-symbol.png"),
            "powerCharged": self.loadImage("assets/lightning.png"),
        }

        # Double the size of the sheets
        for key in self.bobsAssets:
            self.bobsAssets[key] = [pygame.transform.scale(sprite, (sprite.get_width() * 2, sprite.get_height() * 2)) for sprite in self.bobsAssets[key]]
   
    def loadSpriteSheet(self, path):
        """Load a sprite sheet from the given path and return a list of sprites"""
        # Load the sprite sheet
        spriteSheet = pygame.image.load(path)

        # Initialize the list of sprites
        sprites = []

        # Get the width and height of the sprites
        spriteWidth = spriteSheet.get_height()  # Assuming the sprites are square
        spriteHeight = spriteSheet.get_height()

        # Calculate the number of sprites in the sprite sheet
        numSprites = spriteSheet.get_width() // spriteWidth

        # Add each sprite to the list
        for i in range(numSprites):
            rect = pygame.Rect(i * spriteWidth, 0, spriteWidth, spriteHeight)
            sprites.append(spriteSheet.subsurface(rect))

        # Return the list of sprites
        return sprites
   
    @functools.cache
    def getPerlinNoise(self, x, y, scale=80, octaves=6, persistence=0.5, lacunarity=2.0):
        if(not Settings.enableNoise): return 0
        return abs(noise.snoise2(x/scale, y/scale, octaves, persistence, lacunarity, self.worldSeed))

    def getTerrainAt(self, x, y):
        if not self.Game.renderTextures:
            return -1

        noiseValue = self.getPerlinNoise(x, y)

        return round(noiseValue * len(self.tilesAssets))

    def getHeightAt(self, x, y):

        if not self.Game.renderHeight or x < 0 or x >= self.Game.mapWidth or y < 0 or y >= self.Game.mapHeight:
            return 0

        noiseValue = self.getPerlinNoise(x, y)
        return round(noiseValue * len(self.tilesAssets))
    
    def getBobsAt(self, x, y):
        return self.Game.grid.getBobsAt(x, y)
    
    def cartesianToIsometric(self, x, y):
        isoX = (x + y)*2*self.scaleMultiplier# * (tileTotalWidthOriginal * self.scaleMultiplier) / 2
        isoY = (x - y)*2*self.scaleMultiplier# * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2
        return isoX, isoY
    
    def checkWorldOffset(self):
        if self.worldXoffset < -1:
            self.worldXoffset = -1
        elif self.worldXoffset > self.Game.mapWidth - self.width + 1:
            self.worldXoffset = self.Game.mapWidth - self.width + 1

        if self.worldYoffset < -1:
            self.worldYoffset = -1
        elif self.worldYoffset > self.Game.mapHeight - self.height + 1:
            self.worldYoffset = self.Game.mapHeight - self.height + 1

    def moveMap(self, mouseMovementVector=(0,0)):
        x, y = self.cartesianToIsometric(mouseMovementVector[0], mouseMovementVector[1])

        newWorldXoffset = self.worldXoffset - int(x)
        newWorldYoffset = self.worldYoffset + int(y)

        self.worldXoffset = newWorldXoffset
        self.worldYoffset = newWorldYoffset

        self.checkWorldOffset()

        self.mustReRenderTerrain = True
    
    def zoom(self):

        if self.width == 20 or self.height == 20:
            return

        self.height -= self.height // 20
        self.width -= self.width // 20
        self.scaleMultiplier = self.screenWidth / ((self.width + 1) * tileTotalWidthOriginal)

        self.loadAllImages()
        self.mustReRenderTerrain = True

        mousePosition = pygame.Vector2(pygame.mouse.get_pos())

        # Calcul du déplacement nécessaire pour centrer la carte sur la position du curseur de la souris
        delta = (self.zoomCenter - mousePosition) / self.scaleMultiplier
        delta[0] /= tileTotalHeightOriginal
        delta[1] /= tileTotalHeightOriginal

        # Déplacement de la carte
        self.moveMap(delta)
    
    def unzoom(self):
        if self.width == self.Game.mapWidth + 2 or self.height == self.Game.mapHeight + 2:
            return

        if self.width + self.width // 20 > self.Game.mapWidth or self.height + self.height // 20 > self.Game.mapHeight:
            self.width = self.Game.mapWidth + 2
            self.height = self.Game.mapHeight + 2

        else:
            self.height += self.height // 20
            self.width += self.width // 20

        self.scaleMultiplier = self.screenWidth / ((self.width + 1) * tileTotalWidthOriginal)
        self.loadAllImages()
        self.mustReRenderTerrain = True

        self.checkWorldOffset()

    def renderMap(self):
            
            self.terrainSurface.fill((0,0,0,255))
            
            for y in range(self.height):
                for x in range(self.width):
                    # assume: north-is-upper-right
    
                    xTile = ( x + self.worldXoffset ) #% self.width
                    yTile = ( y + self.worldYoffset ) #% self.height

                    height = self.getHeightAt(xTile, yTile) * ((tileTotalHeightOriginal * self.scaleMultiplier) / 2 - 2) # 2 = height of the "hole" in the tile

                    xScreen = (self.terrainSurface.get_width() - self.width*self.scaleMultiplier*tileTotalWidthOriginal)/2 + self.terrainSurface.get_width() / 2 + (x-2) * (tileTotalWidthOriginal * self.scaleMultiplier) / 2 -  + y * (tileTotalWidthOriginal * self.scaleMultiplier) / 2
                    yScreen = y * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2 + x * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2 - height

                    # if the tile is outside the map, blit the border tile
                    if xTile < 0 or xTile >= self.Game.mapWidth or yTile < 0 or yTile >= self.Game.mapHeight:
                        self.terrainSurface.blit( self.borderTile, (xScreen, yScreen))
                        continue

                    textureIndex = self.getTerrainAt( xTile, yTile )

                    # if the tile should be highlighted, blit the highlight tile
                    if self.highlightedTile is not None and self.highlightedTile == (xTile, yTile):
                        self.terrainSurface.blit( self.borderTile, (xScreen, yScreen - ((tileTotalHeightOriginal * self.scaleMultiplier) / 2 - 2)), special_flags=pygame.BLEND_RGBA_ADD)
                        continue
                    
                    if(textureIndex == -1):
                        self.terrainSurface.blit( self.defaultTileAsset, (xScreen, yScreen))
                        continue

                    self.terrainSurface.blit( self.tilesAssets[ self.getTerrainAt( xTile , yTile ) ] , (xScreen, yScreen))
    
    def renderEntities(self, alpha):
        # Fill the surface with a transparent color
        self.bobSurface.fill((0,0,0,0))

        # Get all bobs in the grid sorted by their display coordinates
        sortedBobs = sorted(self.Game.grid.getAllBobs(), key=lambda bob: bob.sprite.displayY + bob.sprite.displayX)
        sortedEdibleObjects = sorted(self.Game.grid.getAllEdibleObjects(), key=lambda edible: edible.y + edible.x)


        # Draw each bob
        for bob in sortedBobs:
            self.drawBob(bob, alpha)

            # Draw the effects of the bob
            if Settings.enableEffects and bob.effects:
                self.drawEffects(bob, alpha)

            # If the bob is spitting, draw the projectile
            if bob.action == "spit":
                # If the bob doesn't have a projectile, create one
                if bob.sprite.projectile == None:
                    bob.sprite.projectile = Spittle(bob.currentX, bob.currentY, bob.target.currentX, bob.target.currentY, bob.sprite.size)
                self.drawProjectile(bob.sprite.projectile, alpha)
            else:
                bob.sprite.projectile = None


        # Iterate over each edible
        for edible in sortedEdibleObjects:
            self.drawEdible(edible)

    def render(self, alpha):

        self.screen.fill((0,0,0))

        if(self.mustReRenderTerrain):
            self.renderMap()
            self.mustReRenderTerrain = False

        self.renderEntities(alpha)

        self.screen.blit(self.terrainSurface, (self.xScreenOffset + (self.screenWidth - self.terrainSurface.get_width()) / 2, self.yScreenOffset))
        self.screen.blit(self.bobSurface, (self.xScreenOffset, self.yScreenOffset))

    def drawBob(self, b, alpha):
        # Update the display position of the bob
        b.sprite.updateDisplayPosition(alpha, self.Game.grid.size)

        # If animations are enabled, update the sprite and facing direction of the bob
        if Settings.enableAnimation:
            if b.action == "birth":
                # Set the bob sprite image to a blank image
                b.sprite.image = pygame.Surface((0,0), pygame.SRCALPHA)
            else:
                b.sprite.updateSprite(alpha, self.Game.paused, self.bobsAssets[b.action])
                b.sprite.updateFacingDirection()
        # Else, set a default sprite
        else:
            b.sprite.image = self.bobsAssets["eat"][1]

        # Calculate the bob's position relative to the world
        xTile = b.sprite.displayX - self.worldXoffset
        yTile = b.sprite.displayY - self.worldYoffset

        # Don't display entities outside the screen
        if xTile < 0 or xTile > self.width or yTile < 0 or yTile > self.height:
            return
        
        # Calculate the screen coordinates of the bob
        xScreen = (self.bobSurface.get_width() - self.width*self.scaleMultiplier*tileTotalWidthOriginal)/2 + self.bobSurface.get_width() / 2 + (xTile-2) * (tileTotalWidthOriginal * self.scaleMultiplier) / 2 -  + yTile * (tileTotalWidthOriginal * self.scaleMultiplier) / 2
        yScreen = (yTile-2) * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2 + xTile * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2

        # Scale the sprite based on the scale multiplier and the bob's size
        b.sprite.image = pygame.transform.scale(b.sprite.image, (int(tileTotalWidthOriginal * self.scaleMultiplier * b.sprite.size), int(tileTotalHeightOriginal * self.scaleMultiplier * b.sprite.size)))

        if Settings.computeColorSprite:
            b.sprite.applyColor()
            
        if b.jobProperty == Network.uuid_player:
            b.sprite.highlight()

        # Adjust the screen coordinates to center the bob on the tile
        xScreen += (tileTotalWidthOriginal * self.scaleMultiplier) / 2 - b.sprite.image.get_width() / 2
        yScreen += (tileTotalHeightOriginal * self.scaleMultiplier) * 52/60 - b.sprite.image.get_height() * 52/60

        # Calculate the height of the bob
        height = self.getHeightAt(xTile, yTile) * ((tileTotalHeightOriginal * self.scaleMultiplier) / 2 - 2) # 2 = height of the "hole" in the tile

        # Draw the sprite on the surface
        self.bobSurface.blit(b.sprite.image, (xScreen, yScreen - height))

        if self.Game.followBestBob and b == self.Game.currentBestBob:
            # Draw a hitbox around the bob
            pygame.draw.rect(self.bobSurface, (255, 0, 0), (xScreen, yScreen - height, b.sprite.image.get_width(), b.sprite.image.get_height()), 1)

    def drawProjectile(self, projectile, alpha):

        # Update the display position of the projectile
        projectile.updateProjectilePosition(alpha, self.Game.grid.size)

        # Draw the projectile if the bob is spitting
        if alpha > 0.5:

            alpha = 2 * (alpha - .5)

            # Scale the sprite based on the tile size and make it half the original size
            projectileSprite = pygame.transform.scale(projectile.image, (int(tileTotalWidthOriginal * self.scaleMultiplier * projectile.size / 2), int(tileTotalHeightOriginal * self.scaleMultiplier * projectile.size / 2)))

            # Calculate the projectile position relative to the world
            xTile = projectile.displayX - self.worldXoffset
            yTile = projectile.displayY - self.worldYoffset

            # Calculate the screen coordinates of the projectile
            xScreen = (self.terrainSurface.get_width() - self.width*self.scaleMultiplier*tileTotalWidthOriginal)/2 + self.terrainSurface.get_width() / 2 + (xTile-2) * (tileTotalWidthOriginal * self.scaleMultiplier) / 2 -  + yTile * (tileTotalWidthOriginal * self.scaleMultiplier) / 2
            yScreen = (yTile-2) * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2 + xTile * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2

            # Adjust the screen coordinates to center the projectile on the tile
            xScreen += (tileTotalWidthOriginal * self.scaleMultiplier) / 2 - projectileSprite.get_width() / 2
            yScreen += (tileTotalHeightOriginal * self.scaleMultiplier) / 2 - projectileSprite.get_height() / 2

            # Calculate the height of the projectile
            height = self.getHeightAt(xTile, yTile) * ((tileTotalHeightOriginal * self.scaleMultiplier) / 2 - 2)

            # Draw the projectile on the surface
            self.bobSurface.blit(projectileSprite, (xScreen, yScreen - height))

    def drawEffects(self, b, alpha):
        # Calculate the bob position relative to the world
        xTile = b.sprite.displayX - self.worldXoffset
        yTile = b.sprite.displayY - self.worldYoffset

        for effect in b.effects:
            # Only display the effect if it has been applied
            if effect.remainingDuration == effect.duration - 1 or effect.remainingDuration <= 0:
                continue

            # Update the sprite for each effect
            if effect.name == "superMutation" or effect.name == "powerCharged":
                effect.sprite.image = self.effectsAssets[effect.name]
            else:
                effect.sprite.updateSprite(alpha, self.Game.paused, self.effectsAssets[effect.name])

            # Calculate the scale factor to fit the effect within the mass of the bob
            scaleFactor = b.sprite.size / 2

            # Scale the effect sprite based on the tile size and the scale factor
            effectSprite = pygame.transform.scale(effect.sprite.image, (int(tileTotalWidthOriginal * self.scaleMultiplier * scaleFactor), int(tileTotalHeightOriginal * self.scaleMultiplier * scaleFactor)))

            # Calculate the screen coordinates of the effect
            xScreen = (self.bobSurface.get_width() - self.width*self.scaleMultiplier*tileTotalWidthOriginal)/2 + self.bobSurface.get_width() / 2 + (xTile-2) * (tileTotalWidthOriginal * self.scaleMultiplier) / 2 -  + yTile * (tileTotalWidthOriginal * self.scaleMultiplier) / 2
            yScreen = (yTile-2) * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2 + xTile * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2

            # Adjust the screen coordinates to center the effect on the tile
            xScreen += (tileTotalWidthOriginal * self.scaleMultiplier) / 2 - effectSprite.get_width() / 2
            yScreen += (tileTotalHeightOriginal * self.scaleMultiplier) / 2 - effectSprite.get_height() / 2 - b.sprite.image.get_height() / 4

            # Draw the effect on the surface
            self.bobSurface.blit(effectSprite, (xScreen, yScreen))

            # Update the xScreen for the next effect
            xScreen += effectSprite.get_width()

    def drawEdible(self, edible):
        # Calculate the edible's position relative to the world
        xTile = edible.x - self.worldXoffset
        yTile = edible.y - self.worldYoffset

        # Don't display entities outside the screen
        if xTile < 0 or xTile > self.width or yTile < 0 or yTile > self.height:
            return

        # Calculate the screen coordinates of the edible
        xScreen = (self.bobSurface.get_width() - self.width*self.scaleMultiplier*tileTotalWidthOriginal)/2 + self.bobSurface.get_width() / 2 + (xTile-2) * (tileTotalWidthOriginal * self.scaleMultiplier) / 2 -  + yTile * (tileTotalWidthOriginal * self.scaleMultiplier) / 2
        yScreen = (yTile-2) * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2 + xTile * (tileVisibleHeightOriginal * self.scaleMultiplier) / 2

        # If the edible is a food, choose the food sprite based on the amount of food
        if isinstance(edible, Food):
            if isinstance(edible, EffectFood):
                if isinstance(edible.effect, SuperMutation):
                    foodSprite = self.edibleAssets["mutant-pizza"] if self.Game.grid.getFoodValueAt(xTile, yTile) > 50 else self.edibleAssets["mutant-croissant"]
                elif isinstance(edible.effect, PowerCharged):
                    foodSprite = self.edibleAssets["powerade"]
            else:
                foodSprite = self.edibleAssets["pizza"] if self.Game.grid.getFoodValueAt(xTile, yTile) > 50 else self.edibleAssets["croissant"]
        
        # Else if the edible is a Sausage, choose the sausage sprite
        elif isinstance(edible, Sausage):
            foodSprite = self.edibleAssets["sausage"]

        # Scale the sprite based on the tile size
        foodSprite = pygame.transform.scale(foodSprite, (int(tileTotalWidthOriginal * self.scaleMultiplier), int(tileTotalHeightOriginal * self.scaleMultiplier)))

        # Calculate the height of the edible
        height = self.getHeightAt(xTile, yTile) * ((tileTotalHeightOriginal * self.scaleMultiplier) / 2 - 2) # 2 = height of the "hole" in the tile

        # Draw the sprite on the surface
        self.bobSurface.blit(foodSprite, (xScreen, yScreen - height))

    def getCoordsFromPosition(self, xScreen, yScreen):

        xScreen -= self.screen.get_width() / 2

        # Calculate the position of the mouse relative to the map
        xMap = (xScreen - self.xScreenOffset - (self.screenWidth - self.terrainSurface.get_width()) / 2) / (tileTotalWidthOriginal * self.scaleMultiplier)
        yMap = (yScreen - self.yScreenOffset) / (tileVisibleHeightOriginal * self.scaleMultiplier)

        xMap *= 2
        yMap *= 2

        # Calculate the position of the mouse relative to the grid
        xGrid = (xMap + yMap) // 2 + self.worldXoffset
        yGrid = (yMap - xMap) // 2 + self.worldYoffset

        if xGrid < 0 or xGrid >= self.Game.mapWidth or yGrid < 0 or yGrid >= self.Game.mapHeight:
            
            if not self.highlightedTile == None:
                self.mustReRenderTerrain = True
            
            self.highlightedTile = None
            return None

        if not self.highlightedTile == (xGrid, yGrid):
            self.mustReRenderTerrain = True

        self.highlightedTile = (xGrid, yGrid)

        return xGrid, yGrid
