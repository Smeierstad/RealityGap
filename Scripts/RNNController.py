import neat
import numpy as np
import matplotlib.pyplot as plt
import os
import visualize
from configparser import ConfigParser

class RNNController:
    staticID = 1

    def __init__(self,  config, delta = None):
        configFile = ConfigParser()
        configFile.read(config)

        controllerData = configFile["DefaultGenome"]
        self.inNodes = int(controllerData["num_inputs"])

        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config)


        self.controllerGenome = neat.genome.DefaultGenome(RNNController.staticID)
        RNNController.staticID += 1
        self.controllerGenome.configure_new(self.config.genome_config)
        self.controller = neat.nn.RecurrentNetwork.create(self.controllerGenome, self.config)

    def __str__(self):
        return str(self.controllerGenome)
    
    def drawNet(self):
        visualize.draw_net(self.config, self.controllerGenome, True)

    def advance(self, obs, advanceTime = 0.2, timeStep = 0.02):
        out = self.controller.activate(obs)
        return out
    
    def reset(self):
        self.controller.reset()
    
    def plot(self, time, obs = None):
        
        x = []

        for i in range(time):
            obs = np.random.uniform(-1, 1, 12)
            x.append(self.advance(obs))

        plt.plot(x)
        plt.show()

    def mutate(self, mutateRate = 0.32, mutatePower = 0.32):
        self.controllerGenome.mutate(self.config.genome_config)
        self.controller = neat.nn.RecurrentNetwork.create(self.controllerGenome, self.config)
    

if __name__ == "__main__":
    controller = RNNController("configs/config.ini")

    # print(controller)
    # controller.drawNet()
    controller.plot(100)

    for i in range(100):
        controller.mutate()

    controller.plot(100)
    controller.drawNet()