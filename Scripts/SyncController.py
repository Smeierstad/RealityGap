import neat
import numpy as np
import matplotlib.pyplot as plt
import os
import visualize
from configparser import ConfigParser

from CTRNNController import CTRNNController

import copy
import time


class SyncController:
    static_id = 1

    def __init__(self, config, delta = 0.2):

        configFile = ConfigParser()
        configFile.read(config)

        self.delta = delta

        files = configFile["FILES"]
        eaData = configFile["EA"]

        self.legConfig = files["legconfig"]
        self.brainConfig = files["brainconfigsync"]

        self.brain = CTRNNController(self.brainConfig, self.delta)

        self.legs = []
        self.leg1 = CTRNNController(self.legConfig, self.delta)
        self.leg2 = CTRNNController(self.legConfig, self.delta)


    def reset(self):
        self.brain.reset()
        self.leg1.reset()
        self.leg2.reset()

    def mutate(self, mutateRate = 0.0, sigma = 0.0):
        self.brain.mutate()
        self.leg1.mutate()
        self.leg2.mutate()
        
    def advance(self, obs, advanceTime = 0.002, timeStep = 0.02):
        brainOutput = self.brain.advance(obs, advanceTime, timeStep)
        output = []

        leg1 = self.leg1.advance([brainOutput[0]], advanceTime, timeStep)
        leg2 = self.leg2.advance([brainOutput[1]], advanceTime, timeStep)

        output.extend(leg1)
        output.extend(leg2)

        leg1 = [-x for x in leg1]
        leg2 = [-x for x in leg2]

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

        time.sleep(2)
        
        self.leg1.drawNet()
        
        time.sleep(2)

        self.leg2.drawNet()
        
if __name__ == "__main__":
    controller = SyncController("configs/config.ini", 0.2)
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
    




