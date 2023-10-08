import math
import numpy as np
import matplotlib.pyplot as plt
from configparser import ConfigParser



class SineController:
    
    def __init__(self, config):


        self.time = 0.0
        self.amp = np.random.uniform(0.0, 0.5)
        self.freq = np.random.uniform(0, 2)
        self.phase = np.random.uniform(-1, 1)
        self.offset = np.random.uniform(-0.5, 0.5)

    def __str__(self):
        string = "Amplitude: " + str(self.amp)
        string += "\nFrequncy: " + str(self.freq)
        string += "\nPhase: " + str(self.phase)
        string += "\nOffset: " + str(self.offset)
        return string

    def advance(self, obs = None, deltaTime = 0.2):
        self.time += deltaTime
        return min(1, max(-1, self.amp * math.sin(self.freq * self.time + self.phase) + self.offset))

    def reset(self):
        self.time = 0

    def mutate(self, mutate_rate, sigma):

        mut = np.random.random()

        if mut < mutate_rate:
            rand_choice = np.random.choice(["amp", "phase", "offset", "freq"])
            to_mutate = "self."+rand_choice
            exec(to_mutate + f"+= np.random.normal(0, {sigma})")
    
    def plot(self, time, show = False):
        x = []

        for i in range(time): 
            x.append(self.advance())

        if show:
            plt.plot(x)
            plt.show()

        return x
        



if __name__ == "__main__":
    controller = SineController("config")
    print(controller)

    controller.plot(100, True)