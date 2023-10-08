import neat
import numpy as np
import matplotlib.pyplot as plt
import os
import visualize
from configparser import ConfigParser


class CTRNNController:
    staticID = 1

    def __init__(self, config, delta = 0.2):

        configFile = ConfigParser()
        configFile.read(config)

        self.delta = delta

        controllerData = configFile["DefaultGenome"]
        self.inNodes = int(controllerData["num_inputs"])

        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config)

        self.controllerGenome = neat.genome.DefaultGenome(CTRNNController.staticID)
        CTRNNController.staticID += 1
        self.controllerGenome.configure_new(self.config.genome_config)
        self.controller = neat.ctrnn.CTRNN.create(self.controllerGenome, self.config, delta)


    def __str__(self):
        return str(self.controllerGenome)

    def reset(self):
        self.controller.reset()

    def advance(self, obs, advanceTime = 0.05, timeStep = 0.05):
        out = self.controller.advance(obs, advanceTime, timeStep)
        # print(out)
        # for i in range(len(out)):
        #     out[i] = min(max(-1, out[i]), 1)
        return out

    def mutate(self, mutate_rate = 0.32, sigma = 1):
        self.controllerGenome.mutate(self.config.genome_config)
        self.controller = neat.ctrnn.CTRNN.create(self.controllerGenome, self.config, self.delta)

    def drawNet(self):
        visualize.draw_net(self.config, self.controllerGenome, True)
    
    def plot(self, time, obs = None, show=True):
        x = []

        if (obs == None):
            obs = np.ones(self.inNodes)

        for i in range(time):
            x.append(self.advance(obs))
        
        plt.plot(x)
        if show:
            plt.show()
        

    
if __name__ == "__main__":

    controller = CTRNNController("configs/config.ini", 0.2)
    # print(controller)

    # controller.reset()

    # for i in range(1):
    #     controller.mutate()

    # controller.drawNet()

    controller.plot(10000)