from deap import base,tools,algorithms
import queue
import threading
import sys
import numpy as np
import pickle
import time

from tqdm import tqdm
from copy import deepcopy

import platform

from Individual import Individual
from SineController12DOF import SineController12DOF
from Evaluator import eval_genome
from EvaluatorLowPass import eval_genome_lowpass
from CTRNNController import CTRNNController
from DecentralizedController import DecentralizedController
from SyncController import SyncController
from SyncControllerOne import SyncControllerOne
# from individualController import individualController

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
from sideChannelPythonside import SideChannelPythonside
from SineController12DOF import SineController12DOF
from RNNController import RNNController
from Individual import Individual
from configparser import ConfigParser
from reporter import Reporter

import socket
import random


HIGHEST_WORKER_ID = 65535 - UnityEnvironment.BASE_ENVIRONMENT_PORT

class EvolutionaryAlgorithm:
    def __init__(self, config):

        configFile = ConfigParser()
        configFile.read(config)

        filesData = configFile["FILES"]

        self.savefolder = filesData["saveFolder"]

        self.startNumber = 0


        if len(sys.argv) > 4:
            self.savefolder = sys.argv[4]

        self.name = ""
        self.reporter = Reporter(self.savefolder, config, self.name)

        config = self.reporter.getConfig()
        

        legConfig = self.reporter.getLegConfig()
        brainConfig = self.reporter.getBrainConfig()
        brainConfigSync = self.reporter.getBrainConfigSync()

        configFile = ConfigParser()
        configFile.read(config)

        eaData = configFile["EA"]
        filesData = configFile["FILES"]
        
        self.controller = eaData["controller"]

        if len(sys.argv) > 5:
            self.controller = sys.argv[5]

        if self.controller == "SINE":
            self.controller_reference = SineController12DOF
        elif self.controller == "CTRNN":
            self.controller_reference = CTRNNController
        elif self.controller == "DEC":
            self.controller_reference = DecentralizedController
        elif self.controller == "RNN":
            self.controller_reference = RNNController
        elif self.controller == "SYNC":
            self.controller_reference = SyncControllerOne
        else:
            print("not a valid controller")
            exit(0)

        

        
        self.gen = int(eaData["generations"])
        self.popNumber = int(eaData["population"])
        self.envNumber = int(eaData["cores"])
        self.steps = int(eaData["steps"])
        self.DP = int(eaData["DP"])
        self.mutateRate = float(eaData["mutateRate"])
        self.mutatePower = float(eaData["mutatePower"])
        self.savingInterval = int(eaData["savingInterval"])
        self.deltaTime = float(eaData["deltaTime"])
        self.advanceTime = float(eaData["advanceTime"])
        self.timeStep = float(eaData["timeStep"])
        self.tournsize = int(eaData["tournsize"])


        if len(sys.argv) > 1:
            self.startNumber = int(sys.argv[1])

        if len(sys.argv) > 2:
            self.mutateRate = float(sys.argv[2])
        
        if len(sys.argv) > 3:
            self.mutatePower = float(sys.argv[3])

        if len(sys.argv) > 6:
            self.DP = int(sys.argv[6])
        

        if eaData["changeScene"] == "True":
            self.changeScene = True
        else:
            self.changeScene = False

        self.path = "Builds/"

        if platform.system() == "Windows":
            self.path += "Windows/"
            self.path += filesData["path"]

        else:
            self.path += "Linux/"
            self.path += filesData["path"]
            self.path += "/linux.x86_64"
        

        # if len(sys.argv) > 3:
        #     self.advanceTime = float(sys.argv[3])

        # if len(sys.argv) > 4:
        #     self.timeStep = float(sys.argv[4])

        # if len(sys.argv) > 5:
        #     self.savingInterval = int(sys.argv[5])
        #     self.gen = self.savingInterval * 5

        
        self._updateConfig(config)
        self._setCTRNNMutation(config, self.mutateRate, self.mutatePower, True)
        if eaData["controller"] == "Decentralized":
            self._setCTRNNMutation(legConfig, self.mutateRate, self.mutatePower)
            self._setCTRNNMutation(brainConfig, self.mutateRate, self.mutatePower)
        
        if eaData["controller"] == "sync":
            self._setCTRNNMutation(legConfig, self.mutateRate, self.mutatePower)
            self._setCTRNNMutation(brainConfigSync, self.mutateRate, self.mutatePower)


        stringList = eaData["robotList"]
        self.robots = []

        for i in stringList:
            self.robots.append(int(i))

        self.robotIndex = 0
        self.robotNumber = self.robots[self.robotIndex]

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", Individual, self.controller_reference, config = config, delta = self.deltaTime)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", eval_genome)
        self.toolbox.register("mutate", Individual.mutate, mutate_rate=self.mutateRate, sigma = self.mutatePower)
        self.toolbox.register("select", tools.selTournament, tournsize=self.tournsize)



        self._makeEnv(self.envNumber)
        self.pop = self.toolbox.population(n=self.popNumber)
        self.elite = self.pop[0]


        

        self.run()

    def _updateConfig(self, config):
        configFile = ConfigParser()
        configFile.read(config)

        configFile.set("EA", "generations", str(self.gen))
        configFile.set("EA", "savinginterval", str(self.savingInterval))
        configFile.set("FILES", "savefolder", self.savefolder)
        configFile.set("EA", "advanceTime", str(self.advanceTime))
        configFile.set("EA", "timeStep", str(self.timeStep))
        configFile.set("EA", "controller", str(self.controller))
        configFile.set("EA", "dp", str(self.DP))

        with open(config, "w") as f:
            configFile.write(f)


    def _setCTRNNMutation(self, config, mutationRate, mutationPower, main = False):
        configFile = ConfigParser()
        configFile.read(config)

        remove = str(mutationRate)
        mutationRate = str(mutationRate)
        mutationPower = str(mutationPower)

        if main:
            configFile.set("EA", "mutaterate", mutationRate)
            configFile.set("EA", "mutatepower", mutationPower)

        configFile.set("DefaultGenome", "bias_mutate_rate", mutationRate)
        configFile.set("DefaultGenome", "bias_mutate_power", mutationPower)

        configFile.set("DefaultGenome", "weight_mutate_rate", mutationRate)
        configFile.set("DefaultGenome", "weight_mutate_power", mutationPower)

        configFile.set("DefaultGenome", "response_mutate_rate", mutationRate)
        configFile.set("DefaultGenome", "response_mutate_power", mutationPower)

        configFile.set("DefaultGenome", "node_add_prob", mutationRate)
        configFile.set("DefaultGenome", "node_delete_prob", remove)

        configFile.set("DefaultGenome", "conn_add_prob", mutationRate)
        configFile.set("DefaultGenome", "conn_delete_prob", remove)

        with open(config, "w") as f:
            configFile.write(f)

    def step(self, gen):

        offspring = self.toolbox.select(self.pop, self.popNumber - 1)
        offspring = list(map(self.toolbox.clone, offspring))


        for mutant in offspring:
            self.toolbox.mutate(mutant)
            
        self.pop = offspring
        self.pop.append(self.elite)


        threads = []

        for ind in self.pop:
            thread = threading.Thread(target=self.toolbox.evaluate, args=(ind, self.evalQueue, self.steps, self.advanceTime, self.timeStep, self.robotNumber, self.DP))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

        fits = [ind.fitness for ind in self.pop]
        self.pop.sort(key=lambda x:x.fitness)
        self.elite = tools.selBest(self.pop, k = 1)[0]
        fits.sort(reverse=True)


        if ((gen + 1) % self.savingInterval == 0):
            self.reporter.saveElite(self.elite, gen)
            if(self.changeScene):
                self.robotIndex += 1
                if self.robotIndex == len(self.robots):
                    self.robotIndex = len(self.robots) - 1
                self.robotNumber = self.robots[self.robotIndex]

        if (gen == (self.gen - 1)): #Always save the best
            self.reporter.saveElite(self.elite, gen)

        self.reporter.saveStats(fits)

    def _makeEnv(self, nEnvs):
        j = 0
        self.evalQueue = queue.Queue()
        print("---Making environments---")
        for i in tqdm(range(nEnvs)):
            sideChannel = SideChannelPythonside()
            while not (self.is_worker_id_open(self.startNumber + j)):
                j += 1
                if j > 1000:
                    break
            env = UnityEnvironment(file_name=self.path, worker_id=self.startNumber + j, seed = 4, side_channels=[sideChannel], no_graphics=True)
            env.reset()
            for j in range(5):
                env.step()
            env.reset()
            env_list = [env, sideChannel]
            self.evalQueue.put(env_list)
    
    def end(self):
        print("---Closing environments---")
        for i in tqdm(range(self.envNumber)):
            env = self.evalQueue.get()
            env = env[0]
            env.close()
        
    def run(self):
        print("---Starting evolution---")
        for g in tqdm(range(self.gen)):
            self.step(g)
        self.end()
        # self.reporter.plot()
    
    
    
    def is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def is_worker_id_open(self, worker_id: int) -> bool:
        return not self.is_port_in_use(
            UnityEnvironment.BASE_ENVIRONMENT_PORT + worker_id
        )

    def get_worker_id(self) -> int:
        pid = random.randrange(HIGHEST_WORKER_ID)
        while not self.is_worker_id_open(pid):
            print("Not open!")
            pid = random.randrange(HIGHEST_WORKER_ID)
        return pid
        
            




                        
if __name__ == "__main__":

    ea = EvolutionaryAlgorithm("configs/config.ini")
