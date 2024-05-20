from backend.Settings import Settings
from backend.Effect import *
from backend.Multi import *


class Edible:
    def __init__(self, x, y, value=0):
        self.x = x
        self.y = y
        self.value = value
        self.network_properties = Network.uuid_player
        self.id = uuid.uuid4()
        self.job_properties = Network.uuid_player

class Food(Edible):
    def __init__(self, x, y, energy=Settings.spawnedFoodEnergy):
        super().__init__(x, y, energy)

class EffectFood(Food):
    def __init__(self, x, y, energy=Settings.spawnedFoodEnergy, effect=None):
        super().__init__(x, y, energy)
        self.effect = effect

class PoisonnedFood(Food):
    pass

class Sausage(Edible):
    def __init__(self, x, y, ammos=Settings.spawnSausagesAmmos):
        super().__init__(x, y, ammos)
