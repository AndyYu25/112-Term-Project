#File contains all buildings and their associated attributes/methods
from cmu_112_graphics import *
class building:
    def __init__(self, cost, row, col, name=None):
        self.cost = cost
        self.row, self.col = row, col
        self.name = name
    
    def getInfo(self):
        return self.cost, self.row, self.col, self.name

class capital(building):
    def __init__(self, row, col):
        super().__init__(0, row, col, 'capital')
    def render(self, canvas, cx, cy, radius):
        capitalSize = (radius*0.8, radius*0.6)
        #list of points that make up the capital building. Each row corresponds
        #to a point
        points = [cx - capitalSize[0]/2, cy + capitalSize[1]/2,
                  cx - capitalSize[0]/2, cy - capitalSize[1]/2,
                  cx - capitalSize[0]/4, cy - capitalSize[1]/2,
                  cx - capitalSize[0]/4, cy - capitalSize[1]/3,
                  cx + capitalSize[0]/5, cy - capitalSize[1]/3,
                  cx + capitalSize[0]/5, cy - capitalSize[1] * 2/3,
                  cx + capitalSize[0]/2, cy - capitalSize[1] * 2/3,
                  cx + capitalSize[0]/2, cy + capitalSize[1]/2]
        canvas.create_polygon(*points, fill='black')
class levee(building):
    def __init__(self, row, col):
        leveeCost = 20
        self.heightChange = 1
        super().__init__(leveeCost, row, col, 'levee')
    
    def changeBuildingHeight(self, buildingHeight):
        buildingHeight += self.heightChange

    def render(self, canvas, cx, cy, radius):
        leveeSize = (radius*0.8, radius*0.6)
        #list of points that make up the capital building. Each row corresponds
        #to a point
        points = [cx - leveeSize[0]/3, cy - leveeSize[1]/2,
                  cx + leveeSize[0]/3, cy - leveeSize[1]/2,
                  cx + leveeSize[0]/2, cy + leveeSize[1]/2, 
                  cx - leveeSize[0]/2, cy + leveeSize[1]/2]
        canvas.create_polygon(*points, fill='black')

class ditch(building):
    def __init__(self, row, col):
        ditchCost = 20
        self.heightChange = -1
        super().__init__(ditchCost, row, col, 'ditch')
    
    def changeBuildingHeight(self, buildingHeight):
        buildingHeight += self.heightChange

    def render(self, canvas, cx, cy, radius):
        ditchRadius, outlineWidth = radius * 0.4, radius * 0.05
        canvas.create_arc(cx-ditchRadius, cy, cx+ditchRadius, 
            cy+ditchRadius,outline = 'black',
            style='arc',extent=-180,width=outlineWidth)

class dam(building):
    def __init__(self, row, col):
        """dams funnel a proportional amount of water through the tile
        and rise to the height of the greatest adjacent edge"""
        self.height = 0
        self.damIntake, self.damOutput = None, None
        damCost = 40
        super().__init__(damCost, row, col, 'dam')


    def render(self, canvas, cx, cy, radius):
        damWidth, damYOffset = radius*0.4, radius * 0.2
        damOutline = radius * 0.1
        canvas.create_line(cx-damWidth, cy-damYOffset,
                           cx+damWidth, cy-damYOffset, width=damOutline)
        canvas.create_line(cx-damWidth, cy+damYOffset,cx+damWidth, 
                           cy+damYOffset, width=damOutline)
        