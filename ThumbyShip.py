import time
import thumby
import math
import random
import ujson

GAME_NAME = "ThumbyShip"
GAME_DIR = "/Games/" + GAME_NAME

from sys import path
path.append(GAME_DIR)

import thumbyGrayscale
graphics = thumbyGrayscale

graphics.display.setFPS(30)
graphics.display.fill(0)
graphics.display.drawText(" Loading... ", 0, 15, 1)
graphics.display.update()

playing = False
turn = False
start = True

def drawBoard():
    for i in range(10):
        for j in range(10):
            graphics.display.drawFilledRectangle(17 + (j * 4), 1 + (i * 4), 2, 2, 2)

def createEmptyBoard():
    b = []
    for i in range(10):
        b.append([0,0,0,0,0,0,0,0,0,0])
    return b
    
def clamp(lo, hi, x):
    return min(hi, max(lo, x))

myBoard = createEmptyBoard()
myHits = createEmptyBoard()
otherBoard = createEmptyBoard()

boats = [2,2,2,2,3,3,3,4,4,6]
boats = sorted(boats, key = lambda x: random.random())
index = 0

xPos = 0
yPos = 0
rot = 0
target = [0, 0]

while True:
    if start:
        if thumby.buttonU.justPressed():
            yPos = clamp(0, 9, yPos - 1)
        if thumby.buttonD.justPressed():
            yPos = clamp(0, (10 - boats[index] if rot == 1 else 9), yPos + 1)
        if thumby.buttonL.justPressed():
            xPos = clamp(0, 9, xPos - 1)
        if thumby.buttonR.justPressed():
            xPos = clamp(0, (10 - boats[index] if rot == 0 else 9), xPos + 1)
        if thumby.buttonB.justPressed():
            rot = int((rot + 1) % 2)
        if thumby.buttonA.justPressed():
            boat = []
            for i in range(boats[index]):
                boat.append([xPos if rot == 1 else xPos + i, yPos if rot == 0 else yPos + i])
            coll = False
            for i in boat:
                if myBoard[i[1]][i[0]] == 1:
                    coll = True
            if coll == False:
                for i in boat:
                    myBoard[i[1]][i[0]] = 1
                rot, xPos, yPos = 0, 0, 0
                if index < 9:
                    index += 1
                else:
                    start = False
                    playing = True

        graphics.display.fill(0)
        drawBoard()
        for i in range(10):
            for j in range(10):
                if myBoard[i][j] == 1:
                    graphics.display.drawFilledRectangle(16 + (j * 4), i * 4, 4, 4, 3)
        graphics.display.drawFilledRectangle(16 + (xPos * 4), yPos * 4, (boats[index] if rot == 0 else 1) * 4, (boats[index] if rot == 1 else 1) * 4, 1)
        graphics.display.update()

        
    elif playing:
        if myBoard == myHits:
            print("Lose")
        if turn:
            endTurn = False
            if thumby.buttonU.justPressed():
                yPos = clamp(0, 9, yPos - 1)
            if thumby.buttonD.justPressed():
                yPos = clamp(0, 9, yPos + 1)
            if thumby.buttonL.justPressed():
                xPos = clamp(0, 9, xPos - 1)
            if thumby.buttonR.justPressed():
                xPos = clamp(0, 9, xPos + 1)
            if thumby.buttonA.justPressed():
                if otherBoard[yPos][xPos] == 0:
                    target = [xPos, yPos]
                    thumby.link.send(str(target).encode())
                    received = thumby.link.receive()
                    if received != None:
                        message = received.decode()
                        if message == "Hit":
                            otherBoard[target[1]][target[0]] = 2
                        elif message == "Miss":
                            otherBoard[target[1]][target[0]] = 1
                        endTurn = True
            graphics.display.fill(0)
            drawBoard()
            for i in range(10):
                for j in range(10):
                    if otherBoard[i][j] == 2:
                        graphics.display.drawFilledRectangle(16 + (j * 4), i * 4, 4, 4, 3)
                    elif otherBoard[i][j]== 1:
                        graphics.display.drawRectangle(16 + (j * 4), i * 4, 4, 4, 3)
            graphics.display.setPixel(16 + xPos, yPos, 1)
            graphics.display.setPixel(19 + xPos, yPos, 1)
            graphics.display.setPixel(16 + xPos, 3 + yPos, 1)
            graphics.display.setPixel(19 + xPos, 3 + yPos, 1)
            graphics.display.update()
            if endTurn:
                time.sleep(1)
                turn = False
        else:
            startTurn = False
            received = thumby.link.receive()
            if received != None:
                message = received.decode()
                if message[0].isnumeric():
                    t = message.split(",")
                    t = [int(t[0]), int([t[1]])]
                    if myBoard[t[1]][t[0]] == 1:
                        myHits[t[1]][t[0]] = 1
                        thumby.link.send("Hit".encode())
                    else:
                        thumby.link.send("Miss".encode())
                    startTurn = True
            graphics.display.fill(0)
            drawBoard()
            for i in range(10):
                for j in range(10):
                    if myBoard[i][j] == 1:
                        graphics.display.drawFilledRectangle(16 + (j * 4), i * 4, 4, 4, 1)
                    if myHits[i][j] == 1:
                        graphics.display.drawFilledRectangle(17 + (j * 4), 1 + (i * 4), 2, 2, 3)
            graphics.display.update()
            if startTurn:
                time.sleep(1)
                turn = True
    
