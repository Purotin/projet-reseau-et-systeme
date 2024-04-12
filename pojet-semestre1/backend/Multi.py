import pickles


def udpdateData(data, grid):
        with open(data, 'rb') as f:
            try:
                data = pickle.load(f)
            except:
                print("Error while loading save file")
                return False
            
        grid_copy = grid.copy()
            
        for key, cell in grid_copy:
            if cell.bobs:
                for bob in cell.bobs:
                    if bob.id in data:
                        #update bob data
                        if data[bob.id]['position']:
                            bob.lastX = bob.currentX
                            bob.lastY = bob.currentY
                            bob.currentX = data[bob.id]['position'][0]
                            bob.currentY = data[bob.id]['position'][1]
                        bob.energy = data[bob.id]['energy'] if data[bob.id]['energy'] else bob.energy
                        pass

            elif cell.edibleObject:
                if cell.edibleObject.id in data:
                    if data[cell.edibleObject.id]['position']:
                        cell.edibleObject.x = data[cell.edibleObject.id]['position'][0]
                        cell.edibleObject.y = data[cell.edibleObject.id]['position'][1]
                    cell.edibleObject.value = data[cell.edibleObject.id]['value'] if data[cell.edibleObject.id]['value'] else cell.edibleObject.value
                    pass

        return grid_copy


            # {"id_bob" : {"position" : x , "value" : x}}