import tkinter as tk
from tkinter import ttk

import os
import pickle

from backend.Settings import Settings

class SettingsWindow(tk.Tk):
    def __init__(self, createSaveFile, loadSaveFile):
        tk.Tk.__init__(self)

        # Set the initial theme
        self.tk.call("source", "assets/azure.tcl")
        self.tk.call("set_theme", "dark")

        # self.geometry('700x400')
        self.title('Settings')
        
        self.createSaveFile = createSaveFile
        self.loadSaveFile = loadSaveFile

        self.constantsVars = {}

        self.initMainNotebook()

        self.addFeaturesFrame()
        self.addConstantsFrame()
        self.addLoadSaveFrame()
        self.addShortcutsFrame()

        self.mainloop()

    def initMainNotebook(self):

        # create a notebook
        self.mainNotebook = ttk.Notebook(self)
        self.mainNotebook.pack(expand=True, fill="both", padx=10, pady=10)

        # create frames
        self.featuresFrame = ttk.Frame(self.mainNotebook, width=700, height=500)
        self.constantsFrame = ttk.Frame(self.mainNotebook, width=700, height=500)
        self.loadSaveFrame = ttk.Frame(self.mainNotebook, width=700, height=500)

        # add frames to notebook
        self.mainNotebook.add(self.featuresFrame, text='Features')
        self.mainNotebook.add(self.constantsFrame, text='Constants')
        self.mainNotebook.add(self.loadSaveFrame, text='Load/Save')


    def addFeaturesFrame(self):

        features = {
            "enableFeed" : "Food and eat mechanism",
            "enablePerception" : "Perception",
            "enableMovement": "Movement",
            "enableEnergyConsumption": "Energy consumption",
            "enableMemory": "Memory",
            "enableMass": "Mass",
            "enableVelocity": "Velocity",
            "enableSmoothMovement": "Smooth movement",
            "donut": "Map borders",
            "enableAnimation": "Animations",
            "computeColorSprite": "Colored sprites",
            "enableEffects": "Effects",
            "enableSpitting": "Spitting",
            "enableSexualReproduction": "Reproduction",
            "enableParthenogenesis": "Parthenogenesis",
            "enableNoise": "Noise (terrain & height)",
            "enableMutation": "Mutation",
            "enableMutantFood": "Mutant food",
            "enableIsotonicDrinks": "Isotonic drinks",
            "enableMassMaxEnergy": "Mass max energy"
        }

        row = 0
        column = 0
        for feature, label in features.items():
            setattr(self, feature, tk.BooleanVar(value=Settings.getSetting(feature)))

            toggle_button = ttk.Checkbutton(self.featuresFrame, text=label, variable=getattr(self, feature), command=lambda f=feature: self.toggleFeature(f))
            toggle_button.grid(row=row, column=column, padx=10, pady=10, sticky="w")
            
            column += 1
            if column == 4:
                column = 0
                row += 1
        
                                      
    def toggleFeature(self, feature):
        Settings.setSetting(feature, not Settings.getSetting(feature))
        print("Toggled feature " + feature + " to " + str(Settings.getSetting(feature)))

    
    def addConstantsFrame(self):
        constants = {
            "Time": {
                "dayLength": { "name": "Day length (ticks)", "increment": 1 },
                "maxTps": { "name": "Max ticks per second", "increment": 1 },
                "maxFps": { "name": "Max frames per second", "increment": 1 }
            },
            "Energy": {
                "spawnEnergy": { "name": "Spawn energy", "increment": 1 },
                "energyMax": { "name": "Max energy", "increment": 1 },
                "motherEnergy": { "name": "Mother energy", "increment": 1 },
                "matingEnergyConsumption": { "name": "Mating energy consumption", "increment": 1 },
                "matingEnergyRequirement": { "name": "Mating energy requirement", "increment": 1 },
                "tickMinEnergyConsumption": { "name": "Tick min energy consumption", "increment": 1 },
                "spawnedFoodEnergy": { "name": "Spawned food energy", "increment": 1 },
            },
            "Velocity": {
                "spawnVelocity": { "name": "Spawn velocity", "increment": 0.1 },
                "minVelocity": { "name": "Min velocity", "increment": 0.1 },
            },
            "Mass": {
                "spawnMass": { "name": "Spawn mass", "increment": 0.1 },
                "minMass": { "name": "Min mass", "increment": 0.1 },
                "massRatioThreshold": { "name": "Mass ratio threshold", "increment": 0.1 },
            },
            "Vision": {
                "spawnPerception": { "name": "Spawn perception", "increment": 1 },
                "preyFactor": { "name": "Prey factor", "increment": 1 },
                "predatorFactor": { "name": "Predator factor", "increment": 1 },
                "foodFactor": { "name": "Food factor", "increment": 1 },
            },
            "Memory": {
                "spawnMemory": { "name": "Spawn memory", "increment": 1 },
            },
            "Mutation": {
                "velocityMutation": { "name": "Velocity mutation", "increment": 0.1 },
                "massMutation": { "name": "Mass mutation", "increment": 0.1 },
                "perceptionMutation": { "name": "Perception mutation", "increment": 1 },
                "memoryMutation": { "name": "Memory mutation", "increment": 1 },
                "pBirthEnergy": { "name": "Birth energy mutation", "increment": 1 },
                "sBirthEnergy": { "name": "Birth energy mutation", "increment": 1 },
            },
            "Spitting": {
                "spawnAmmos": { "name": "Spawn ammos", "increment": 1 },
                "spawnMaxAmmos": { "name": "Max ammos", "increment": 1 },
                "spawnSausagesAmmos": { "name": "Spawn sausages ammos", "increment": 1 },
            },
            "Colors": {
                "velocityFactor": { "name": "Velocity factor", "increment": 1 },
                "perceptionFactor": { "name": "Perception factor", "increment": 1 },
                "memoryFactor": { "name": "Memory factor", "increment": 1 },
            }
        }

        # create a notebook
        self.constantsNotebook = ttk.Notebook(self.constantsFrame)
        self.constantsNotebook.pack(expand=True, fill="both", padx=10, pady=10)

        row = 0
        column = 0
        for category, subcategories in constants.items():
            
            setattr(self, category, ttk.Frame(self.constantsNotebook, width=650, height=450))
            self.constantsNotebook.add(getattr(self, category), text=category)
            
            innercol = 0
            for subcategory, c in subcategories.items():

                self.constantsVars[subcategory] = tk.DoubleVar(value=Settings.getSetting(subcategory))

                label = ttk.Label(getattr(self, category), text=c["name"])
                label.grid(row=row, column=innercol, padx=10, pady=0, sticky="w")

                spinbox = ttk.Spinbox(getattr(self, category), from_=-100000, to=100000, increment=c['increment'], textvariable=self.constantsVars[subcategory], command=lambda s=subcategory: self.changeConstant(s))
                spinbox.grid(row=row+1, column=innercol, padx=10, pady=10, sticky="w")

                innercol += 1
                if innercol == 3:
                    innercol = 0
                    row += 2

            row = 0
            column += 2
    

    def changeConstant(self, constantName):
        Settings.setSetting(constantName, self.constantsVars[constantName].get())
        print("Changed constant " + constantName + " to " + str(Settings.getSetting(constantName)))

    def addLoadSaveFrame(self):

        scrollbar = ttk.Scrollbar(self.loadSaveFrame)
        scrollbar.pack(side="right", fill="y")

        widget = ttk.Treeview(self.loadSaveFrame, yscrollcommand=scrollbar.set, selectmode="browse")
        widget.pack(expand=True, fill="both", padx=10, pady=10, side="left")
        scrollbar.config(command=widget.yview)
        
        files = [f for f in os.listdir("saves") if os.path.isfile(os.path.join("saves", f)) and f.endswith(".save")]

        widget.heading("#0", text=f"{len(files)} saves found")

        # find all files ending with .save that are in the saves folder
        for f in files:
            
            # load file with pickle to check version
            with open(os.path.join("saves", f), 'rb') as saveFile:

                try:
                    data = pickle.load(saveFile)
                except:
                    data = None
                
                isOldVersion = data is None or not 'version' in data['settings'] or data['settings']['version'] != Settings.version
                widget.insert("", "end", text=f"{f}{' - May be incompatible' if isOldVersion else ''}", tags=('oldVersion',) if isOldVersion else ())

        
        # When double clicking on a save, load it
        widget.bind("<Double-1>", lambda _: self.loadButton(widget))
        
        # When suppr + clicking on a save, delete it
        widget.bind("<Delete>", lambda _: self.deleteButton(widget))

        widget.tag_configure('oldVersion', foreground='red')

        a = ttk.Button(self.loadSaveFrame, text ="Load", command = lambda: self.loadButton(widget))
        b = ttk.Button(self.loadSaveFrame, text ="Save", command = lambda: self.saveButton(widget))
        c = ttk.Button(self.loadSaveFrame, text ="Delete", command = lambda: self.deleteButton(widget))

        a.pack(padx=10, pady=10)
        b.pack(padx=10, pady=10)
        c.pack(padx=10, pady=10)
    
    def saveButton(self, treeview):
        saveName = self.createSaveFile()
        treeview.insert("", "end", text=saveName)

        files = [f for f in os.listdir("saves") if os.path.isfile(os.path.join("saves", f)) and f.endswith(".save")]

        treeview.heading("#0", text=f"{len(files)} saves found")
    
    def loadButton(self, treeview):
        selectedItems = treeview.selection()

        if len(selectedItems) == 0:
            return

        selected = treeview.item(selectedItems[0])['text']

        # if text ends with " - May be incompatible", remove it
        if selected.endswith(" - May be incompatible"):
            selected = selected[:-len(" - May be incompatible")]

        loadSuccess = self.loadSaveFile(os.path.join("saves", selected))

        if loadSuccess:
            self.destroy()
            self.quit()
        else:
            print("Error while loading save file")
            exit()

    def deleteButton(self, treeview):
        selectedItems = treeview.selection()

        if len(selectedItems) == 0:
            return

        selected = treeview.item(selectedItems[0])['text']

        # if text ends with " - May be incompatible", remove it
        if selected.endswith(" - May be incompatible"):
            selected = selected[:-len(" - May be incompatible")]

        os.remove(os.path.join("saves", selected))
        treeview.delete(selectedItems[0])

        files = [f for f in os.listdir("saves") if os.path.isfile(os.path.join("saves", f)) and f.endswith(".save")]
        treeview.heading("#0", text=f"{len(files)} saves found")

    def addShortcutsFrame(self):
        shortcuts = {
            "escape": "Display pause menu",
            "p": "Pause/unpause",
            "r": "Toggle rendering",
            "h": "Toggle height",
            "t": "Toggle textures",
            "s": "Toggle overlay",
            "o": "Population charts",
            "": "",
            "scroll": "Zoom in/out",
            "click and drag": "Move camera",
            "EDITOR_MODE: left click": "Add",
            "EDITOR_MODE: right click": "Remove",
        }

        # help menu just to display the available shortcuts
        self.shortcutsFrame = ttk.Frame(self.mainNotebook, width=700, height=500)
        self.mainNotebook.add(self.shortcutsFrame, text='Shortcuts')

        row = 0
        column = 0

        for shortcut, label in shortcuts.items():
            ttk.Label(self.shortcutsFrame, text=shortcut).grid(row=row, column=column, padx=10, pady=0, sticky="w")
            ttk.Label(self.shortcutsFrame, text=label).grid(row=row, column=column+1, padx=10, pady=0, sticky="w")

            row += 1
            if row == 12:
                row = 0
                column += 2

        