import matplotlib.pyplot as plt
import numpy as np

class DisplayStatsChart:
    def __init__(self, tickCount, bobCountHistory, bestBobGenerationHistory):
        self.bobCountHistory = bobCountHistory
        self.bestBobGenerationHistory = bestBobGenerationHistory

        self.time = np.linspace(0, tickCount, tickCount)

        print("TickCount: " + str(tickCount))
        print("len BobCountHistory: " + str(len(bobCountHistory)))
        print("len BestBobGenerationHistory: " + str(len(bestBobGenerationHistory)))

        self.render()

    def render(self):
        # Définir la taille de la fenêtre
        plt.figure(figsize=(12, 6))  # largeur de 12 pouces, hauteur de 6 pouces

        # Créer une fenêtre avec deux sous-graphiques (1 ligne, 2 colonnes)
        plt.subplot(1, 2, 1)
        plt.plot(self.time, self.bobCountHistory)
        plt.title('Evolution du nombre de bobs au fil du temps')

        plt.subplot(1, 2, 2)
        plt.plot(self.time, self.bestBobGenerationHistory)
        plt.title('Génération du bob le plus vieux en fonction du temps')

        # Ajuster l'espacement entre les sous-graphiques
        plt.tight_layout()

        # Afficher la fenêtre avec les deux sous-graphiques
        plt.show()
