import neat
import numpy as np
import matplotlib.pyplot as plt
import os
import visualize
from configparser import ConfigParser

from CTRNNController import CTRNNController

import copy
import time


class SyncControllerOne:
    static_id = 1

    def __init__(self, config, delta = 0.2):

        configFile = ConfigParser()
        configFile.read(config)

        self.delta = delta

        files = configFile["FILES"]
        eaData = configFile["EA"]

        self.brainConfig = files["brainconfigsync"]

        self.brain = CTRNNController(self.brainConfig, self.delta)


    def reset(self):
        self.brain.reset()

    def mutate(self, mutateRate = 0.0, sigma = 0.0):
        self.brain.mutate()
        
    def advance(self, obs, advanceTime = 0.002, timeStep = 0.02):
        brainOutput = self.brain.advance(obs, advanceTime, timeStep)
        output = []


        leg1 = brainOutput[0:3]
        leg2 = brainOutput[3:6]
        
        output.extend(leg1)
        output.extend(leg2)

        leg1[1] = - leg1[1]
        leg1[2] = - leg1[2]

        leg2[1] = - leg2[1]
        leg2[2] = - leg2[2]

        # leg1 = [-x for x in leg1]
        # leg2 = [-x for x in leg2]

        output.extend(leg1)
        output.extend(leg2)
        
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
        
if __name__ == "__main__":
    controller = SyncControllerOne("configs/config.ini", 0.2)
    controller.reset()

    # for i in range(10):
    #     controller.mutate()

    # for i in range(1):
    #     controller = DecentralizedController("configs/config.ini", 0.2)
    #     controller.reset()
    #     controller.plot(200, np.random.uniform(-1, 1, 12))
    # controller.plot(100, np.ones(12))

    # controller.advance(np.zeros(12))
    for i in range(10):
        print(controller.advance(np.ones(12)))
    




