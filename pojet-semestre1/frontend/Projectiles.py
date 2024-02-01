import pygame
from backend.Settings import Settings

class Projectile():
    def __init__(self, originX, originY, targetX, targetY, size=1):
        self.originX, self.originY = originX, originY
        self.targetX, self.targetY = targetX, targetY
        self.displayX, self.displayY = originX, originY
        self.size = size

      # Update the projectile's display position
    def updateProjectilePosition(self, alpha, gridSize):

        alpha = 2 * (alpha - .5)
        if alpha < 0:
            return

        originX, originY = self.originX, self.originY
        targetX, targetY = self.targetX, self.targetY

        if Settings.donut:
            # If the Bob crossed the border, update its display position
            if abs(originX - targetX) > gridSize / 2:
                if originX < targetX:
                    originX += gridSize
                else:
                    targetX += gridSize

            if abs(originY - targetY) > gridSize / 2:
                if originY < targetY:
                    originY += gridSize
                else:
                    targetY += gridSize

        newX, newY = (1 - alpha) * originX + alpha * targetX, (1 - alpha) * originY + alpha * targetY

        # Update the display position
        self.displayX, self.displayY = newX % gridSize, newY % gridSize

class Spittle(Projectile):
    def __init__(self, originX, originY, targetX, targetY, size=1):
        super().__init__(originX, originY, targetX, targetY, size)

        self.image = pygame.image.load("assets/hot-dog.png")