import building as bldg
import hexgrid
import waterflow as flow
import copiedCode as cited
import isometric as iso
#python builtin module
import math
import os
import string
from datetime import datetime

#graphics framework from https://www.diderot.one/course/34/chapters/2847/
from cmu_112_graphics import *



def stripParens(text):
    """returns the input string without parentheses"""
    return text.replace('(', '').replace(')','')
    

class hydroGame(ModalApp):
    def appStarted(self):
        #self.addMode(StartMode(name='start'))
        self.addMode(InstructionMode(name='instruct'))
        self.addMode(GameMode(name='game'))
        self.addMode(EndMode(name='end'))
        self.addMode(StartMode(name='start'))
        self.setActiveMode('start')
        self.loadGame = False
        self.saveFileName = '\\saves'

class InstructionMode(Mode):
    def appStarted(self):
        pass
    def playGame(self):
        self.setActiveMode('game')
    def redrawAll(self, canvas):
        titleCoords = (self.width/2, self.height/20)
        titleFont = f'Arial {self.height//20}'
        canvas.create_text(*titleCoords, text='Game Information', font = titleFont)
        instructionText = ['Welcome to Hydraulic Engineering Simulator!', 
        'Your objective is to protect the capital building (shown to the right)', 
        'from being flooded by water for as long as possible.', 
        'Water comes from a single source block denoted with a yellow star.',
        'Hexagonal tiles are colored based on elevation and if there is water on the tile.',
        'Blue tiles have water on them, with darker shades indicating more water.',
        'All other tiles are colored darker the taller they are.',
        'Water tiles also have vectors colored which indicate the direction of flow.',
        'You can place buildings on water to help protect the capital.',
        'Levees increase the tile height by one, making it harder for water to flood that tile.',
        'Ditches decrease the tile height by one, providing an alternative path for water to flow.',
        'Dams are constructed with their height based on the axis with the greatest minimum height.',
        '(An axis is the two adjacent tiles that make up the vertical column and the 2 diagonals)',
        'Dams also divert water across the axis with the least minimum height,',
        'with water flowing from the higher tile on that axis to the lower tile on that axis.',
        'Cost is based on the height of the tile.', 
        'Buildings adjacent to the capital cost 10 times as much.',
        'Controls are the qweasd keys to control a selected tile, and the jkl keys to purchase buildings.',
        'To move the selected tile, use the w/s keys to move the tile up/down.', 
        'The q/d keys to move the tile up/down the downwards diagonal.',
        'The e/a keys to move the tile up/down the upwards diagonal.',
        'The j, k, and l keys purchase dams, ditches, and levees respectively.',
        'If a tile with a building gets flooded, the building is destroyed.', 
        'As time progressing, the amount of water flowing from the source block will increase.',
        'If the capital is destroyed, game over!',
        'Click the button to start the game, and good luck!']
        linePos = [self.width/2, self.height*0.1]
        for line in instructionText:
            canvas.create_text(*linePos, text=line)
            linePos[1] += self.height * 0.03
        buttonPos = (self.width/2, self.height * 0.95)
        buttonSize = (self.width/5, self.height/10)
        cited.drawButton(canvas, buttonPos[0], buttonPos[1], buttonSize[0], 
                        buttonSize[1],self.playGame, "Start Game", 'green')

class EndMode(Mode):
    def appStarted(self):
        self.score= self.getMode('game').timeSurvived
        #access leaderboard
        with open("leaderboard.txt", 'r') as f:
            self.scoreboard = [float(line) for line in f.readlines()]
            #update leaderboard
            self.scoreboard.append(self.score)
            self.scoreboard.sort(reverse=True)
            self.highestFiveScores = self.scoreboard[:5]
            f.close()
        #write new leaderboard to board
        with open("leaderboard.txt", 'w') as f:    
            for score in self.scoreboard:
                f.writelines(f"{score} \n")
            f.close()
        
    def keyPressed(self, event):
        if event.key == 'r':
            self.setActiveMode('start')

    def redrawAll(self, canvas):
        endText = [f"Your city lasted {self.score} hours!", 
                f"Your time was number {self.scoreboard.index(self.score)+1} on the leaderboard.",
                "Here are the top five scores:"]
        scoreText = ''
        endFont = f"Arial {self.height//30}"
        for score in range(len(self.highestFiveScores)):
            scoreText = scoreText + f"{score+1}. {self.highestFiveScores[score]}\n"
        textPos = [self.width/2, self.height * 0.1]
        for line in endText:
            canvas.create_text(*textPos, text=line,font=endFont)
            textPos[1] += self.height * 0.1
        textPos[1] += self.height * 0.15
        canvas.create_text(*textPos, text=scoreText,font=endFont)
        textPos[1] += self.height*0.15
        canvas.create_text(*textPos, text='Press R to return to the menu',font=endFont)        

class StartMode(Mode):
    def appStarted(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
    def newGame(self):
        """creates a new game"""
        self.app.getMode('game').appStarted()
        self.app.getMode('game').timeSurvived = 0
        self.app.getMode('game').resources = 500 
        self.setActiveMode('instruct')
    def loadGame(self):
        """loads the selected save file name"""
        self.app.loadGame = True
        self.app.saveFileName = filedialog.askopenfilename(initialdir = self.path+"\\saves",
                        title = "Select save file",
                        filetypes = (("text files","*.txt"),("all files","*.*")))
        self.app.getMode('game').appStarted()
        self.setActiveMode('instruct')
    def redrawAll(self, canvas):
        titlePos=[self.width/2, self.height/10]
        titleText=f"Arial 36"
        canvas.create_text(*titlePos, text='Hydraulic Engineering',font=titleText)
        titlePos[1] += self.height/10
        canvas.create_text(*titlePos, text='Simulator',font=titleText)
        buttonSizes = (self.width/3, self.height/7)
        loadGameButtonPos = [self.width/2, self.height/2]
        cited.drawButton(canvas, *loadGameButtonPos, *buttonSizes, self.loadGame,
                         'Load Game', 'white')
        loadGameButtonPos[1] += self.height * 0.25
        cited.drawButton(canvas, *loadGameButtonPos, *buttonSizes, self.newGame, 
                        'New Game', 'white')

class GameMode(Mode):
    def appStarted(self):
        self.selectedNode = [0,0]
        self.boardDim = (8, 8)
        if self.app.loadGame: self.loadGame(self.app.saveFileName)
        else: self.grid = hexgrid.hexGrid(self.boardDim[0], self.boardDim[1])
        if not hasattr(self, 'timeSurvived'):
            self.timeSurvived = 0
        self.timer = 0
        if not hasattr(self, 'resources'):
            self.resources = 500
        self.displayTile = (None, None)
        #hexSize is the total width of the hexagon. A single side is hexSize/2 pixels long.
        self.hexSize = self.width/self.boardDim[1] * 0.85
        self.hexHeight = (3**0.5)/2 * self.hexSize 
        self.startWater = False
        self.waterIncrease = 0.25
        self.notificationText = None
        self.isoView = False
        self.notificationDuration = 50

    def moveSelection(self, drow, dcol):
        """moves a piece by the specified dRow and dCol if possible"""
        if 0 <= self.selectedNode[0] + drow < self.boardDim[0] and \
           0 <= self.selectedNode[1] + dcol < self.boardDim[1]:    
            self.selectedNode[0] += drow
            self.selectedNode[1] += dcol


    def keyPressed(self, event):
        """place buildings or move selection.
         Movement is as follows (letters represent the direction the cell moves
         if that key is pressed, c is the current selected tile):
           w
         q   e
           c 
         a   d 
           s
        """
        isEvenCol = (self.selectedNode[1] % 2 == 0)
        if event.key == 'w': self.moveSelection(-1, 0)
        elif event.key == 's': self.moveSelection(1, 0)
        elif event.key == 'q':
            if isEvenCol: self.moveSelection(-1, -1)
            else: self.moveSelection(0, -1)
        elif event.key == 'e':
            if isEvenCol: self.moveSelection(-1, 1)
            else: self.moveSelection(0, 1)
        elif event.key == 'a':
            if isEvenCol: self.moveSelection(0, -1)
            else: self.moveSelection(1, -1)
        elif event.key == 'd':
            if isEvenCol: self.moveSelection(0, 1)
            else: self.moveSelection(1, 1)
        elif event.key == 'l':
            currentRow,currentCol = self.selectedNode[0], self.selectedNode[1]
            cost = self.grid.board[currentRow][
                            currentCol].updateBuilding(bldg.levee(currentRow, currentCol))
            if self.resources - cost >= 0: self.resources -= cost
            else: self.grid.board[currentRow][currentCol].updateBuilding(None)
        elif event.key == 'k':
            currentRow,currentCol = self.selectedNode[0], self.selectedNode[1]
            cost = self.grid.board[currentRow][
                            currentCol].updateBuilding(bldg.ditch(currentRow, currentCol))
            if self.resources - cost >= 0:
                self.resources -= cost
            else: self.grid.board[currentRow][currentCol].updateBuilding(None)
        elif event.key == 'j':
            currentRow,currentCol = self.selectedNode[0], self.selectedNode[1]
            cost = self.grid.board[currentRow][
                            currentCol].updateBuilding(bldg.dam(currentRow, currentCol))
            if self.resources - cost >= 0: self.resources -= cost
            else: self.grid.board[currentRow][currentCol].updateBuilding(None)
        elif event.key == 'r':
            self.setActiveMode('start')


    def timerFired(self):
        self.timer += 1
        if self.notificationText != None: self.notificationDuration -= 1
        floodInterval = 5 #frequency that flowvectors get updated
        if self.timer % floodInterval == 0 and self.startWater:
            #water exponentially increases as time increases
            self.waterIncrease *= 1.05
            #time survived goes up by 1 every second
            self.timeSurvived += floodInterval/10
            #get notification if building is destroyed
            if self.grid.notification != None:
                self.notificationText = self.grid.notification[
                    0].upper()+self.grid.notification[1:]
            #get updated elevation graph and flow vectors
            graph = self.grid.getElevationGraph()
            for row in range(self.boardDim[0]):
                for col in range(self.boardDim[1]):
                    if self.grid.board[row][col].getIsWaterTile():
                        self.grid.board[row][col].setFlowVectors(graph)
            self.grid.updateHexTiles(self.waterIncrease)
            capital = self.grid.getCapitalCoords()
            if self.grid.board[capital[0]][capital[1]].building == None:
                self.setActiveMode('end')
        if self.notificationDuration == 0:
            self.notificationText = None
            self.notificationDuration = 50

    def mousePressed(self, event):
        pass
    
    def renderHexGrid(self, canvas, leftCorner):
        """draws a hex grid"""
        if not self.isoView:
            for row in range(self.boardDim[0]):
                for col in range(self.boardDim[1]):
                    tile = self.grid.board[row][col]
                    #each tile is spaced three times the edge length apart
                    #odd-q vertical layout
                    cx = leftCorner[1] + col * self.hexSize * 0.75
                    #each row is half a hexagon tall
                    cy = leftCorner[0] + self.hexHeight * (row + 0.5*(col%2))
                    #if self.isoView = True
                    tile.render(canvas, self.hexSize/2, cx, cy,self.width, self.height, outline='black')
        else:
            #EXPERIMENTAL ISOMETRIC VIEW. WILL BE LARGER THAN CANVAS
            for row in range(self.boardDim[0]):
                for col in range(self.boardDim[1]):
                    tile = self.grid.board[row][col]
                    cx = leftCorner[1] + col * self.hexSize * 0.75
                    cy = leftCorner[0] + self.hexHeight * (row + 0.5*(col%2))
                    cx, cy = iso.CartesianToIsometric(cx, cy, self.width/2, self.height/2)
                    tile.renderHexPrism(canvas,cx, cy, self.hexSize/2)

    def activateWater(self):
        """toggles whether or not the water will flow"""
        self.startWater = not self.startWater

    def loadGame(self, fileName):
        '''loads game based on savegame format'''
        with open(fileName, "r") as loadedFile:
            hexInfo = loadedFile.readlines()
            gameInfo = stripParens(hexInfo.pop(0)).split(',')
            self.boardDim = (int(gameInfo[0]), int(gameInfo[1]))
            self.timeSurvived = float(gameInfo[2])
            self.resources = int(gameInfo[3])
            print(self.resources)
            self.grid = hexgrid.hexGrid(*self.boardDim, boardLoaded = True, loadedBoard = hexInfo)

    def saveGame(self):
        """save the game as a text file in the saves folder
        Format is as follows:
        (rows, cols)
        (tileInfo1)
        (tileInfo1)
        ...
        ...
        (tileInfoN)"""
        #get current date and time
        now = datetime.datetime.now()
        currentTime = now.strftime("%d-%m-%Y_%H-%M-%S")
        saveGameInfo = self.grid.getBoard()
        saveFileName = str("saves\\"+currentTime+".txt")
        with open(saveFileName, "w+") as saveFile:
            saveFile.write(str(self.boardDim)+','+str(self.timeSurvived) +','+str(int(self.resources))+", \n")
            for row in saveGameInfo:
                for tile in row:
                    saveFile.write(str(tile) + "\n")
            saveFile.close()

    def toggleIso(self):
        self.isoView = not self.isoView

    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, outline = '',fill='#D2B48C')
        leftCorner = (self.hexSize/2, self.hexSize/2)
        #draw hex grid
        self.renderHexGrid(canvas, leftCorner)   
        #draw selection outline            
        cx = leftCorner[1] + self.selectedNode[1] * self.hexSize * 0.75
        tile = self.grid.board[self.selectedNode[0]][self.selectedNode[1]]
        cy = leftCorner[0] + self.hexHeight * (self.selectedNode[0] + 0.5*(self.selectedNode[1]%2))
        if not self.isoView:
            tile.render(canvas, self.hexSize/2, cx, cy, self.width, self.height,
                outline = 'red', justOutline=True)
            tile.renderHexPrism(canvas, self.width * 0.85, self.height*0.6, self.hexSize)
        #draw info sidebar
        font = f"Arial {int(self.width//40)}"
        textPos = (self.width * 0.825, self.height* 0.15)
        canvas.create_text(*textPos, font = font, 
        text=f"Funds Left: {self.resources} \n Hours Survived: {self.timeSurvived}")
        #draw notifications
        canvas.create_text(self.width*0.8, self.height*0.05, text=self.notificationText, 
            fill='red', font=font)
        waterButtonPos = (self.width * 0.2, self.height * 0.9)

        #draw bottom buttons
        buttonSize = ( self.width/5, self.height/15)
        cited.drawButton(canvas, waterButtonPos[0], waterButtonPos[1], *buttonSize,
            self.activateWater, "Toggle Water Flow", 'green')
        saveButtonPos = (self.width * 0.4, self.height * 0.9)
        cited.drawButton(canvas, *saveButtonPos, *buttonSize,
            self.saveGame, "Save Game", 'grey')
        isoButtonPos = (self.width * 0.6, self.height * 0.9)
        cited.drawButton(canvas, *isoButtonPos, *buttonSize,
            self.toggleIso, "Isometric View", 'blue')
hydroGame(width=800, height = 800)