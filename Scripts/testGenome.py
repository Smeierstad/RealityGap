from Evaluator import eval_genome, testOne, makeEnv, testAll
from Individual import Individual
from DecentralizedController import DecentralizedController
from SyncControllerOne import SyncControllerOne
# from EvaluatorLowPass import eval_genome_lowpass, testOne, makeEnv
import pickle
import numpy as np
from configparser import ConfigParser
import os
import platform


# path = r"Builds/NoRigid_W"
# path = None

folder = r"runs\1\CTRNN\SDP\20"
# folder = r"runs\3\CTRNN\1\04\2023_07_06_11_22_47_418700"


number = "099"

for subdir, dirs, files in os.walk(folder):
        for file in files:
            name = os.path.join(subdir, file)
            if "config.ini" in name:
                  config = name
            if "bestInv" + number in name:
                  file = name
                  break

configFile = ConfigParser()
configFile.read(config)

eaData = configFile["EA"]
filesData = configFile["FILES"]

path = "Builds/"

if platform.system() == "Windows":
    path += "Windows/"
    path += filesData["path"]

else:
    path += "Linux/"
    path += filesData["path"]
    path += "/linux.x86_64"

# path = "Builds/Windows/2"
# path = None

steps = int(eaData["steps"])
DP = int(eaData["DP"])
advanceTime = float(eaData["advanceTime"])
timeStep = float(eaData["timeStep"])




with open(file, 'rb') as f:
    ind = pickle.load(f)

# ind = Individual(DecentralizedController, "configs/config.ini", 0.02)

# controller = ind.getController()
# # controller.plot(1000)
# controller.drawNet()


q = makeEnv(path)


# testOne(ind, advanceTime, timeStep, q, steps, DP=DP)
testAll(folder, q, number)

q.get()[0].close()
