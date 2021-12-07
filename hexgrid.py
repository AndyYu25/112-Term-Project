
import waterflow as flow
import building as bldg
import copiedCode as cited
import isometric as iso
#python builtin module
import math
import random
#graphics framework from https://www.diderot.one/course/34/chapters/2847/
from cmu_112_graphics import *

#file contains hexgrird and hex class, along with helper functions

def drawHexagon(canvas, radius, cx, cy, color, outline):
    """draws a regular hexagon with the given parameters
    Flat side is on top. Radius is distance from center to any 1 point
    Example:
     C B
    D   A
     E F
    """
    dy = radius * (3**0.5)/2
    #the 2 lists are all possible x or y coordinates for the hexagonal points
    yCoords = [cy, cy+dy, cy-dy]
    xCoords = [cx+radius, cx-radius, cx+radius/2, cx-radius/2]
    canvas.create_polygon(xCoords[0], yCoords[0], 
                          xCoords[2], yCoords[2], 
                          xCoords[3], yCoords[2],
                          xCoords[1], yCoords[0],
                          xCoords[3], yCoords[1],
                          xCoords[2], yCoords[1],
                          fill=color, outline = outline)

def renderVectorArrow(canvas, x1, y1, angle, length, thickness, arrowheadSize, hexRadius):
    """draws an arrow emanating from x1, y1 at the specified angle 
    (0 degrees is pointing directly to the right of the screen and
    angle goes counterclockwise) with the specified thickness. Angle 
    is in degrees. arrowheadSize determines the size of the arrowhead"""
    #easier to work in degrees since 360 is easily divisible by 6
    #convert to radians
    if length > hexRadius:
        length = hexRadius
    angle = -angle * math.pi/180
    x2 = x1 + (hexRadius/3 + length/2) * math.cos(angle)
    y2 = y1 + (hexRadius/3 + length/2) * math.sin(angle)
    #offset x1, y1 for aesthetic reasons
    x1 = x1 + hexRadius/3 * math.cos(angle)
    y1 = y1 + hexRadius/3 * math.sin(angle)
    arrowhead = (8*arrowheadSize, 10*arrowheadSize, 3*arrowheadSize)
    canvas.create_line(x1, y1, x2, y2, arrow=LAST, width = thickness)

def drawStar(canvas, cx, cy, color, radius):
    """draws a 5-pointed star with the specified radius (the size of the tips),
    color, and center"""
    points = []
    for point in range(0, 10): #loop finds all points for a star
        angle = math.pi/10 + math.pi/5 * point 
        #there are 10 evenly spaced points in a 5-pointed star
        if point % 2 == 1: #the farther points
            dx, dy = radius * math.cos(angle), radius * math.sin(angle)
        else: dx, dy = radius/2 * math.cos(angle), radius/2 * math.sin(angle)
        points.extend([cx + dx, cy + dy])
    canvas.create_polygon(*points, fill=color)

def drawHexPrism(canvas, landHeight,waterHeight,buildingHeight, cx, cy, hexRadius,landColor,waterColor):
    """draws isometric hexagonalPrisms"""
    dy = hexRadius * (3**0.5)/2
    totalHeight = sum([landHeight,waterHeight,buildingHeight])
    yCoords = [cy, cy+dy, cy-dy]
    xCoords = [cx+hexRadius, cx-hexRadius, cx+hexRadius/2, cx-hexRadius/2]
    points = [[xCoords[0], yCoords[0]], 
            [xCoords[2], yCoords[2]], 
            [xCoords[3], yCoords[2]],
            [xCoords[1], yCoords[0]],
            [xCoords[3], yCoords[1]],
            [xCoords[2], yCoords[1]]]
    if buildingHeight < 0: #ditches won't have a gray color, just decrease the land height
        landHeight -= 1
        buildingHeight = 0
    landPrismCenter, landZOffset = (cx, cy), 0
    iso.isometricPrism(canvas, points,landPrismCenter,-landHeight*10,color=landColor, zOffset=landZOffset)
    if waterHeight != 0:
        waterPrismCenter = (cx, cy)
        iso.isometricPrism(canvas, points, waterPrismCenter,waterHeight*10,color=waterColor)
    if buildingHeight != 0:
        buildingPrismCenter, bldgZOffset = (cx, cy), waterHeight*10
        iso.isometricPrism(canvas, points, buildingPrismCenter,buildingHeight*10,color='grey', zOffset=bldgZOffset)

def preprocessLine(text):
    """returns the input string without parentheses and separated into a list by
    commas and converted into the proper datatype"""
    lineList = text.replace('(', '').replace(')','').split(',')
    lineList[0], lineList[1] = int(lineList[0]), int(lineList[1]), 
    lineList[2], lineList[3] = int(lineList[2]), float(lineList[3])
    if lineList[4] == ' True': lineList[4] = True
    else: lineList[4] = False
    lineList[5] = lineList[5].replace("'", "")
    lineList[6] = float(lineList[6])
    return lineList
""" Sample representation of a hex grid as a 2D List
            [[0, 0, 0, 0]
            [0, 1, 0, 0]
            [0,0, 0, 0]
            [0,0, 0, 0] 
    evenDirections: [1,  0], [1, -1], [0, -1], [-1, -1], [-1,  0], [0, 1]
    oddDirections: [1, 1], [1, 0], [0, -1], [-1, 0], [-1, 1], [0, 1]
"""
class hexGrid:
    def __init__(self, rows, cols, boardLoaded = False, loadedBoard = None):
        self.rows, self.cols = rows, cols
        #hex grid is essentially a 2D list.
        self.loadedBoard = loadedBoard
        if not boardLoaded: 
            self.board, self.capitalCoords, self.sourceCoords = self.generateHexes(self.rows, self.cols)
        else: 
            self.board = [[None]*self.cols for row in range(self.rows)]
            self.capitalCoords, self.sourceCoords = self.setBoard()
        self.notification = None

    def setBoard(self):
        """set the board according self.loadedBoard"""
        newGrid = [[None]*self.cols for row in range(self.rows)]
        source, capital = None, None
        for tile in self.loadedBoard:
            tileInfo = preprocessLine(tile)
            self.board[tileInfo[0]][tileInfo[1]]=hexTile(*tileInfo[:5], self)
            tile = self.board[tileInfo[0]][tileInfo[1]]
            tile.buildingHeight = tileInfo[6]
            if tileInfo[4]:
                source = (tileInfo[0], tileInfo[1])
            if tileInfo[5] == ' dam':
                tile.building = bldg.dam(*tileInfo[:2])
                tile.createDam()
            elif tileInfo[5] == ' ditch':
                tile.building = bldg.ditch(*tileInfo[:2])
            elif tileInfo[5] == ' levee':
                tile.building = bldg.levee(*tileInfo[:2])
            elif tileInfo[5] == ' capital':
                tile.building = bldg.capital(*tileInfo[:2])
                capital = (tileInfo[0], tileInfo[1])
        return capital, source
    def getBoard(self):
        """returns the board representing as a 2d list of strings."""
        debugBoard = [[None]*self.cols for row in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                debugBoard[row][col] = self.board[row][col].getInfo()
        return debugBoard

    def getCapitalCoords(self):
        return self.capitalCoords

    def generateHexes(self, rows, cols):
        """randomly generates an new map with a starting source block"""
        minHeight, maxHeight = -1, 10
        newGrid = [[None]*self.cols for row in range(self.rows)]
        sourceWaterHeight = 5
        capitalBuilding = (random.randrange(0, rows), random.randrange(0, cols))
        for row in range(self.rows): #generates elevation hex tiles
            for col in range(self.cols):
                newGrid[row][col] = hexTile(row, col, 
                        random.randint(minHeight, maxHeight), 0, False, self)
                #newGrid[row][col].waterHeight = 1 for debugging purposes               
                if (row, col) == capitalBuilding:
                    newGrid[row][col].building = bldg.capital(row, col)
        #randomly generate the source tile
        sourceBlock = (random.randrange(0, rows), random.randrange(0, cols))
        while sourceBlock == capitalBuilding:
            sourceBlock = (random.randrange(0, rows), random.randrange(0, cols))
        newGrid[sourceBlock[0]][sourceBlock[1]].isSourceBlock = True
        newGrid[sourceBlock[0]][sourceBlock[1]].waterHeight = sourceWaterHeight
        return newGrid, capitalBuilding, sourceBlock

    def updateDams(self, tile):
        """updates dam water flow. Tile is a hex object which has a tile on it"""
        damOutflow = 0.25 #factor of how much water flows out of the intake tile.
        #with a value of 0.25, a quarter of the water heigh flows out of the dam.
        inTile = self.board[tile.building.damIntake[0]][tile.building.damIntake[1]]
        outTile = self.board[tile.building.damOutput[0]][tile.building.damOutput[1]]
        waterVolume = damOutflow * inTile.getInfo()[3]
        inTile.waterHeight -= waterVolume
        outTile.waterHeight += waterVolume

    def updateHexTiles(self, waterIncrease):
        """updates the water level in every tile by transferring water from
        1 tile to the next using the flowVector Attribute. Also spawns in 
        more water"""
        #add water to source block
        self.board[self.sourceCoords[0]][self.sourceCoords[1]].updateTile(waterIncrease, 0)
        for row in range(self.rows): 
            for col in range(self.cols): 
                tile = self.board[row][col]
                if tile.building != None and tile.building.name == 'dam':
                    self.updateDams(tile)
                for neighbour in tile.flowVector.keys():
                    #convert string to tuple
                    #strip parenthesis
                    neighbourCoords = neighbour.replace("(", "").replace(")","")
                    neighbourCoords = neighbourCoords.split(", ")
                    neighbourTile = self.board[int(neighbourCoords[0])][int(neighbourCoords[1])]
                    newNeighbourHeight = neighbourTile.getHeight()+tile.flowVector[neighbour]
                    newTileHeight = tile.getHeight()-tile.flowVector[neighbour]
                    newTileWaterHeight = tile.getInfo()[3]-tile.flowVector[neighbour]
                    #transfer water height from 1 coordinate to the next.
                    if newNeighbourHeight <= newTileHeight and \
                        newTileWaterHeight > 0:          
                        self.notification = neighbourTile.updateTile(tile.flowVector[neighbour], 0)
                        tile.updateTile(-tile.flowVector[neighbour], 0)


    def getElevationGraph(self):
        """returns a directed graph as an adjacency list with edges representing 
        the elevation change on a scale from 0 to 2"""
        adjacencyList = dict()
        minHeightDiff, maxHeightDiff = -20, 20 #smallest and largest possible height differences
        for nodeRow in range(self.rows): #loop through each hex tile
            for nodeCol in range(self.cols):
                currentNode = self.board[nodeRow][nodeCol]
                currentNodeID = str((nodeRow, nodeCol))
                currentHeight = currentNode.getHeight()
                adjacencyList[currentNodeID] = set()
                #loop through each neighbouring node
                for neighbour in currentNode.getAdjacentHexes():
                    neighbourNodeID = str(neighbour)
                    neighbourHeight = self.board[neighbour[0]][neighbour[1]].getHeight()
                    #normalize the height difference between 0 and 2 
                    #to avoid negative edge weights and negative cycles
                    #the higher the value, the more uphill it is
                    #1 is completeley flat
                    heightDifference = neighbourHeight-currentHeight
                    edgeWeight = 2 * (heightDifference-minHeightDiff)/(maxHeightDiff-minHeightDiff)
                    #add an edge to the adjacency list
                    adjacencyList[currentNodeID].add((neighbourNodeID, edgeWeight))
        return adjacencyList



class hexTile:
    def __init__(self, row, col, landHeight, waterHeight, isSourceBlock, grid):
        self.row,self.col = row, col
        self.landHeight,self.waterHeight = landHeight, waterHeight
        self.isSourceBlock = isSourceBlock #source blocks infinitely produce water
        self.building = None
        self.buildingHeight = 0
        self.totalHeight = self.landHeight+self.waterHeight+self.buildingHeight
        #this is the parent hexGrid of which the object is part of
        self.grid = grid 
        self.adjacentHexes = self.setAdjacentHexes()
        self.flowVector = dict()
        self.renderInfo = False
        self.debugData = None
        #provides a gradient of colors in the form of an rgb tuple from a light blue 
        #to dark blue. Used to color water tiles based on total height (darker is higher)
        self.waterHeightColors = [(max(173-step*10, 0), max(216-step*12, 0), 
            max(230-step*5, 0)) for step in range(0,20)]
        #provides a gradient of colors in the form of an rgb tuple from a brown 
        #to green. Used to color land tiles based on land height (darker is higher)
        self.landHeightColors = [(94+10*step,65+11*step,65+5*step) for step in range(0, 12)]
        self.landHeightColors = self.landHeightColors[::-1]
    def getInfo(self):
        """returns all relevant info about the tile"""
        if self.building != None:
            return (self.row,self.col,self.landHeight,self.waterHeight,self.isSourceBlock,
                   self.building.name,self.buildingHeight)
        else:
            return (self.row,self.col,self.landHeight,self.waterHeight,self.isSourceBlock,
                   None,self.buildingHeight)

    def getHeight(self):
        """return total height"""
        return self.landHeight+self.waterHeight+self.buildingHeight

    def getCoords(self):
        return (self.row, self.col)

    def getColor(self):
        """returns the color of the tile"""
        if self.getIsWaterTile():
            colorIndex = min(round(self.landHeight+self.waterHeight), 19)
            color = self.waterHeightColors[colorIndex]
            return cited.rgbString(color[0],color[1],color[2])
        else:
            #since landHeight is between -1 and 10, add 1 to correspond 
            #with indices in landHeightColors
            colorIndex = self.landHeight + 1
            color = self.landHeightColors[colorIndex]
            return cited.rgbString(color[0],color[1],color[2])
    def getIsWaterTile(self):
        return self.waterHeight > 0

    def getAdjacentHexes(self):
        return self.adjacentHexes
    
    def setAdjacentHexes(self):
        """returns a list of all adjacent hexes"""

        adjacentTile = [] #output list
        #the two lists are a list of vectors (dRow, dCol) for each adjacent tile
        #one is for odd rows, the other is for even rows
        evenDirections = [[1,  0], [-1, 1], [0, -1], [-1, -1], [-1,  0], [0, 1]]
        oddDirections =  [[0, 1], [-1, 0], [0, -1], [1, -1], [1, 0], [1, 1]]

        if self.col % 2 == 0: 
            adjacentPositions = evenDirections
        else:
            adjacentPositions = oddDirections

        for position in adjacentPositions:
            if 0 <= self.row + position[0] < self.grid.rows and \
               0 <= self.col + position[1] < self.grid.cols:
               adjacentTile.append((self.row + position[0],self.col + position[1]))
        return adjacentTile

    def updateTile(self, waterElevationChange, buildingElevationChange):
        self.buildingHeight += buildingElevationChange
        #water height can never be less than 0
        self.waterHeight = max(self.waterHeight+waterElevationChange, 0)
        self.totalHeight = self.landHeight+self.waterHeight+self.buildingHeight
        if self.waterHeight > 0 and self.building != None:
            alertText = f"{self.building.name} at {self.row}, {self.col} \n has been destroyed"
            self.building = None
            self.buildingHeight = 0
            return alertText

    def createDam(self):
        """creates a dam building in the tile"""
        evenColAxes = [((self.row-1, self.col+1), (self.row, self.col-1)),
                              ((self.row-1, self.col), (self.row+1, self.col)),
                              ((self.row-1, self.col-1), (self.row, self.col-1))]
        oddColAxes = [((self.row, self.col+1), (self.row+1, self.col-1)),
                              ((self.row-1, self.col), (self.row+1, self.col)),
                              ((self.row+1, self.col+1), (self.row+1, self.col-1))]
        axes = evenColAxes
        if self.col % 2 == 1: axes = oddColAxes
        possibleAxes = []
        damOrientation = None
        for axis in axes:
            if axis[1] in self.adjacentHexes and axis[0] in self.adjacentHexes:
                neighbour1 = self.grid.board[axis[0][0]][axis[0][1]]
                neighbour2 = self.grid.board[axis[1][0]][axis[1][1]]
                #check if neighbouring tiles are greater than the current
                #tile's height.
                if neighbour1.getHeight() > self.getHeight() and \
                    neighbour2.getHeight() > self.getHeight():
                    #add valid axis to possible axes
                    possibleAxes.append([min(neighbour2.getHeight(),
                    neighbour1.getHeight()), neighbour1,neighbour2])
        if len(possibleAxes) < 2: #need 2 valid axes for dam to be built
            self.building = None
            return 0
        #find axis with largest minimum height and set that to be the height
        axisHeight = 0
        for axis in range(len(possibleAxes)):
            if possibleAxes[axis][0] > axisHeight:
                axisHeight = possibleAxes[axis][0]
                damOrientation = possibleAxes[axis]
        possibleAxes.remove(damOrientation) #remove from list to avoid trouble in next several lines
        self.building.height = axisHeight
        damWaterFlow = random.choice(possibleAxes) #select other random axis
        #have the intake be tile with the lower height
        self.building.damIntake = max(damWaterFlow[1:], key=lambda k: k.getHeight())
        self.building.damOutput = min(damWaterFlow[1:], key=lambda k: k.getHeight())
        self.building.damIntake = self.building.damIntake.getCoords()
        self.building.damOutput = self.building.damOutput.getCoords()
        self.buildingHeight = self.building.height  
        return self.building.cost * max(self.landHeight*0.5, 1)    
        

    def updateBuilding(self, newBuilding):
        if newBuilding == None or self.getIsWaterTile():
            self.building = None
            self.buildingHeight = 0
            return 0 
        elif not isinstance(self.building, bldg.capital):
            if newBuilding.name == 'levee':
                self.building = newBuilding
                self.buildingHeight = 1
            elif newBuilding.name == 'ditch':
                self.building = newBuilding
                self.buildingHeight = -1
            elif newBuilding.name == 'dam':
                self.building = newBuilding
                #axes are pairs of neighboring nodes
                return self.createDam()


            #significantly more expensive to place buildings next to capital
            if self.grid.getCapitalCoords() in self.adjacentHexes:
                return 10 *self.building.cost * max(self.landHeight*0.5, 1)
            #cost scales with terrain height
            return self.building.cost * max(self.landHeight*0.5, 1)
        return 0

    def onClick(self):
        #self.renderInfo = not self.renderInfo
        pass

    def setFlowVectors(self, elevationGraph):
        """determine how much water flows into each adjacent hex"""
        currentNode = str((self.row, self.col))
        closestMinima = flow.findClosestMin(elevationGraph, currentNode)
        output = dict()
        adjacentCost = dict()
        minimaList = dict() #for debugging
        for neighbor in self.adjacentHexes: #finds the cost to go from one node to the next
            neighborRow, neighborCol = neighbor
            neighbor = str(neighbor)
            if flow.isLocalMin(elevationGraph, neighbor):
                adjacentCost[neighbor] = 0
            #check if neighbor is downhill or flat (water doesn't move uphill)
            elif self.grid.board[neighborRow][neighborCol].getHeight() <= self.getHeight():
                minimaCost = []
                for minima in closestMinima:
                    minimaCost.append(flow.dijkstraPath(elevationGraph, neighbor, minima)[1])
                minimaList[neighbor] = minimaCost
                adjacentCost[neighbor] = min(minimaCost)
        costSum = sum(adjacentCost.values())
        for neighbor in adjacentCost.keys():
            #the value is the proportion of water that should go to the 
            #neighboring tile
            if adjacentCost[neighbor] == 0: #edge case
                output[neighbor] = 1
            elif adjacentCost[neighbor] == costSum:
                output[neighbor] = costSum
            elif costSum != 0:
                #subtract from 1 since a lesser proportional value means
                #less cost and therefore more water should flow
                output[neighbor] = 1 - (adjacentCost[neighbor]/costSum)
            else: output[neighbor] = 0
        self.debugData = (costSum, adjacentCost,minimaList) # for debugging
        self.flowVector = output

    def getFlow(self, row, col):
        """returns the flow to the specified adjacent hex"""
        nodeID = str((row, col))

        if nodeID in self.flowVector:
            return self.flowVector[nodeID]
        else: return 0


    def renderNeighborVector(self, canvas, cx, cy, angle, maxRadius, isEvenCol):
        """renders a vector with a length and thickness based off of self.flowVector,
        and a shape based off of the size and center of hexagon"""
        avgThickness = 0.125
        if angle == 30: #upper-right hex
            if isEvenCol: length = self.getFlow(self.row-1, self.col+1)
            else: length = self.getFlow(self.row, self.col+1)
        elif angle == 90: #upper hex
            length = self.getFlow(self.row-1, self.col)
        elif angle == 150: #upper-left hex
            if isEvenCol: length = self.getFlow(self.row-1, self.col-1)
            else: length = self.getFlow(self.row, self.col-1)
        elif angle == 210: #lower-left hex
            if isEvenCol: length = self.getFlow(self.row, self.col-1)
            else: length = self.getFlow(self.row+1, self.col-1)
        elif angle == 270: #lower hex
            length = self.getFlow(self.row+1, self.col)
        elif angle == 330: #lower-right hex
            if isEvenCol: length = self.getFlow(self.row, self.col+1)
            else: length = self.getFlow(self.row+1, self.col+1)
        if length != 0:
            renderVectorArrow(canvas, cx, cy, angle, length*maxRadius, 
                            avgThickness*maxRadius, length, maxRadius)

    def getLandColor(self):
        """get the color of the land based on elevation"""
        #since landHeight is between -1 and 10, add 1 to correspond 
        #with indices in landHeightColors
        colorIndex = self.landHeight + 1
        color = self.landHeightColors[colorIndex]
        return cited.rgbString(color[0],color[1],color[2])
    def getWaterColor(self):
        """get the color of the water based on elevation"""
        colorIndex = min(round(self.landHeight+self.waterHeight), 19)
        color = self.waterHeightColors[colorIndex]
        return cited.rgbString(color[0],color[1],color[2])

    def renderHexPrism(self, canvas, cx, cy, radius):
        drawHexPrism(canvas, self.landHeight,self.waterHeight,self.buildingHeight, cx, cy, 
            radius,self.getLandColor(),self.getWaterColor())

    def render(self, canvas, radius, cx, cy, width, height, outline='black',justOutline=False):
        """renders hexagons and vectors
        Vectors are rendered based on self.flowVector, starting with the
        upper-right neighbor hex and iterating counterclockwise"""
        
        if not justOutline:
            drawHexagon(canvas, radius, cx, cy, self.getColor(), outline)
            if self.getIsWaterTile(): #render vectors
                isEven = (self.col % 2 == 0)
                for hexAngle in range(30,331, 60):
                    self.renderNeighborVector(canvas, cx, cy, hexAngle, radius, isEven)
                if self.isSourceBlock:
                    starRadius = radius/3
                    drawStar(canvas, cx, cy, 'yellow', starRadius)
            if self.building != None: #render building
                self.building.render(canvas, cx, cy, radius)
        else: drawHexagon(canvas, radius, cx, cy, '', outline)
                


def testGrid():
    """unit testing"""
    newBoard = hexGrid(3, 3)
    for row in newBoard.getBoard():
        print(row)





#testGrid()

    





