import pygame
from backend.Settings import *

class Sprite:
    def __init__(self, size=1):
        self.size = size
        self.currentSprite = 0
        self.image = None

    # Update the sprite's image
    def updateSprite(self, alpha, paused, spriteSheet):
        """
        alpha: float between 0 and 1, used to select the sprite to display
        paused: boolean, if true, the sprite will not change
        spriteSheet: list containing the sprites
        """
        # If alpha is not between 0 and 1, set it to the correct value to avoid potential errors
        alpha %= 1

        if not Settings.enableAnimation:
            self.image = spriteSheet[4]

        # Select the sprite based on the alpha value
        if not paused:
            self.currentSprite = int(alpha * (len(spriteSheet) - 1))

        # Select the current sprite
        image = spriteSheet[self.currentSprite]

        self.image = image

    
class BobSprite(Sprite):
    def __init__(self, bob):
        super().__init__(pow(bob.mass, 1/3))
        self.displayX, self.displayY = bob.currentX, bob.currentY
        self.bob = bob
        self.directionFacing = "right"
        self.projectile = None

       # get the sprite to display

    # Update the sprite's facing direction
    def updateFacingDirection(self):
        dx = self.bob.currentX - self.bob.lastX
        dy = self.bob.currentY - self.bob.lastY

        # If the bob is facing left (x+ is down right, y+ is down left), set the bob's facing direction
        if Settings.enableAnimation:
            if (dx < 0 and dx < dy) or (dy > 0 and dy >= dx):
                self.directionFacing = "left"
            else:
                self.directionFacing = "right"

    # Update the bob's sprite's display position
    def updateDisplayPosition(self, alpha, gridSize):

        # If smooth movement is disabled, set the display position to the logical current position
        if not Settings.enableSmoothMovement:
            self.displayX, self.displayY = self.bob.currentX, self.bob.currentY
            return

        lastX, lastY = self.bob.lastX, self.bob.lastY
        currentX, currentY = self.bob.currentX, self.bob.currentY

        self.size = pow(self.bob.mass, 1/3)


        if Settings.donut:
            # If the Bob crossed the border, update its display position
            if abs(lastX - currentX) > gridSize / 2:
                if lastX < currentX:
                    lastX += gridSize
                else:
                    currentX += gridSize

            if abs(lastY - currentY) > gridSize / 2:
                if lastY < currentY:
                    lastY += gridSize
                else:
                    currentY += gridSize

        # Interpolate the display position
        newX, newY = (1 - alpha) * lastX + alpha * currentX, (1 - alpha) * lastY + alpha * currentY

        # Update the display position
        self.displayX, self.displayY = newX % gridSize, newY % gridSize

    # aply a color to the current image of the bob depending on the velocity, the perception and the memory
    def applyColor(self):
        # Get the current image
        image = self.image.copy()

        # Get the color to apply
        color = self.calculateColor()

        image.fill((200,200,200) , special_flags=pygame.BLEND_SUB)

        # Apply the color
        image.fill(color, special_flags=pygame.BLEND_ADD)

        # Set the image
        self.image = image
        
    
    def highlight(self):
        image = self.image.copy()
        image.fill((90,70,150), special_flags=pygame.BLEND_ADD)
        self.image = image

    
    def calculateColor(self):
            # Calculate the r, g, b color depending on the velocity, perception, and memory
            r = int(min(self.bob.velocity * Settings.velocityFactor,255))
            g = int(min(self.bob.perception * Settings.perceptionFactor,255))
            b = int(min(self.bob.memorySize * Settings.memoryFactor,255))

            # Return the color
            return (r,g,b)

class EffectSprite(Sprite):
    def __init__(self, effect):
        super().__init__()
        self.effect = effect