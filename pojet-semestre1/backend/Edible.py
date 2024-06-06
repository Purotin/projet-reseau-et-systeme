from backend.Settings import Settings
from backend.Effect import *
from multi.network import Network
import uuid


class Edible:
    def __init__(self, x, y, value=0, ID = None, Nproperty = None, Jproperty = None):
        self.x = x
        self.y = y
        self.value = value
        self.networkProperty = Nproperty if not Nproperty is None else Network.uuid_player
        self.id = ID if not ID is None else uuid.uuid4()
        self.jobProperty = Jproperty if not Jproperty is None else Network.uuid_player

class Food(Edible):
    def __init__(self, x, y, energy=Settings.spawnedFoodEnergy, ID = None, Nproperty = None, Jproperty = None):
        super().__init__(x, y, energy, ID, Nproperty, Jproperty)

class EffectFood(Food):
    def __init__(self, x, y, energy=Settings.spawnedFoodEnergy, effect=None):
        super().__init__(x, y, energy)
        self.effect = effect

class PoisonnedFood(Food):
    pass

class Sausage(Edible):
    def __init__(self, x, y, ammos=Settings.spawnSausagesAmmos):
        super().__init__(x, y, ammos)
