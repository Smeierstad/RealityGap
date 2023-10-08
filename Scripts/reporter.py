import os
import pickle
from datetime import datetime
import shutil
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from configparser import ConfigParser


class Reporter:

    def __init__(self, folderPath, config, name):
        
        self.filePath = folderPath

        if name == "":
            name = datetime.now()
            name = name.strftime("%Y_%m_%d_%H_%M_%S_%f")
        else:
            name = name
        

        self.path = os.path.join(folderPath, name)
        self.csvPath = self.path + "/stats.csv"

        os.mkdir(self.path)
        os.mkdir(self.path + "/gens")

        configFile = ConfigParser()
        configFile.read(config)

        filesData = configFile["FILES"]
        legConfig = filesData["legconfig"]
        brainConfig = filesData["brainconfig"]
        brainConfigSync = filesData["brainconfigsync"]

        self.config = shutil.copy(config, self.path + "/" + config[8::])
        self.legConfig = shutil.copy(legConfig, self.path + "/" + legConfig[8::])
        self.brainConfig = shutil.copy(brainConfig, self.path + "/" + brainConfig[8::])
        self.brainConfigSync = shutil.copy(brainConfigSync, self.path + "/" + brainConfigSync[8::])

    def getConfig(self):
        return self.config
    
    def getLegConfig(self):
        return self.legConfig
    
    def getBrainConfig(self):
        return self.brainConfig
    
    def getBrainConfigSync(self):
        return self.brainConfigSync

    def savePop(self, pop, gen):
        with open(self.path + "/gens/gen" +  str(gen), 'wb') as f:
            pickle.dump(pop, f)
    
    def saveElite(self, elite, gen):
        if (gen < 100):
            if (gen < 10):
                gen = "0" + str(gen)
            gen = "0" + str(gen)
        with open(self.path + "/gens/bestInv" +  str(gen), 'wb') as f:
            pickle.dump(elite, f)
    
    def saveStats(self, fits):
        with open(self.csvPath, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(fits)

    def plot(self, file=None):

        if file:
            df = pd.read_csv(file, header=None)
        else:
            df = pd.read_csv(self.csvPath, header=None)

        mean = df.mean(axis=1)
        max = df.max(axis=1)
        min = df.min(axis=1)


        plt.plot(mean)
        plt.plot(min)
        plt.plot(max)
        plt.show()

def plot(file):

    df = pd.read_csv(file, header=None)

    mean = df.mean(axis=1)
    max = df.max(axis=1)
    min = df.min(axis=1)


    plt.plot(mean)
    plt.plot(min)
    plt.plot(max)
    plt.show()

if __name__ == "__main__":

    rep = Reporter("runs", "configs/config.ini", "")


