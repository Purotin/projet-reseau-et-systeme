from frontend.Sprite import *

class Effect:
    def __init__(self, duration):
        self.duration = duration
        self.remainingDuration = duration
        self.sprite = EffectSprite(self)

    def applyEffect(self, b):
        pass

    def __getstate__(self):
        state = self.__dict__.copy()

        del state['sprite']
        
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.sprite = EffectSprite(self)

class SpittedAt(Effect):
    def __init__(self, duration=5, slowness=.5, blindness=.5):
        super().__init__(duration)
        self.name = "spittedAt"
        self.slowness = slowness
        self.blindness = blindness

    def __str__(self):
        return "S"

    def applyEffect(self, b):
        """
        Apply the effect to a bob.

        Args:
            b (Bob): The Bob object to apply the effect to.
        """
        # Update the remaining duration
        self.remainingDuration -= 1

        # Apply the effect if it is the first turn
        if self.remainingDuration == self.duration - 1:
            self.originalVelocity = b.velocity
            self.originalVelocityBuffer = b.velocityBuffer
            self.originalPerception = b.perception
            b.velocity = int(b.velocity * self.slowness)
            b.velocityBuffer = b.velocityBuffer * self.slowness
            b.perception = b.perception * self.blindness
        
        # Remove the effect and restore the original attributes if the effect is over
        elif self.remainingDuration <= 0:
            b.velocity = self.originalVelocity
            b.velocityBuffer = self.originalVelocityBuffer
            b.perception = self.originalPerception
            b.effects.remove(self)

# SuperMutation effect triggered when eating a mutant food
class SuperMutation(Effect):
    def __init__(self):
        super().__init__(1)
        self.name = "superMutation"
        self.mutationBoost = 3

    # Apply the effect
    def applyEffect(self, b):
        b.mutationFactor += self.mutationBoost

# PowerCharged effect triggered when eating a power food
class PowerCharged(Effect):
    def __init__(self, duration=100):
        super().__init__(duration)
        self.name = "powerCharged"
        self.consumptionFactor = .5

    def applyEffect(self, b):
        if self.remainingDuration == self.duration:
            b.consumptionFactor *= self.consumptionFactor

        self.remainingDuration -= 1

        if self.remainingDuration <= 0:
            b.consumptionFactor /= self.consumptionFactor
            b.effects.remove(self)

    