from SineController import SineController
import matplotlib.pyplot as plt


class SineController12DOF:

    def __init__(self, config = None, delta = None):
        self.controllers = []
        for i in range(12):
            self.controllers.append(SineController(config))

    def __str__(self) -> str:

        string = ""

        for controller in self.controllers:
            string += str(controller)
            string += "\n\n"
        
        return string

    def advance(self, obs = None, advanceTime = 0.2, timeStep = None):
        actions = []
        for controller in self.controllers:
            actions.append(controller.advance(advanceTime))
        return actions


    def reset(self):
        for controller in self.controllers:
            controller.reset()

    def mutate(self, mutate_rate, sigma = 1):
        for controller in self.controllers:
            controller.mutate(mutate_rate, sigma)

    def plot(self, time, obs = None):
        for controller in self.controllers:
            plt.plot(controller.plot(time))
        plt.show()
    
    def getControllers(self):
        return self.controllers

    def drawNet(self):
        self.plot(100)



    
if __name__ == "__main__":
    controller = SineController12DOF()
    controller.plot(100)

    for i in range(100):
        controller.mutate(0.2, 1)

    controller.plot(100)