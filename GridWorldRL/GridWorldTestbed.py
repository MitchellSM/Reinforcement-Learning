# Imports
import numpy as np
from enum import Enum
import typing
from PIL import Image

## DEBUG INFO ##
imagepath = "images/" 
testimagename = "testmap"
imageext = ".png"
imageFileName = imagepath + testimagename + imageext
imageFileName = "GridWorldRL/images/testmap.png"
##

    ## Image Colour Space ##
WHITE = (255, 255, 255) # Open space (i.e. moveable space)
BLACK = (0, 0, 0)       # Closed space (i.e. borders)
GREEN = (0, 255, 0)     # Goal space (i.e. Goal state)
RED = (255, 0, 0)       # Start space (i.e. start state)
    ##

class Action(Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
       
    
    def __add__(self, y):
        if type(y) == Action:
            return ((self.value[0] + y.value[0]), (self.value[1] + y.value[1]))
        else:
            return ((self.value[0] + y[0]), (self.value[1] + y[1]))

    def __eq__(self, y):
        if type(y) == Action:
            return (self.value[0] == y.value[0]) and (self.value[1] == y.value[1])
        else:
            return (self.value[0] == y[0]) and (self.value[1] == y[1])
    
    def __hash__(self):
        return hash(tuple(self.value))

    def get():
        return [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]

class World:
    
    def __init__(self, filename):
        self.fn = filename
        self.xsize, self.ysize = 28, 28#None, None 
        self.startState, self.goalState = None, None
        self.bitmap = None
        self.agent = None
        self.boarders = []
        #if self.bitmap = None:
        #    self.bitmap, self.startState, self.goalState = self.loadMap(filename)
        

    def loadMap(self, filename: str, size : (int, int) = (28, 28)):
        """ Given an image, create a 2D map using a specified colour scheme """
        startState = None
        goalState = None
        bitImage = None
        boarders = []

        if type(filename) is not str:
            return None, None, None
        else:
            # Populate a size[0] x size[1] matrix with 0's 
            bitImage = np.zeros([size[0], size[1]])     #[[0 for i in range(size[0])] for j in range(size[1])]

        with Image.open(filename) as im:
            pix = im.load()
            #self.xsize, self.ysize = im.size()
            for x in range(size[0]):
                for y in range(size[1]):
                    if pix[x, y] == BLACK:
                        #bitImage[y][x] = -1
                        bitImage[x, y] = -1
                        boarders.append((x, y))
                    if pix[x, y] == GREEN:
                        goalState = (x, y)
                        # bitImage[y][x] = 1
                        bitImage[x, y] = 1
                    if pix[x, y] == RED:
                        startState = (x, y)
                        #bitImage[y][x] = 2
                        bitImage[x, y] = 2
        #print(boarders)
        return bitImage, startState, goalState, boarders
    
    def getSize(self):
        return self.xsize, self.ysize
    
    def getWorldInfo(self):
        print("Start State:", self.startState)
        return {"start": self.startState, "goal": self.goalState, "xsize": self.xsize, "ysize": self.ysize, "boarder": self.boarders}
    
    def addAgent(self):
        self.agent = Agent(self.getWorldInfo())

    # TODO finish this and figure out how to send agent state information to GUI
    def run(self, rounds=10):
        self.bitmap, self.startState, self.goalState, self.boarders = self.loadMap(self.fn)
        # print(self.startState, self.goalState)
        self.addAgent()
        states = self.agent.play(rounds)
        
        #print(self.agent.State.state)
        #print(self.goalState)
        #self.agent.showValues()
        return states

class State:
    ## Stuff that doesnt need to exist but while converting the project, I'm not sure what to do with ...

    def __init__(self, worldInfo, state, deterministic = False):

        self.state = state #worldInfo["start"] if state is None else state
        self.worldinfo = worldInfo
        self.isEnd = False
        self.deterministic = deterministic

    def isLegal(self, state):
        """ Check is state is within the bounds of the world """
        if state[0] > 0 and state[0] < self.worldinfo["xsize"]-1:
            if state[1] > 0 and state[1] < self.worldinfo["ysize"]-1:
                return True
        return False
    
    def getReward(self):
        #print(self.state, type(self.state))
        if self.state == self.worldinfo["goal"]:
            return 3
        elif self.state in self.worldinfo["boarder"]:
            #print("!")
            return -1 
        else:
            #for i in self.worldinfo["boarder"]:
            #    if i == self.state:
                    #print("Boarder!!!")
            #        return -1
            return 0
    
    def isEndFunc(self):
        if (self.state == self.worldinfo["goal"]) or (self.state in self.worldinfo["boarder"]):
            self.isEnd = True
    
    def _selectActionProb(self, action):
        if action == Action.UP:
            return np.random.choice([Action.UP, Action.LEFT, Action.RIGHT], p = [0.8, 0.1, 0.1])
        if action == Action.DOWN:
            return np.random.choice([Action.DOWN, Action.LEFT, Action.RIGHT], p = [0.8, 0.1, 0.1])
        if action == Action.LEFT:
            return np.random.choice([Action.LEFT, Action.UP, Action.DOWN], p = [0.8, 0.1, 0.1])
        if action == Action.RIGHT:
            return np.random.choice([Action.RIGHT, Action.UP, Action.DOWN], p = [0.8, 0.1, 0.1])
    
    def nextPos(self, action):
        if self.deterministic:
            nextState = action + self.state
            self.deterministic = False
        else:
            action = self._selectActionProb(action)
            self.deterministic = True
            nextState = self.nextPos(action)

        if self.isLegal(nextState):
            return nextState        
        return self.state
    
class Agent:

    def __init__(self, worldInfo):
        self.states = []
        self.actions = Action.get()
        self.worldinfo = worldInfo
        self.State = State(worldInfo, worldInfo["start"])
        self.learnrate = 0.2
        self.exprate = 0.3
        self.gamma = 0.8
        self.allStates = []
    
        self.Qvalues = {}
        for i in range(self.worldinfo["xsize"]):
            for j in range(self.worldinfo["ysize"]):
                self.Qvalues[(i, j)] = {}
                for a in self.actions:
                    self.Qvalues[(i, j)][a] = 3
    
    # TODO This needs to be rewritten to use e-Greedy or something... 
    # ... on second thought ... is this e-greedy in disguise? is exprate == epsilon? I think it is.. if so... lets change this to match my policy code
    # Implement Upper-bound Confidence Action Selection Algorithm instead of this bs. 
    def selectAction(self):
        mx_nextreward = 0
        #action = Action.UP

        if np.random.uniform(0, 1) <= self.exprate:
            action = np.random.choice(self.actions)
            
        else:
            for a in self.actions:
                current_pos = self.State.state
                nextreward = self.Qvalues[current_pos][a]
                if nextreward >= mx_nextreward:
                    action = a
                    mx_nextreward = nextreward
        return action 
    
    # TODO Use this in World to move agent?
    def stepAgent(self, action):
        pos = self.State.nextPos(action)
        return State(self.worldinfo, pos)
    
    def reset(self):
        self.allStates.append(self.states)
        self.states = []
        self.State = State(self.worldinfo, (2, 25))#self.worldinfo['start'])
        self.isEnd = False

    def play(self, rounds=50):
        i = 0
        while i < rounds:
            if self.State.isEnd:
                reward = self.State.getReward()
                #if reward == -1:
                #    print("Boarder: ", self.State.state)
                for a in self.actions:
                    self.Qvalues[self.State.state][a] = reward

                #print("Game End Reward", reward)

                for s in reversed(self.states):
                    current_Qvalue = self.Qvalues[s[0]][s[1]]
                    reward = current_Qvalue + self.learnrate * (self.gamma * reward - current_Qvalue)
                    self.Qvalues[s[0]][s[1]] = round(reward, 3)
                self.reset()
                i += 1
            else:
                action = self.selectAction()
                self.states.append([(self.State.state), action])
                #print("current pos {} action {}".format(self.State.state, action))

                self.State = self.stepAgent(action)
                self.State.isEndFunc()
                #print("next state", self.State.state)
                #print("------------------------------")
        return self.allStates


    def showValues(self):
        for i in range(0, self.worldinfo['xsize']):
            print("----------------------------------------------------------------------------------")
            out = "|"
            for j in range(0, self.worldinfo['ysize']):
                maxi = -1
                maxcoord = None
                act = None
                for a in self.actions:
                    if self.Qvalues[(i, j)][a] >= -1:
                        if self.Qvalues[(i, j)][a] > maxi:
                            maxi = self.Qvalues[(i, j)][a]
                            maxcoord = (i, j)
                            act = a
                if not act is None:
                    out += str(act.name) + " " + str(maxcoord) +" " + str(maxi) + " | "
                        #out += str(a.name) + " (" + str(i) + ", " + str(j) + ") "+ str(self.Qvalues[(i, j)][a]).ljust(6) + " | "
            print(out)
        print("----------------------------------------------------------------------------------")  



# TODO Implement play function from agent. Most of which will go into World, just need to figure out what functions all need for the world to "play" the agent. 
    


# world = World(imageFileName)
# states = world.run(2)
# coord = 0
# roundnum = 0
# step = 0
# print(states[roundnum][step][coord])


