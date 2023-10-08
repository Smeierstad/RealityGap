import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pickle



class LowPass:
    def __init__(self):
        self.buffer = []
        self.filterData = 0


        self.fs = 1000
        self.cutoff =200
        self.order = 5

        self.b, self.a = signal.butter(self.order, self.cutoff / (self.fs/2), 'low')

        self.index = -1
        self.setStart()


    def setStart(self):
        for i in range(18):
            self.buffer.append(0)

    def filter(self, newData):
        self.buffer.append(newData)

        self.filterData = (signal.filtfilt(self.b, self.a, self.buffer))
        self.index += 1

        return self.filterData[self.index]
