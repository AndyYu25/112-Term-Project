#isometric projections


#graphics framework from https://www.diderot.one/course/34/chapters/2847/
from cmu_112_graphics import *

import hexgrid
import math

#inspiration from https://en.wikipedia.org/wiki/Isometric_video_game_graphics
def CartesianToIsometric(x, y, cx, cy, zOffset=0):
    """converts the given cartesian coordinates to isometric coordinates 
    about the center coordinates"""
    x, y = x-cx, y-cy
    isoX = x-y
    isoY = (x+y)/2
    return [isoX+cx, isoY+cy+zOffset]

def isometricRect(canvas, pos1:list, pos2:list, centerX, centerY):
    """draws an isometric rectangle based on a flat rectangle's coordinates"""
    rectanglePoints = [[pos2[0], pos1[1]], pos1, [pos1[0], pos2[1]], pos2]
    flatPointList = []
    center = (centerX, centerY)
    for point in rectanglePoints: flatPointList.extend(CartesianToIsometric(*point, *center))
    canvas.create_polygon(*flatPointList, fill = '', outline='black')

def isometricPolygon(canvas, pointList, center, zOffset = 0, color='green'):
    """draws an isometric polygon. z-offsets changes the cartesian y-coordinate"""
    flatPointList = []
    for point in pointList:
        newPoint = CartesianToIsometric(*point, *center)
        newPoint[1] += zOffset
        flatPointList.extend(newPoint)
    canvas.create_polygon(*flatPointList, outline='black', fill=color)

def isometricPrism(canvas, pointList, center, height, color='green',zOffset=0):
    """draw an isometric prism with the given points for a shape and the height of the prism"""
    newPointList = pointList
    height=-height
    if height < 0: isometricPolygon(canvas, pointList, center, color=color,zOffset=zOffset)
    #draw surrounding rectangular faces
    for point in range(len(pointList)):
        if point not in [2, 3]:#exclude the 2nd face due to overlap
            isoTopCorner = CartesianToIsometric(*newPointList[point-1], *center,zOffset=height+zOffset)
            isoTopCorner1 = CartesianToIsometric(*newPointList[point], *center,zOffset=height+zOffset)
            isoBottomCorner = CartesianToIsometric(*pointList[point], *center,zOffset=zOffset)
            isoBottomCorner1 = CartesianToIsometric(*pointList[point-1], *center,zOffset=zOffset)
            canvas.create_polygon(*isoTopCorner,*isoTopCorner1,*isoBottomCorner, 
                                  *isoBottomCorner1, fill=color, outline='black')
    #draw top and bottom polygonal faces
    if height < 0: isometricPolygon(canvas, newPointList, center, zOffset = zOffset+height, color=color)
    else: isometricPolygon(canvas, pointList, center, color=color,zOffset=zOffset)

class test(App):
    def appStarted(self):
        """FOR TESTING PURPOSES"""
        pass
    def redrawAll(self, canvas):
        cx, cy = self.width/2, self.height/2
        radius = 60
        dy = radius * (3**0.5)/2
        yCoords = [cy, cy+dy, cy-dy]
        xCoords = [cx+radius, cx-radius, cx+radius/2, cx-radius/2]
        points = [[xCoords[0], yCoords[0]], 
                [xCoords[2], yCoords[2]], 
                [xCoords[3], yCoords[2]],
                [xCoords[1], yCoords[0]],
                [xCoords[3], yCoords[1]],
                [xCoords[2], yCoords[1]]]
        #bounding box
        #canvas.create_rectangle(cx-radius, cy-dy, cx+radius, cy+dy)
        #isometricRect(canvas, [cx-radius, cy-dy], [cx+radius, cy+dy], self.width/2, self.height/2)
        isometricPrism(canvas, points, (self.width/2, self.height/2), 100,zOffset=10)
#test() Uncomment to test functions