import neat
import numpy as np
import matplotlib.pyplot as plt
import os
import visualize
from configparser import ConfigParser

from CTRNNController import CTRNNController

import copy
import time


class DecentralizedController:
    static_id = 1

    def __init__(self, config, delta = 0.2):

        configFile = ConfigParser()
        configFile.read(config)

        self.delta = delta

        files = configFile["FILES"]
        eaData = configFile["EA"]

        self.legConfig = files["legconfig"]
        self.brainConfig = files["brainconfig"]

        self.brain = CTRNNController(self.brainConfig, self.delta)

        self.legs = []
        self.leg = CTRNNController(self.legConfig, self.delta)
        for i in range(4):
            self.legs.append(copy.deepcopy(self.leg))


    def reset(self):
        self.brain.reset()
        for leg in self.legs:
            leg.reset()

    def mutate(self, mutateRate = 0.0, sigma = 0.0):
        self.brain.mutate()
        self.leg.mutate()

        for i in range(4):
            self.legs[i] = copy.deepcopy(self.leg)
        
    def advance(self, obs, advanceTime = 0.002, timeStep = 0.02):
        brainOutput = self.brain.advance(obs, advanceTime, timeStep)
        output = []

        for i in range(4):
            output.extend(self.legs[i].advance([brainOutput[i]], advanceTime, timeStep))

        # output = [(x * 2) - 1 for x in output]
        # print(output)
        
        return output

    def plot(self, time, obs = None):

        plt.style.use('ggplot')
        x = []
        for i in range(time):
            obs = np.random.uniform(-100, 100, 12)
            x.append(self.advance(obs))
        plt.plot(x)
        plt.show()

    def drawNet(self):       
        self.brain.drawNet()

        time.sleep(2)
        
        self.leg.drawNet()
        
if __name__ == "__main__":
    controller = DecentralizedController("configs/config.ini", 0.2)
    controller.reset()

    for i in range(10):
        controller.mutate()

    # for i in range(1):
    #     controller = DecentralizedController("configs/config.ini", 0.2)
    #     controller.reset()
    #     controller.plot(200, np.random.uniform(-1, 1, 12))

    controller.plot(2000, np.ones(12))

    # controller.advance(np.zeros(12))

    # controller.drawNet()
    




