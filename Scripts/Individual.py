import matplotlib.pyplot as plt
from configparser import ConfigParser
from SineController12DOF import SineController12DOF
from CTRNNController import CTRNNController
from DecentralizedController import DecentralizedController
from copy import deepcopy

import numpy as np

class Individual:
    def __init__(self, controller_ref, config, delta):

        self.controller = controller_ref(config, delta)
        self.fitness = 0.0
        self.highestFitness = 0.0

        self.robot = 0

    def mutate(self, mutate_rate, sigma):
        self.controller.mutate(mutate_rate, sigma)

    def advance(self, obs = None, advanceTime = 0.2, timeStep = 0.02):
        return self.controller.advance(obs, advanceTime, timeStep)

    def reset(self):
        if self.highestFitness < self.fitness:
            self.highestFitness = self.fitness
        self.fitness = 0.0
        self.controller.reset()

    def setFitness(self, fitness):
        self.fitness = fitness

    def getFitness(self):
        return self.fitness
    
    def getHighestFitness(self):
        return self.highestFitness

    def __str__(self):
        string = ""
        string += str(self.fitness)
        return string
    
    def plot(self, time, obs = None):
        self.controller.reset()
        if obs == None:
            obs = np.zeros(12)
        self.controller.plot(time, obs)

    def getController(self):
        return self.controller
    
    def setRobot(self, robot):
        self.robot = robot

    def getRobot(self):
        return self.robot


if __name__ == "__main__":
    ind = Individual(DecentralizedController, "configs/config.ini", 0.2)
    ind.plot(10)

    ind.mutate(0, 0)
    ind.plot(10)
    for i in range(5):
        ind.advance(np.zeros(12), 0.2, 0.02)
        ind.plot(10)
    
    # controller.drawNet()

    

    
    